import os
import sys
from ctypes import *
import numpy as np
import sqlite3
import re
import random
from src.utils.UtilsContainers import UtilsContainers
from src.utils.UtilsMath import UtilsMath

class Colmap():

    _colmap_container = None
    _utils_math = None

    def __init__(self, colmap_container = None):
        """Init colmap object to run predefined commands"""
        self._colmap_container = colmap_container
        self._utils_math = UtilsMath()

    def extract_features(self, database_path, image_path):
        self._colmap_container.command_dict("colmap feature_extractor", 
            {"database_path": database_path, 
            "image_path": image_path,
            "ImageReader.camera_model": "RADIAL",
            "ImageReader.single_camera_per_folder": 1
            })

    def exhaustive_matcher(self, database_path):
        self._colmap_container.command_dict("colmap exhaustive_matcher", 
            {"database_path": database_path})

    def custom_matching(self, database_path, match_list_path):
        self._colmap_container.command_dict("colmap matches_importer", 
            {"database_path": database_path,
            "match_list_path": match_list_path})

    def mapper(self, database_path, image_path, output_path):
        self._colmap_container.command_dict("colmap mapper", 
            {"database_path": database_path, 
            "image_path": image_path,
            "output_path": output_path,
            "Mapper.min_model_size": 5,
            "Mapper.ba_global_images_ratio": 1.2, 
            "Mapper.ba_global_points_ratio": 1.2, 
            "Mapper.ba_global_max_num_iterations": 20,
            "Mapper.ba_global_max_refinements": 3,
            "Mapper.ba_global_points_freq": 200000
            })

    def images_undistortion(self, image_path, input_path, output_path):
        self._colmap_container.command_dict("colmap image_undistorter", 
            {"image_path": image_path,
            "input_path": input_path,
            "output_path": output_path,
            "output_type": "COLMAP",
            "max_image_size": 2048
            })

    def model_converter(self, in_path, out_path, out_type):
        self._colmap_container.command_dict("colmap model_converter", 
            {"input_path": in_path, 
            "output_path": out_path,
            "output_type": out_type
            })

    def prepare_database(self, physical_database_path, container_database_path):
        if os.path.exists(physical_database_path):
            os.remove(physical_database_path)
        self._colmap_container.command_dict("colmap database_creator", {"database_path": container_database_path})

    def insert_pv_camera_into_database(self, database_path):   # use predefined parameters
        con = sqlite3.connect(database_path)
        cursor = con.cursor()
        sqlite_insert = """INSERT INTO cameras (camera_id, model, width, height, params, prior_focal_length) VALUES (?, ?, ?, ?, ?, ?)"""
        params = bytearray(np.array([(1038.135254 + 1036.468140)/2, 664.387146, 396.142090, 0.182501, -0.161466], dtype=np.float64))
        data_tuple = (0, 3, 1344, 756, params, (1038.135254 + 1036.468140)/2)
        cursor.execute(sqlite_insert, data_tuple)
        con.commit()
        con.close()

    def insert_pv_images_into_database(self, database_path, holo_cameras, obs_for_images):    # use hololens tracking parameters
        con = sqlite3.connect(database_path)
        cursor = con.cursor()
        sqlite_insert = """INSERT INTO images (image_id, name, camera_id, prior_qw, prior_qx, prior_qy, prior_qz, prior_tx, prior_ty, prior_tz) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""         
        for img_name in obs_for_images:
            img = holo_cameras[img_name]
            q = self._utils_math.r2q(img["R"])
            t = img["t"].tolist()
            data_tuple = (img["id"], str(img["file_path"].replace("pv\\","")), 0, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan)   #, q[0,0], q[1,0], q[2,0], q[3,0], t[0][0], t[1][0], t[2][0]
            cursor.execute(sqlite_insert, data_tuple)
        con.commit()
        con.close()

    def insert_pv_keypoints_into_database(self, database_path, holo_cameras, obs_for_images):
        con = sqlite3.connect(database_path)
        cursor = con.cursor()
        sqlite_insert = """INSERT INTO keypoints (image_id, rows, cols, data) VALUES (?, ?, ?, ?)"""
        for img_name in obs_for_images:
            img_id = holo_cameras[img_name]["id"]
            img_data = obs_for_images[img_name]
            n = int(np.shape(img_data)[0])
            data = np.concatenate((img_data, np.zeros((n,2))), axis=1).astype(np.float32).tobytes(order='C')
            data_tuple = (img_id, n, 4, data)
            cursor.execute(sqlite_insert, data_tuple)
        con.commit()
        con.close()

    def img_ids_to_pair_id(self, img1_id, img2_id):
        if img1_id > img2_id:
            pair_id = 2147483647 * img2_id + img1_id
        else:
            pair_id = 2147483647 * img1_id + img2_id
        return pair_id
   
    def insert_pv_matches_into_database(self, database_path, patch2pix_matches, holo_cameras, obs_for_images):
        con = sqlite3.connect(database_path)
        cursor = con.cursor()
        sqlite_insert = """INSERT INTO matches (pair_id, rows, cols, data) VALUES (?, ?, ?, ?)"""
        for pair_name in patch2pix_matches:
            imgs_names = pair_name.split("-")
            img1_id = holo_cameras[imgs_names[0]]["id"]
            img2_id = holo_cameras[imgs_names[1]]["id"]
            pair_id = self.img_ids_to_pair_id(img1_id, img2_id)
            corresp_ids = np.array([patch2pix_matches[pair_name]["obs_ids1"], patch2pix_matches[pair_name]["obs_ids2"]]).T.astype(dtype='uint32')
            if img1_id > img2_id:
                corresp_ids = corresp_ids[:, [1, 0]]
            data = corresp_ids.tobytes(order='C')
            n = np.shape(patch2pix_matches[pair_name]["obs_ids1"])[0]
            data_tuple = (pair_id, n, 2, data)
            cursor.execute(sqlite_insert, data_tuple)
        con.commit()
        con.close()

    def insert_pv_inliers_into_database(self, database_path, patch2pix_matches, holo_cameras):
        con = sqlite3.connect(database_path)
        cursor = con.cursor()
        sqlite_insert = """INSERT INTO two_view_geometries (pair_id, rows, cols, data, config, F, E) VALUES (?, ?, ?, ?, ?, ?, ?)"""
        for pair_name in patch2pix_matches:
            imgs_names = pair_name.split("-")
            img1_id = holo_cameras[imgs_names[0]]["id"]
            img2_id = holo_cameras[imgs_names[1]]["id"]
            pair_id = self.img_ids_to_pair_id(img1_id, img2_id)
            inliers_filter = patch2pix_matches[pair_name]["inliers"]
            obs_ids1 = patch2pix_matches[pair_name]["obs_ids1"][inliers_filter]
            obs_ids2 = patch2pix_matches[pair_name]["obs_ids2"][inliers_filter]
            corresp_ids = np.array([obs_ids1, obs_ids2], dtype='uint32').T
            if img1_id > img2_id:
                corresp_ids = corresp_ids[:, [1, 0]]
            data = corresp_ids.tobytes(order='C')
            F_data = patch2pix_matches[pair_name]["F"].astype(dtype='float64').tobytes(order='C')
            E_data = patch2pix_matches[pair_name]["E"].astype(dtype='float64').tobytes(order='C')
            n = int(np.sum(inliers_filter))
            data_tuple = (pair_id, n, 2, data, 2, F_data, E_data)
            cursor.execute(sqlite_insert, data_tuple)
        con.commit()
        con.close()
    
    def get_image_id_for_name(self, database_path, img_name):
        con = sqlite3.connect(database_path)
        cursor = con.cursor()
        cursor.execute("SELECT image_id FROM images WHERE name=?", (img_name,))
        row = cursor.fetchall()
        con.close()
        return row[0][0]
    
    def load_matches_for_pair_of_images(self, database_path, img1_id, img2_id):
        con = sqlite3.connect(database_path)
        cursor = con.cursor()
        cursor.execute("SELECT pair_id, rows, cols, data FROM matches WHERE pair_id=?", (self.img_ids_to_pair_id(img1_id, img2_id),))
        row = cursor.fetchall()
        if row[0][3] == None:
            return np.array([])
        corresp_ids = np.fromstring(row[0][3], dtype="uint32").reshape(row[0][1],row[0][2])
        if img1_id > img2_id:
            corresp_ids = corresp_ids[:, [1, 0]]

        cursor.execute("SELECT image_id, rows, cols, data FROM keypoints WHERE image_id=?", (img1_id,))
        row = cursor.fetchall()
        keypoints1 = np.fromstring(row[0][3], dtype="float32").reshape(row[0][1],row[0][2])

        cursor.execute("SELECT image_id, rows, cols, data FROM keypoints WHERE image_id=?", (img2_id,))
        row = cursor.fetchall()
        keypoints2 = np.fromstring(row[0][3], dtype="float32").reshape(row[0][1],row[0][2])
        con.close()

        return np.concatenate((keypoints1[corresp_ids[:,0],0:2], keypoints2[corresp_ids[:,1],0:2]), axis=1)

    def load_matches_from_db(self, database_path, img1_name, img2_name):
        assert database_path != "", "The database_path in load_matches_from_db is not specified."
        img1_id = self.get_image_id_for_name(database_path, img1_name)
        img2_id = self.get_image_id_for_name(database_path, img2_name)
        return self.load_matches_for_pair_of_images(database_path, img1_id, img2_id)
        

    def compose_images_and_points3D_from_visibilty(self, images, visibility_map, new_xyz):
        # find which points are seen from more than 2 viewpoints
        used_points3D = np.zeros(np.shape(new_xyz)[1])
        for i in range(0,len(visibility_map),4):
            used_points3D[int(visibility_map[i])] += 1
        valid_points3D = used_points3D > 1

        # remove old observations
        for img_id in images:
            img = images[img_id]
            img['uvs'] = []
            img['point3D_ids'] = []

        points3D = []
        ids_xyz_to_points3D = -np.ones(np.shape(new_xyz)[1], dtype=int)
        for i in range(0,len(visibility_map),4):
            if valid_points3D[int(visibility_map[i])]:
                
                # add point if not exist
                if ids_xyz_to_points3D[int(visibility_map[i])] == -1:
                    xyz = new_xyz[::,int(visibility_map[i])]
                    ids_xyz_to_points3D[int(visibility_map[i])] = len(points3D)
                    pt = {
                        'point3D_id': len(points3D),
                        'X': [xyz[0], xyz[1], xyz[2]],
                        'rgb': [0, 0, 0],
                        'err': 1,
                        'img_pt': []
                    }
                    points3D.append(pt)
                
                # update observations of the point and image 
                pt = points3D[ids_xyz_to_points3D[int(visibility_map[i])]]
                image = images[int(visibility_map[i+1])] 
                pt['img_pt'].append(image['image_id'])
                pt['img_pt'].append(len(image['point3D_ids'])) 
                image['uvs'].append(visibility_map[i+2])
                image['uvs'].append(visibility_map[i+3])
                image['point3D_ids'].append(pt['point3D_id'])
                points3D[ids_xyz_to_points3D[int(visibility_map[i])]] = pt
                images[int(visibility_map[i+1])] = image

        return (images, points3D)

    def select_subset_of_points3D(self, num_of_points3D, num_of_observations, images, points3D):
        num_of_unsucessful_trials = 0
        remove_point = [False for i in range(len(points3D))]
        num_of_removed_points = 0

        # save num. of obs for each image
        min_observations_for_img = {}
        num_obs_in_img = {}
        obs_to_remove = {}
        for img_id in images:
            k = len(images[img_id]['point3D_ids'])
            num_obs_in_img[img_id] = k
            min_observations_for_img[img_id] = min(k,num_of_observations)
            obs_to_remove[img_id] = [False for j in range(k)]

        # simulation -> select what can be removed
        while (len(points3D) - num_of_removed_points) > num_of_points3D or num_of_unsucessful_trials > 1000:

            pt_position = random.randint(0, len(points3D)-1)
            if remove_point[pt_position]:
                continue
            pt = points3D[pt_position]

            num_obs_in_img2 = num_obs_in_img.copy()
            for i in range(0, len(pt['img_pt']), 2):
                num_obs_in_img2[int(pt['img_pt'][i])] -= 1

            remain_enough_observations = True
            for img_id in images:
                if num_obs_in_img2[img_id] < min_observations_for_img[img_id]:
                    remain_enough_observations = False
            if remain_enough_observations:
                num_of_removed_points += 1
                num_of_unsucessful_trials = 0
                remove_point[pt_position] = True
                num_obs_in_img = num_obs_in_img2
                for i in range(0, len(pt['img_pt']), 2):
                    obs_to_remove[int(pt['img_pt'][i])][int(pt['img_pt'][i+1])] = True
            else:
                num_of_unsucessful_trials += 1

        # remove points and observations 
        new_points3D = []
        new_points3D_ids_map = {}
        for i in range(len(points3D)):
            if not remove_point[i]:
                pt = points3D[i]
                new_points3D_ids_map[i] = len(new_points3D)
                pt['point3D_id'] = len(new_points3D)
                new_points3D.append(pt)

        for img_id in images:
            img = images[img_id]
            point3D_ids = img['point3D_ids']
            uvs = img['uvs']
            new_point3D_ids = []
            new_uvs = []
            for j in range(len(point3D_ids)):
                if not obs_to_remove[img_id][j] and int(point3D_ids[j]) > -1:
                    new_point3D_ids.append(new_points3D_ids_map[int(point3D_ids[j])])
                    new_uvs.append(uvs[2*j])
                    new_uvs.append(uvs[2*j+1])
            img['point3D_ids'] = new_point3D_ids
            img['uvs'] = new_uvs

        return images, new_points3D


    def remove_observations_of_removed_images_in_points3D(self, filtered_images, points3D):
        for pt in points3D:
            img_pt = pt['img_pt']
            new_img_pt = []
            for i in range(0,len(img_pt),2):
                if not (int(img_pt[i]) in filtered_images):
                    new_img_pt.append(img_pt[i])
                    new_img_pt.append(img_pt[i+1])
            pt['img_pt'] = new_img_pt
        return points3D


    def remove_points_with_less_than_two_oservations(self, images, points3D):
        new_points3D = []
        new_points3D_ids_map = {}
        for i in range(len(points3D)):
            pt = points3D[i]
            if (len(pt['img_pt']) / 2) >= 2:
                new_points3D_ids_map[int(pt['point3D_id'])] = len(new_points3D)
                pt['point3D_id'] = len(new_points3D)
                new_points3D.append(pt) 
            else: 
                new_points3D_ids_map[int(pt['point3D_id'])] = -1
        
        for img_id in images:
            img = images[img_id]
            point3D_ids = img['point3D_ids']
            for j in range(len(point3D_ids)):
                if int(point3D_ids[j]) > -1:
                    new_pt_id = new_points3D_ids_map[int(point3D_ids[j])]
                    if new_pt_id > -1:
                        point3D_ids[j] = str(new_pt_id)
                    else:
                        point3D_ids[j] = '-1'
        return (images, new_points3D)

    def remove_images_with_less_than_three_points3D(self, images):
        filtered_images = {}
        for img_id in images:
            img = images[img_id]
            if len(img['point3D_ids']) < 3:
                filtered_images[img_id] = img
        for img_id in filtered_images:
            images.pop(img_id)

        return (filtered_images, images)


    def remove_images_from_model(self, regular_pattern, images, points3D):
        # filter images with given regular_pattern in name
        new_images = {}
        filtered_images = {}
        for img_id in images:
            img = images[img_id]
            if re.search(regular_pattern, img['name']):
                filtered_images[int(img['image_id'])] = img
            else:
                new_images[int(img['image_id'])] = img
        
        # check the consistency of the remaining model and remove wrong images/points3D
        while filtered_images:
            points3D = self.remove_observations_of_removed_images_in_points3D(filtered_images, points3D)
            images, points3D = self.remove_points_with_less_than_two_oservations(images, points3D)
            filtered_images, new_images = self.remove_images_with_less_than_three_points3D(new_images)

        return (new_images, points3D)
    
    def get_largest_reconstruction_dir(self, parent_dir):
        largest_reconstruction_dir = '0'
        largest_reconstruction_size = -1
        for i in range(100):
            if os.path.isdir(parent_dir + '/' + str(i)):
                if os.path.isfile(parent_dir + '/' + str(i) + '/cameras.bin') and \
                    os.path.isfile(parent_dir + '/' + str(i) + '/images.bin') and \
                    os.path.isfile(parent_dir + '/' + str(i) + '/points3D.bin'):
                    current_reconstruction_size = \
                        os.path.getsize(parent_dir + '/' + str(i) + '/cameras.bin') + \
                        os.path.getsize(parent_dir + '/' + str(i) + '/images.bin') + \
                        os.path.getsize(parent_dir + '/' + str(i) + '/points3D.bin')
                    if current_reconstruction_size > largest_reconstruction_size:
                        largest_reconstruction_size = current_reconstruction_size
                        largest_reconstruction_dir = str(i)
            else:
                return largest_reconstruction_dir

