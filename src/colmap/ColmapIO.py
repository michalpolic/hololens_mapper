import sys
import os
import numpy as np
from numpy import linalg
from src.utils.UtilsMath import UtilsMath

class ColmapIO:
    _project_path = ''
    _cameras = {}
    _images = {}
    _points = {}

    def __init__(self):
       pass 

    def load_model(self, project_path):
        print('Reading colmap model.')
        os.system(f"colmap model_converter --input_path {project_path} --output_path {project_path} --output_type TXT")
        if not project_path[-1] == '/':
            project_path = project_path + '/'
        self._project_path = project_path

        self._cameras = self.load_colmap_camera(project_path + "cameras.txt")
        self._images = self.load_colmap_images(project_path + "images.txt")
        self._points = self.load_colmap_points(project_path + "points3D.txt")
        return (self._cameras, self._images, self._points)

    # load camera params
    def load_colmap_camera(self, colmap_cams_file):
        camera_dict = {}
        file_reader = open(colmap_cams_file, 'r')
        data_lines = file_reader.read().split("\n")
        for line in data_lines:
            if line[0] == "#":
                continue
            else:
                p = line.split(" ")
                camera_dict['camera_id'] = int(p[0])
                camera_dict['width'] = int(p[2])
                camera_dict['height'] = int(p[3])
                camera_dict['f'] = float(p[4])
                camera_dict['pp'] = [float(p[5]), float(p[6])]
                camera_dict['rd'] = [float(p[7]), float(p[8])]
                break
        return camera_dict

    # load images params
    def load_colmap_images(self, colmap_imgs_file):
        utils_math = UtilsMath()
        images_list = []
        file_reader = open(colmap_imgs_file, 'r')
        data_lines = file_reader.read().split("\n")
        first_row = True
        for line in data_lines:
            if len(line) == 0:
                break
            if line[0] == "#":
                continue

            p = line.split(" ")
            if first_row:
                R = utils_math.q2r([float(p[1]), float(p[2]), float(p[3]), float(p[4])])
                C = - np.matrix(R).T * np.matrix([float(p[5]), float(p[6]), float(p[7])]).T
                img = {
                    'image_id': int(p[0]),
                    'camera_id': p[8],
                    'R': R,
                    'C': C,
                    'name': p[9],
                    'uvs': [],
                    'point3D_ids': []
                }
                first_row = False
            else:
                for ii in range(int(len(p) / 3)):
                    img['uvs'].append(p[3 * ii])
                    img['uvs'].append(p[3 * ii + 1])
                    img['point3D_ids'].append(p[3 * ii + 2])
                images_list.append(img)
                first_row = True
        return images_list

    # load points 3D
    def load_colmap_points(self, colmap_points_file):
        points_list = []
        file_reader = open(colmap_points_file, 'r')
        data_lines = file_reader.read().split("\n")
        for line in data_lines:
            if len(line) == 0:
                break
            if line[0] == "#":
                continue

            p = line.split(" ")
            pt = {
                'point3D_id': int(p[0]),
                'X': [float(p[1]), float(p[2]), float(p[3])],
                'rgb': [int(p[4]), int(p[5]), int(p[6])],
                'err': float(p[7]),
                'img_pt': []
            }
            for ii in range(int((len(p) - 8) / 2)):
                pt['img_pt'].append(p[8 + 2 * ii])
                pt['img_pt'].append(p[8 + 2 * ii + 1])
            points_list.append(pt)
        return points_list

    def getImage(self, images, image_id):
        for img in images:
            if img['image_id'] == image_id:
                return img
        return None