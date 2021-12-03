import sys
import os
import numpy as np
from numpy import True_, linalg
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

        # TODO: use container and run this command only if needed
        # os.system(f"colmap model_converter --input_path {project_path} --output_path {project_path} --output_type TXT") # TODO: use docker instead
        if not project_path[-1] == '/':
            project_path = project_path + '/'
        self._project_path = project_path

        self._cameras = self.load_cameras(project_path + "cameras.txt")
        self._images = self.load_images(project_path + "images.txt")
        self._points = self.load_points(project_path + "points3D.txt")
        return (self._cameras, self._images, self._points)

    # load camera params
    def load_cameras(self, colmap_cams_file):
        camera_dict = {}
        file_reader = open(colmap_cams_file, 'r')
        data_lines = file_reader.read().split("\n")
        for line in data_lines:
            if len(line) == 0 or line[0] == "#":
                continue
            else:
                p = line.split(" ")
                camera = {}
                camera['camera_id'] = int(p[0])
                camera['model'] = p[1]
                camera['width'] = int(p[2])
                camera['height'] = int(p[3])
                
                known_camera_model = False
                if camera['model'] == "PINHOLE":
                    known_camera_model = True
                    camera['f'] = [float(p[4]), float(p[5])]
                    camera['pp'] = [float(p[6]), float(p[7])]
                    camera['rd'] = []

                if camera['model'] == "RADIAL":
                    known_camera_model = True
                    camera['f'] = float(p[4])
                    camera['pp'] = [float(p[5]), float(p[6])]
                    camera['rd'] = [float(p[7]), float(p[8])]

                assert known_camera_model, "Unsuported camera model"                
                camera_dict[camera['camera_id']] = camera
                
        return camera_dict

    # load images params
    def load_images(self, colmap_imgs_file):
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
    def load_points(self, colmap_points_file):
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


    def write_model(self, project_path, cameras, images, points3D):
        print('Write COLMAP model.')
        if not project_path[-1] == '/':
            project_path = project_path + '/' 
        self.write_cameras(project_path + "cameras.txt", cameras)
        self.write_images(project_path + "images.txt", images)
        self.write_points3D(project_path + "points3D.txt", points3D)


    def write_cameras(self, cameras_file_path, cameras):
        cameras_file = open(cameras_file_path, "w")
        cameras_file.write( \
            "# Camera list with one line of data per camera:\n" + \
            "# CAMERA_ID, MODEL, WIDTH, HEIGHT, PARAMS[]\n" + \
            "# Number of cameras: {}\n".format(len(cameras)))

        for cam in cameras:
            params = [cam['camera_id'], cam['model'], cam['width'], cam['height']]
            if isinstance(cam['f'], list):
                params.extend(cam['f'])
            else:
                params.append(cam['f'])
            params.extend(cam['pp'])    

            known_camera_model = False
            if cam['model'] == "PINHOLE":
                known_camera_model = True
            if cam['model'] == "RADIAL":
                known_camera_model = True
                params.extend(cam['rd'])
            assert known_camera_model, "Unsuported camera model"
            line = " ".join(map(str, params))
            cameras_file.write(line + "\n")


    def write_images(self, images_file_path, images):
        mean_observations = 0
        if len(images) >= 0:
            mean_observations = sum((len(img['point3D_ids']) for img in images))/len(images)

        images_file = open(images_file_path, "w")
        images_file.write( \
            "# Image list with two lines of data per image:\n" + \
            "# IMAGE_ID, QW, QX, QY, QZ, TX, TY, TZ, CAMERA_ID, NAME\n" + \
            "# POINTS2D[] as (X, Y, POINT3D_ID)\n" + \
            f"# Number of images: {len(images)}, mean observations per image: {mean_observations}\n")
        
        utils_math = UtilsMath()
        for img in images:
            params = [img["image_id"]]
            R = img["R"]
            params.extend(np.reshape(utils_math.r2q(R),-1).tolist()[0])
            params.extend(np.reshape(-R*img["C"],-1).tolist()[0])
            params.append(img["camera_id"])    
            params.append(img["name"])
            line = " ".join(map(str, params))
            images_file.write(line + "\n")

            observations = []
            for i in range(len(img["point3D_ids"])):
                observations.extend([img['uvs'][2*i], img['uvs'][2*i + 1], img['point3D_ids'][i]])
            line = " ".join(map(str, observations))
            images_file.write(line + "\n")


    def write_points3D(self, points3D_file_path, points3D):
        mean_track_length = 0
        if len(points3D) >= 0:
            mean_track_length = sum((len(pt['img_pt'])/2 for pt in points3D))/len(points3D)
        points3D_file = open(points3D_file_path, "w")
        points3D_file.write( \
            "# 3D point list with one line of data per point:\n" + \
            "# POINT3D_ID, X, Y, Z, R, G, B, ERROR, TRACK[] as (IMAGE_ID, POINT2D_IDX)\n" + \
            f"# Number of points: {len(points3D)}, mean track length: {mean_track_length}\n")

        for pt in points3D:
            params = [pt["point3D_id"], *pt["X"], *pt["rgb"], pt["err"], *pt['img_pt']]
            line = " ".join(map(str, params))
            points3D_file.write(line + "\n")

    def save_image_pairs(self, out_file_path, images, view_graph, min_common_pts):
        list_image_pairs = []
        img_pair_ids = np.where(view_graph>min_common_pts)
        for i in range(np.shape(img_pair_ids)[1]):
           list_image_pairs.append(f"{images[img_pair_ids[0][i]]['name']} {images[img_pair_ids[1][i]]['name']}\n") 

        out_file = open(out_file_path, "w")
        out_file.write("".join(list_image_pairs))
        out_file.close()