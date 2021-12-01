import os
import sys
from ctypes import *
import numpy as np
import sqlite3
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
            "ImageReader.single_camera": 1
            })

    def exhaustive_matcher(self, database_path):
        self._colmap_container.command_dict("colmap exhaustive_matcher", 
            {"database_path": database_path})

    def mapper(self, database_path, image_path, output_path):
        self._colmap_container.command_dict("colmap mapper", 
            {"database_path": database_path, 
            "image_path": image_path,
            "output_path": output_path,
            "Mapper.min_model_size": 5
            })

    def prepare_database(self, data_dir, database_path):
        if os.path.exists(data_dir + database_path):
            os.remove(data_dir + database_path)
        self._colmap_container.command_dict("colmap database_creator", {"database_path": "/data" + database_path})

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


    def save_matches_into_database(self, data_dir, database_path, holo_cameras, patch2pix_matches, obs_for_images):
        self.prepare_database(data_dir, database_path)
        self.insert_pv_camera_into_database(data_dir + database_path)
        self.insert_pv_images_into_database(data_dir + database_path, holo_cameras, obs_for_images)
        self.insert_pv_keypoints_into_database(data_dir + database_path, holo_cameras, obs_for_images)
        self.insert_pv_matches_into_database(data_dir + database_path, patch2pix_matches, holo_cameras, obs_for_images)
        self.insert_pv_inliers_into_database(data_dir + database_path, patch2pix_matches, holo_cameras)
    
    def get_image_id_for_name(self, database_path, img_name):
        con = sqlite3.connect(database_path)
        cursor = con.cursor()
        cursor.execute("SELECT image_id FROM images WHERE name=?", (img_name,))
        row = cursor.fetchall()
        con.close()
        return row[0][0]
        

    def load_matches_from_db(self, database_path, img1_name, img2_name):
        assert database_path != "", "The database_path in load_matches_from_db is not specified."
        img1_id = self.get_image_id_for_name(database_path, img1_name)
        img2_id = self.get_image_id_for_name(database_path, img2_name)
        
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

    def compose_images_and_points3D_from_visibilty(self, images, visibility_map, new_xyz):
        # find which points are seen from more than 2 viewpoints
        used_points3D = np.zeros(np.shape(new_xyz)[1])
        for i in range(0,len(visibility_map),4):
            used_points3D[int(visibility_map[i])] += 1
        valid_points3D = used_points3D > 1

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

