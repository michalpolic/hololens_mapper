import sys
import os
import numpy as np
from numpy import True_, linalg
import sqlite3
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
                continue
            if line[0] == "#":
                continue

            p = line.split(" ")
            if first_row:
                if float(p[1]) == 1 and float(p[2]) == 0 and float(p[3]) == 0 and float(p[4]) == 0 \
                    and float(p[5]) == 0 and float(p[6]) == 0 and float(p[7]) == 0:
                    continue
                R = utils_math.q2r([float(p[1]), float(p[2]), float(p[3]), float(p[4])])
                C = - np.matrix(R).T * np.matrix([float(p[5]), float(p[6]), float(p[7])]).T
                img = {
                    'image_id': int(p[0]),
                    'camera_id': p[8],
                    'R': R,
                    'C': C,
                    'name': p[9].replace('\\','/').replace('\/','/'),
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
                
        images_dict = {}
        for img in images_list:
            images_dict[int(img['image_id'])] = img

        return images_dict
        
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

        if isinstance(cameras,dict):
            cameras = list(cameras.values())

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
            mean_observations = sum((len(img['point3D_ids']) for img in images.values()))/len(images)

        images_file = open(images_file_path, "w")
        images_file.write( \
            "# Image list with two lines of data per image:\n" + \
            "# IMAGE_ID, QW, QX, QY, QZ, TX, TY, TZ, CAMERA_ID, NAME\n" + \
            "# POINTS2D[] as (X, Y, POINT3D_ID)\n" + \
            f"# Number of images: {len(images)}, mean observations per image: {mean_observations}\n")
        
        utils_math = UtilsMath()
        for img in images.values():
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
        # images may have any ids
        order_to_image_id = {}  
        i = 0
        for image in images.values(): 
            order_to_image_id[i] = image['image_id']
            i += 1
        
        list_image_pairs = []
        img_pair_ids = np.where(view_graph>min_common_pts)
        for i in range(np.shape(img_pair_ids)[1]):
            image1_id = order_to_image_id[img_pair_ids[0][i]]
            image2_id = order_to_image_id[img_pair_ids[1][i]]
            list_image_pairs.append(f"{images[image1_id]['name']} {images[image2_id]['name']}\n") 

        out_file = open(out_file_path, "w")
        out_file.write("".join(list_image_pairs))
        out_file.close()

    def camera_model_to_db(self, cam):
        known_camera_model = False
        if cam['model'] == 'PINHOLE':
            known_camera_model = True
            model_id = 1
            params = bytearray(np.array([cam['f'][0], cam['f'][1], cam['pp'][0], cam['pp'][1]], dtype=np.float64))
            prior_focal = (cam['f'][0] + cam['f'][1]) / 2

        if cam['model'] == 'RADIAL':
            known_camera_model = True
            model_id = 3
            params = bytearray(np.array([cam['f'], cam['pp'][0], cam['pp'][1], cam['rd'][0], cam['rd'][1]], dtype=np.float64))
            prior_focal = cam['f']

        assert known_camera_model, 'Unknown camera model.'
        return (model_id, params, prior_focal)

    def write_model_into_database(self, data_dir, database_path, cameras, images, matches):
        self.insert_cameras_into_database(data_dir + database_path, cameras)
        self.insert_images_into_database(data_dir + database_path, images)
        self.insert_keypoints_into_database(data_dir + database_path, images)
        self.insert_matches_into_database(data_dir + database_path, matches)
        self.insert_inliers_into_database(data_dir + database_path, matches)

    def insert_cameras_into_database(self, physical_database_path, cameras):
        con = sqlite3.connect(physical_database_path)
        cursor = con.cursor()
        sqlite_insert = """INSERT INTO cameras (camera_id, model, width, height, params, prior_focal_length) VALUES (?, ?, ?, ?, ?, ?)"""
        for cam_id in cameras:
            cam = cameras[cam_id]
            cam_model_id, params, prior_focal = self.camera_model_to_db(cam)
            data_tuple = (cam_id, cam_model_id, cam['width'], cam['height'], params, prior_focal)
            cursor.execute(sqlite_insert, data_tuple)
        con.commit()
        con.close()

    def insert_images_into_database(self, physical_database_path, images):
        con = sqlite3.connect(physical_database_path)
        cursor = con.cursor()
        sqlite_insert = """INSERT INTO images (image_id, name, camera_id, prior_qw, prior_qx, prior_qy, prior_qz, prior_tx, prior_ty, prior_tz) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""         
        utils_math = UtilsMath()
        for img in images.values():
            q = np.ndarray.tolist(utils_math.r2q(img['R']).reshape(-1))[0]
            t = np.ndarray.tolist((- img['R'] * img['C']).reshape(-1))[0]
            data_tuple = (img['image_id'], img['name'].replace('\\','/'), int(img['camera_id']), \
                q[0], q[1], q[2], q[3], t[0], t[1], t[2])
            cursor.execute(sqlite_insert, data_tuple)
        con.commit()
        con.close()

    def insert_keypoints_into_database(self, physical_database_path, images):
        con = sqlite3.connect(physical_database_path)
        cursor = con.cursor()
        sqlite_insert = """INSERT INTO keypoints (image_id, rows, cols, data) VALUES (?, ?, ?, ?)"""
        for img in images.values():
            n = int(len(img['uvs'])/2)
            uvs = np.array(img['uvs']).reshape(-1,2)
            data = np.concatenate((uvs, np.zeros((n,2))), axis=1).astype(np.float32).tobytes(order='C')
            data_tuple = (img['image_id'], n, 4, data)
            cursor.execute(sqlite_insert, data_tuple)
        con.commit()
        con.close()

    def pair_id_to_image_ids(self, pair_id):
        image_id2 = pair_id % 2147483647
        image_id1 = int((pair_id - image_id2) / 2147483647)
        return image_id1, image_id2

    def insert_matches_into_database(self, physical_database_path, matches):
        con = sqlite3.connect(physical_database_path)
        cursor = con.cursor()
        sqlite_insert = """INSERT INTO matches (pair_id, rows, cols, data) VALUES (?, ?, ?, ?)"""
        for pair_id in matches:
            img1_id, img2_id = self.pair_id_to_image_ids(pair_id)
            corresp_ids = np.array([matches[pair_id]["obs_ids1"], matches[pair_id]["obs_ids2"]]).T.astype(dtype='uint32')
            if img1_id > img2_id:
                corresp_ids = corresp_ids[:, [1, 0]]
            data = corresp_ids.tobytes(order='C')
            n = np.shape(matches[pair_id]["obs_ids1"])[0]
            data_tuple = (pair_id, n, 2, data)
            cursor.execute(sqlite_insert, data_tuple)
        con.commit()
        con.close()

    def insert_inliers_into_database(self, physical_database_path, matches):
        con = sqlite3.connect(physical_database_path)
        cursor = con.cursor()
        sqlite_insert = """INSERT INTO two_view_geometries (pair_id, rows, cols, data, config, F, E) VALUES (?, ?, ?, ?, ?, ?, ?)"""
        for pair_id in matches:
            img1_id, img2_id = self.pair_id_to_image_ids(pair_id)
            inliers_filter = matches[pair_id]["inliers"]
            obs_ids1 = matches[pair_id]["obs_ids1"][inliers_filter]
            obs_ids2 = matches[pair_id]["obs_ids2"][inliers_filter]
            corresp_ids = np.array([obs_ids1, obs_ids2], dtype='uint32').T
            if img1_id > img2_id:
                corresp_ids = corresp_ids[:, [1, 0]]
            data = corresp_ids.tobytes(order='C')
            F_data = matches[pair_id]["F"].astype(dtype='float64').tobytes(order='C')
            E_data = matches[pair_id]["E"].astype(dtype='float64').tobytes(order='C')
            n = int(np.sum(inliers_filter))
            data_tuple = (pair_id, n, 2, data, 2, F_data, E_data)
            cursor.execute(sqlite_insert, data_tuple)
        con.commit()
        con.close()

    def load_images_from_database(self, physical_database_path):
        con = sqlite3.connect(physical_database_path)
        cursor = con.cursor()
        cursor.execute("SELECT image_id, name FROM images")
        row = cursor.fetchall()
        con.close()

        images_db = []
        for item in row:
            images_db.append({'image_id': item[0], 'name': item[1]})

        return images_db

    def points3D_to_xyz(self, points3D):
        xyz = np.zeros((3,len(points3D)), dtype=float)
        rgb = np.zeros((3,len(points3D)), dtype=float)
        xyz_colored = []
        rgb_colored = []
        for i, pt in enumerate(points3D):
            xyz[0,i] = pt['X'][0]
            xyz[1,i] = pt['X'][1]
            xyz[2,i] = pt['X'][2]
            rgb[0,i] = float(pt['rgb'][0]) / 255.0
            rgb[1,i] = float(pt['rgb'][1]) / 255.0
            rgb[2,i] = float(pt['rgb'][2]) / 255.0
            if pt['rgb'][0] != pt['rgb'][1] or pt['rgb'][1] != pt['rgb'][2]:
                xyz_colored.append(pt['X'][0])
                xyz_colored.append(pt['X'][1])
                xyz_colored.append(pt['X'][2])
                rgb_colored.append(float(pt['rgb'][0]) / 255.0)
                rgb_colored.append(float(pt['rgb'][1]) / 255.0)
                rgb_colored.append(float(pt['rgb'][2]) / 255.0)
        return (xyz, rgb, np.reshape(np.array(xyz_colored),(3,-1),order='F'), np.reshape(np.array(rgb_colored),(3,-1),order='F'))