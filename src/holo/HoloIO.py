import sys
import math
import os
from pathlib import Path

import numpy as np

class HoloIO:

    def __init__(self):
        pass

    def read_uv(self, uvdata_path):
        """ Read the mapping from UV depth to distance from camera center.
        Input: 
            uvdata_path - path to UV data file 
        Output: 
            uvdata - dictionary uvdata['u'+'v'] -> (new u, new v) 
        """
        assert os.path.isfile(uvdata_path), f"the UV depthmap decoding file {uvdata_path} does not exist"

        try:
            uvfile = open(uvdata_path, 'r')
            uvlines = uvfile.read().split("\n")
            uvdata = {}
            for line in uvlines:
                if not "inf, inf" in line:
                    parsed = line.split(" ")
                    uvdata[parsed[1] + parsed[2]] = (float(parsed[4].split(",")[0]), float(parsed[5]))
        except:
            assert(False, "failed parsing the UV data file")
        finally:
            uvfile.close()

        return uvdata


    def read_csv(self, file_path):
        """ Read csv file with camera poses.
        Input: 
            file_path - path to camera info file 
        Output: 
            camerainfo - dictionary camerainfo['name'] -> {array of camera parameters} 
        """
        assert os.path.isfile(file_path), f"the csv file {file_path} does not exist"

        try:
            csvfile = open(file_path, 'r')
            csvheader = csvfile.readline()
            csvdata = csvfile.read()
            parsedcsvdata = csvdata.split("\n")
            parsedcsvdata = [x for x in parsedcsvdata if x]
            camerainfo = {}
            for csvline in parsedcsvdata:
                splitted = csvline.split(",")
                name = splitted[1].split("\\")[-1].split(".")[0]
                camerainfo[name] = csvline

        except:
            assert False, "failed parsing the csv camera information file"
        finally:
            csvfile.close()

        return camerainfo

    def write_csv(self, csv_dict, file_path):
        """ Write csv file to disk.
        Input: 
            csv_dict - the dictionary with csv row to be saved
            file_path - path to file where to write csv records
        """
        assert csv_dict, f"the csv is empty"

        try:
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            csvfile = open(file_path, 'w')
            csvfile.write('Timestamp,ImageFileName,Position.X,Position.Y,Position.Z,' + \
                'Orientation.W,Orientation.X,Orientation.Y,Orientation.Z,FrameToOrigin.m11,' + \
                'FrameToOrigin.m12,FrameToOrigin.m13,FrameToOrigin.m14,FrameToOrigin.m21,' + \
                'FrameToOrigin.m22,FrameToOrigin.m23,FrameToOrigin.m24,FrameToOrigin.m31,' + \
                'FrameToOrigin.m32,FrameToOrigin.m33,FrameToOrigin.m34,FrameToOrigin.m41,' + \
                'FrameToOrigin.m42,FrameToOrigin.m43,FrameToOrigin.m44,CameraViewTransform.m11,' + \
                'CameraViewTransform.m12,CameraViewTransform.m13,CameraViewTransform.m14,' + \
                'CameraViewTransform.m21,CameraViewTransform.m22,CameraViewTransform.m23,' + \
                'CameraViewTransform.m24,CameraViewTransform.m31,CameraViewTransform.m32,' + \
                'CameraViewTransform.m33,CameraViewTransform.m34,CameraViewTransform.m41,' + \
                'CameraViewTransform.m42,CameraViewTransform.m43,CameraViewTransform.m44,' + \
                'CameraProjectionTransform.m11,CameraProjectionTransform.m12,' + \
                'CameraProjectionTransform.m13,CameraProjectionTransform.m14,' + \
                'CameraProjectionTransform.m21,CameraProjectionTransform.m22,' + \
                'CameraProjectionTransform.m23,CameraProjectionTransform.m24,' + \
                'CameraProjectionTransform.m31,CameraProjectionTransform.m32,' + \
                'CameraProjectionTransform.m33,CameraProjectionTransform.m34,' + \
                'CameraProjectionTransform.m41,CameraProjectionTransform.m42,' + \
                'CameraProjectionTransform.m43,CameraProjectionTransform.m44\n')
            list_of_rows = [f"{item}\n" for key, item in csv_dict.items()]
            csvfile.write(''.join(list_of_rows))

        except:
            assert False, "failed writing the csv file"
        finally:
            csvfile.close()




    def parse_poseinfo_to_cameras(self, poseinfo):
        """Rewrite each HoloLens camera parametes to standard format used in Hartley - MVG.
        Input: 
            poseinfo - dictionary camerainfo['name'] -> {array of camera parameters in HoloLens format}
        Output: 
            cameras - dictionary cameras['name'] -> {array of parameters: R, t, C, ...} 
        """
        assert poseinfo, "Pose info is empty."

        try:
            cameras = {}
            view_id = 0
            for k, line in poseinfo.items():
                vals = line.split(",")
                D2C = np.matrix([float(num_str) for num_str in vals[25:41]]).reshape((4, 4)).T
                D2O = np.matrix([float(num_str) for num_str in vals[9:25]]).reshape((4, 4)).T
                O2D = np.linalg.inv(D2O)
                Rt = np.matrix([[-1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]) * D2C * O2D
                R = Rt[0:3, 0:3]
                C = - R.T * Rt[0:3, 3]
                cameras[k] = {
                    "id": view_id,
                    "timestamp": vals[0],
                    "file_path": vals[1].replace(".ppm", ".jpg"),
                    "D2C": D2C,
                    "O2D": O2D,
                    "C2D": np.linalg.inv(D2C),
                    "D2O": D2O,
                    "R": R,
                    "C": C,
                    "t": Rt[0:3, 3],
                    "Rt": Rt
                }
                view_id += 1
        except:
            assert False, "failed rewriting HoloLnes params to standard format"

        return cameras


    def read_depthmap(self, depthmap_path, uvdata):   
        """Read and decode the depthmaps using the UV data.
        Input: 
            depthmap_path - path to depthmap file in .pgm format
            uvdata - dictionary uvdata['u'+'v'] -> (new u, new v) 
        Output: 
            xyz1 - pointcloud in camera coordinate systems 
        """
        assert os.path.isfile(depthmap_path), f"the depthmaps file {depthmap_path} does not exist"
        assert ".pgm" in depthmap_path, f"the depthmaps file {depthmap_path} is in wrong format"
        assert uvdata, "UV data are empty"

        try:
            file = open(depthmap_path, 'rb')
 
            line = file.readline()
            while(not b'65535' in line):
                line = file.readline()

            data = file.read()

            values = np.frombuffer(data, np.short)
            values = np.reshape(values, (450, -1))

            xyz1 = []
            for i in range(0, 450):
                for j in range(0, 448):
                    r = values[i, j]
                    if not r == 0:
                        uv = uvdata["(" + str(j) + "," + str(i) + ")"]
                        d = r / (math.sqrt(uv[0] * uv[0] + uv[1] * uv[1] + 1) * -1000)
                        xyz1.append(d * uv[0])
                        xyz1.append(d * uv[1])
                        xyz1.append(d) 
                        xyz1.append(1)
        except:
            assert False, "failed decoding depthmap file"
        finally:
            file.close()

        return xyz1


    def transform_depthmap_to_world(self, xyz1, poseinfo):
        """Transform the depthmaps into HoloLens world coorinate system.
        Input: 
            xyz1 - one decoded dense pointcloud extended by ones captured by HoloLens ToF camera
            poseinfo - the pose of ToF camera while capturing xyz1 
        Output: 
            wold_xyz - pointcloud in HoloLens world coorinate system
        """
        assert xyz1, "no points to transform"
        assert poseinfo, "no camera parameters available"

        pi = poseinfo.split(",")
        frametoorigin = np.matrix([float(num_str) for num_str in pi[9:25]]).reshape((4, 4))
        cameraviewtransform = np.matrix([float(num_str) for num_str in pi[25:41]]).reshape((4, 4))
        C2W = frametoorigin.T * np.linalg.inv(cameraviewtransform.T)

        return C2W * xyz1


    def read_dense_pointcloud(self, depthmaps_dir, uvdata_path, depthmap_poses_path, logger=None):
        """Read, decode and transform depthmaps into common HoloLens world coordinate system.
        Input: 
            depthmaps_dir - path to depthmaps directory
            uvdata_path - path to UV data decoding file
            depthmap_poses_path - path to CSV file with ToF camera poses  
        Output: 
            wold_xyz - pointcloud in HoloLens world coorinate system
        """
        if not depthmaps_dir[-1] == '/':
            depthmaps_dir = depthmaps_dir + '/'
        
        if logger:
            logger.info(f'Reading uv decoding file: {uvdata_path}')
        uvdata = self.read_uv(uvdata_path)

        if logger:
            logger.info(f'Reading camera poses from file: {depthmap_poses_path}')
        csv = self.read_csv(depthmap_poses_path)

        wold_xyz = np.array([]).reshape(3,0)
        for r, d, f in os.walk(depthmaps_dir):
            for filename in f:
                if ".pgm" in filename:
                    timestamp = filename.split(".")[0]
                    if logger:
                        logger.info(f'Reading depthmap {filename}')
                    xyz1 = self.read_depthmap(depthmaps_dir + filename, uvdata)
                    xyz1 = np.matrix(np.reshape(xyz1, (-1, 4)).T)
                    if logger:
                        logger.info(f'Transforming depthmap {filename} into common coordinate system')
                    xyz1 = np.array(self.transform_depthmap_to_world(xyz1, csv[timestamp]))
                    wold_xyz = np.concatenate((wold_xyz, xyz1[0:3,::]), axis=1)

        return wold_xyz


    def write_pointcloud_to_file(self, xyz, file_path, rgb = None):
        """Write dense pointcloud into file.
        Input: 
            xyz - dense pointcloud
            file_path - path where to save the pointcloud (ext. .obj)
        """
        assert file_path, "file_path is empty"
        assert xyz.any(), "pointcloud to save is empty"

        try:
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            objfile = open(file_path, 'w')
            objfile.write("o Object.1\n")
            if rgb.any():
                list_of_rows = [f"v {xyz[0,i]} {xyz[1,i]} {xyz[2,i]} {rgb[0,i]} {rgb[1,i]} {rgb[2,i]}\n" for i in range(np.shape(xyz)[1])]
            else:
                list_of_rows = [f"v {xyz[0,i]} {xyz[1,i]} {xyz[2,i]}\n" for i in range(np.shape(xyz)[1])]
            objfile.write(''.join(list_of_rows))
        except:
            assert False, "failed writing pointcloud to file"
        finally:
            objfile.close()
            

    def read_cameras(self, csv_file_path):
        """Read cameras parameters from CSV file
        Input: 
            csv_file_path - path where to save the pointcloud (ext. .obj)
        Output: 
            cameras_dict - dictionary with camera parameters cameras_dict[name] = {params}
        """
        csv = self.read_csv(csv_file_path)
        return self.parse_poseinfo_to_cameras(csv)

    def load_model(self, csv_file_path):
        """Transform cameras parameters from CSV file into standard model structures
        Input: 
            csv_file_path - path where to save the pointcloud (ext. .obj)
        Output: 
            cameras - the Colmap structure with camera info
            images - the Colmap structure with images info
            points3D - the Colmap structure with points in 3D
        """
        cameras_dict = self.read_cameras(csv_file_path)
        cameras = self.get_hololens_camera()
        images = self.get_hololens_images(cameras_dict)
        points3D = self.get_hololens_points3D()
        
        return (cameras, images, points3D)


    def get_hololens_camera(self):
        """Create hololens camera with standard parameters
        Output: 
            camera_dict - the Colmap structure with camera info
        """
        camera = {}
        camera['camera_id'] = int(0)
        camera['width'] = int(1344)
        camera['height'] = int(756)
        camera['f'] = float((1038.135254 + 1036.468140) / 2)
        camera['pp'] = [664.387146, 396.142090]
        camera['rd'] = [0., 0.]
        return camera

    def get_hololens_images(self, cameras_dict):
        """Create hololens images dict. with parameters from parsed pv.csv
        Output: 
            images - the Colmap structure with images parameters
        """
        images = []
        image_id = 0
        for image_csv in cameras_dict.items():
            images.append({
                'image_id': int(image_id),
                'camera_id': int(0),
                'R': image_csv[1]['R'],
                'C': image_csv[1]['C'],
                'name': image_csv[1]['file_path'],
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



