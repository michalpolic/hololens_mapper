import sys
import math
import os
from pathlib import Path
import re
import multiprocessing as mp
from distutils.dir_util import copy_tree
from plyfile import PlyData, PlyElement

import numpy as np
from src.holo.HoloIO import HoloIO

class HoloIO2:

    def __init__(self):
        pass

    def read_csv(self, file_path, skip_n_lines = 1):
        """ Read csv file with camera poses.
        Input: 
            file_path - path to camera info file 
        Output: 
            camerainfo - dictionary camerainfo['name'] -> {array of camera parameters} 
        """
        assert os.path.isfile(file_path), f"the csv file {file_path} does not exist"

        try:
            skipped = ''
            csvfile = open(file_path, 'r')
            for i in range(skip_n_lines):
                skipped += csvfile.readline()
            csvdata = csvfile.read()
            parsedcsvdata = csvdata.split("\n")
            parsedcsvdata = [x for x in parsedcsvdata if x]
            camerainfo = {}
            for csvline in parsedcsvdata:
                splitted = csvline.split(",")
                camerainfo[splitted[0]] = csvline
        except:
            assert False, "failed parsing the csv camera information file"
        finally:
            csvfile.close()

        return (camerainfo,skipped)


    def write_csv(self, skipped, csv_dict, file_path):
        """ Write csv file to disk.
        Input: 
            csv_dict - the dictionary with csv row to be saved
            file_path - path to file where to write csv records
        """
        if not csv_dict:
            return

        try:
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            csvfile = open(file_path, 'w')
            csvfile.write(skipped)

            imgs_order = np.sort(np.array(list(map(int, csv_dict.keys()))))
            list_of_rows = []
            for img_id in imgs_order:
                list_of_rows.append(f"{csv_dict[str(img_id)]}\n")
            csvfile.write(''.join(list_of_rows))

        except:
            assert False, "failed writing the csv file"
        finally:
            csvfile.close()


    def compose_common_pointcloud(self, pointclouds_dir, logger=None):
        """Read and concatenate the pointcloud in Long Throw Depth folder.
        Input: 
            pointclouds_dir - path to pointclouds directory
        Output: 
            xyz - single common pointcloud
        """
        if not pointclouds_dir[-1] == '/':
            pointclouds_dir = pointclouds_dir + '/'

        xyz = []
        for r, d, f in os.walk(pointclouds_dir):
            for filename in f:
                if ".ply" in filename:
                    if logger:
                        logger.info(f'Loading: {filename}')

                    plydata = PlyData.read(pointclouds_dir + filename)
                    for pt in plydata['vertex'].data:
                        xyz.append(pt[0])
                        xyz.append(pt[1])
                        xyz.append(pt[2])

        return np.array(xyz,dtype=float).reshape((3,-1),order='F') 


    def get_pv_rig2world(self, data):
        return np.matrix(data[3:20]).astype(float).reshape((4, 4))


    def get_vlc_rig2world(self, data):
        return np.matrix(data[1:]).astype(float).reshape((4, 4))


    def get_hololens_images(self, rig2world, rig2cam, recording_dir, 
        imgs_dir, imgs_ext, camera_id = 0, image_id = 0, pv = False):
        """Create hololens images dict. with parameters from parsed csv
        Input: 
            rig2world - transformation from device coordinates to world coordinate system
            rig2cam - the camera pose w.r.t. device coordinates
            camera_id - related camera id for all the views 
            image_id - starting id of the view, used if more cameras loaded
        Output: 
            images - the Colmap structure with images parameters
        """
        images = []
        img_timestamps = list(map(int, [f[0:-4] for f in os.listdir(recording_dir + imgs_dir)]))
        for txt_params in rig2world.values():
            data = list(map(float, txt_params.split(",")))
            rig2world = self.get_pv_rig2world(data) if pv else self.get_vlc_rig2world(data)  
            world2cam = rig2cam * np.linalg.inv(rig2world)
            R = world2cam[0:3,0:3]
            t = world2cam[0:3,3]
            C = - R.T * t
            Rx = np.matrix([[1,0,0],[0,-1,0],[0,0,-1]]) if pv else np.eye(3)

            timestamp_id = np.argmin(np.abs(np.array(img_timestamps) - int(data[0])))
            images.append({
                'image_id': int(image_id),
                'camera_id': int(camera_id),
                'R': Rx * R,
                'C': C,
                'name': imgs_dir + '/' + str(img_timestamps[timestamp_id]) + '.' + imgs_ext,
                'uvs': [],
                'point3D_ids': []
            })
            image_id += 1
        return images


    def get_hololens_points3D(self):
        """Create hololens points3D (empty dictionary)
        Output: 
            points_list - empty dict
        """
        points3D = []
        return points3D


    def get_tracking_files_for_shortcuts(self, recording_dir, tracking_file):
        rig2world = ''
        extrinsics = ''
        images_dir = ''
        images_ext = ''
        if tracking_file == 'pv':
            images_ext = 'png'
            pv_files = [f for f in os.listdir(recording_dir) if len(f)>7 and f[-7:]=='_pv.txt']
            assert len(pv_files) > 0, 'Failed to find the tracking info for PV camera in recording dir.'
            rig2world = recording_dir + pv_files[0]
        else:
            if len(tracking_file) == 0 or tracking_file not in ['vlc_ll','vlc_lf','vlc_rf','vlc_rr']:
                assert False, 'Missing vlc camera abreviation in tracking files.'
            images_ext = 'pgm'
            if tracking_file == 'vlc_ll':
                images_dir = 'VLC LL'
            if tracking_file == 'vlc_lf':
                images_dir = 'VLC LF'
            if tracking_file == 'vlc_rf':
                images_dir = 'VLC RF'
            if tracking_file == 'vlc_rr':
                images_dir = 'VLC RR'
            rig2world = recording_dir + images_dir + '_rig2world.txt'
            extrinsics = recording_dir + images_dir + '_extrinsics.txt'
        return (rig2world, extrinsics, tracking_file, images_ext)


    def load_model(self, recording_dir, intrinsics):
        """Transform cameras parameters from tracking files into standard model structures
        Input: 
            recording_dir - path hololens recording folder
            intrinsics - information about cameras assumed in the model
        Output: 
            cameras - the Colmap structure with camera info
            images - the Colmap structure with images info
            points3D - the Colmap structure with points in 3D
        """
        if not recording_dir[-1] == '/':
            recording_dir = recording_dir + '/'

        cameras = []
        images = []
        holo_io = HoloIO()
        for camera_params in intrinsics:
            rig2world_file, extrinsics_file, imgs_dir, imgs_ext = \
                self.get_tracking_files_for_shortcuts(recording_dir, camera_params["trackingFile"])
            
            if os.path.exists(rig2world_file):
                # add camera to cameras
                cameras.append(holo_io.get_hololens_camera_from_intrinsics(camera_params))

                # add images to images
                rig2world, _ = self.read_csv(rig2world_file, (1 if len(extrinsics_file) == 0 else 0))
                extrinsics = np.eye(4)
                if len(extrinsics_file) > 0 and Path(extrinsics_file).exists():
                    extrinsics = np.loadtxt(extrinsics_file, delimiter=',').reshape(4,4)
                images.extend(self.get_hololens_images(rig2world, extrinsics, recording_dir, imgs_dir, 
                    imgs_ext, camera_id = camera_params["intrinsicId"], image_id = len(images), 
                    pv = (True if len(extrinsics_file) == 0 else False)))

        images_dict = {}
        for img in images:
            images_dict[img['image_id']] = img
        images = images_dict
        points3D = self.get_hololens_points3D()
        return (cameras, images, points3D)