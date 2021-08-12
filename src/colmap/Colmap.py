import os
from ctypes import *
import numpy as np
import sqlite3
from src.utils.UtilsSingularity import UtilsSingularity
from src.utils.UtilsMath import UtilsMath

class Colmap():

    _colmap_sif = None
    _utils_math = None

    def __init__(self, colmap_sif):
        """Init colmap object to run predefined commands"""
        self._colmap_sif = colmap_sif
        self._utils_math = UtilsMath()

    def extract_features(self, database_path, image_path):
        self._colmap_sif.command_dict("colmap feature_extractor", 
            {"database_path": database_path, 
            "image_path": image_path,
            "ImageReader.camera_model": "RADIAL",
            "ImageReader.single_camera": 1
            })

    def exhaustive_matcher(self, database_path):
        self._colmap_sif.command_dict("colmap exhaustive_matcher", 
            {"database_path": database_path})

    def mapper(self, database_path, image_path, output_path):
        self._colmap_sif.command_dict("colmap mapper", 
            {"database_path": database_path, 
            "image_path": image_path,
            "output_path": output_path,
            "Mapper.min_model_size": 5
            })

    def prepare_database(self, data_dir, database_path):
        if os.path.exists(data_dir + database_path):
            os.remove(data_dir + database_path)
        self._colmap_sif.command_dict("colmap database_creator", {"database_path": database_path})

    def insert_pv_camera_into_database(self, con):   # use predefined parameters
        cursor = con.cursor()
        sqlite_insert = """INSERT INTO cameras (camera_id, model, width, height, params, prior_focal_length) VALUES (?, ?, ?, ?, ?, ?)"""
        params = bytearray(np.array([(1038.135254 + 1036.468140)/2, 664.387146, 396.142090, 0.182501, -0.161466], dtype=np.float64))
        data_tuple = (0, 3, 1344, 756, params, (1038.135254 + 1036.468140)/2)
        cursor.execute(sqlite_insert, data_tuple)
        con.commit()

    def insert_pv_images_into_database(self, con, holo_cameras, obs_for_images):    # use hololens tracking parameters
        cursor = con.cursor()
        sqlite_insert = """INSERT INTO images (image_id, name, camera_id, prior_qw, prior_qx, prior_qy, prior_qz, prior_tx, prior_ty, prior_tz) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""         
        for img_name in obs_for_images:
            img = holo_cameras[img_name]
            q = self._utils_math.r2q(img["R"])
            t = img["t"].tolist()
            data_tuple = (img["id"], str(img["file_path"].replace("\\","/")), 0, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan)   #, q[0,0], q[1,0], q[2,0], q[3,0], t[0][0], t[1][0], t[2][0]
            cursor.execute(sqlite_insert, data_tuple)
        con.commit()

    def insert_pv_keypoints_into_database(self, con, holo_cameras, obs_for_images):
        cursor = con.cursor()
        sqlite_insert = """INSERT INTO keypoints (image_id, rows, cols, data) VALUES (?, ?, ?, ?)"""
        for img_name in obs_for_images:
            img = holo_cameras[img_name]
            img_data = obs_for_images[img_name]
            n = np.shape(img_data)[0]
            data = np.concatenate((img_data, np.zeros((n,2))), axis=1).astype(np.float32).tobytes(order='C')
            data_tuple = (img["id"], n, 4, data)
            cursor.execute(sqlite_insert, data_tuple)
        con.commit()

    def img_ids_to_pair_id(self, img1_id, img2_id):
        if img1_id > img2_id:
            pair_id = 2147483647 * img2_id + img1_id
        else:
            pair_id = 2147483647 * img1_id + img2_id
        return pair_id
   
    def insert_pv_matches_into_database(self, con, patch2pix_matches, holo_cameras):
        cursor = con.cursor()
        sqlite_insert = """INSERT INTO matches (pair_id, rows, cols, data) VALUES (?, ?, ?, ?)"""
        for pair_name in patch2pix_matches:
            imgs_names = pair_name.split("-")
            img1_id = holo_cameras[imgs_names[0]]["id"]
            img2_id = holo_cameras[imgs_names[1]]["id"]
            pair_id = self.img_ids_to_pair_id(img1_id, img2_id)
            corresp_ids = np.array([patch2pix_matches[pair_name]["obs_ids1"], patch2pix_matches[pair_name]["obs_ids2"]]).T
            # corresp_ids = corresp_ids[patch2pix_matches[pair_name]["inliers"],::]
            data = corresp_ids.astype(dtype='uint32').tobytes(order='C')
            n = np.shape(patch2pix_matches[pair_name]["obs_ids1"])[0]
            cursor.execute(sqlite_insert, (pair_id, n, 2, data))
        con.commit()
        

    def insert_pv_inliers_into_database(self, con, patch2pix_matches, holo_cameras):
        cursor = con.cursor()
        sqlite_insert = """INSERT INTO two_view_geometries (pair_id, rows, cols, data, config, F, E) VALUES (?, ?, ?, ?, ?, ?, ?)"""
        for pair_name in patch2pix_matches:
            if pair_name == "00132595722640683874-00132595722638019500":
                aa = 1

            imgs_names = pair_name.split("-")
            img1_id = holo_cameras[imgs_names[0]]["id"]
            img2_id = holo_cameras[imgs_names[1]]["id"]
            pair_id = self.img_ids_to_pair_id(img1_id, img2_id)
            inliers_filter = patch2pix_matches[pair_name]["inliers"]
            obs_ids1 = patch2pix_matches[pair_name]["obs_ids1"][inliers_filter]
            obs_ids2 = patch2pix_matches[pair_name]["obs_ids2"][inliers_filter]
            
            data = np.array([obs_ids1, obs_ids2], dtype='uint32').T.tobytes(order='C')
            F_data = patch2pix_matches[pair_name]["F"].astype(dtype='float64').tobytes(order='C')
            E_data = patch2pix_matches[pair_name]["E"].astype(dtype='float64').tobytes(order='C')
            n = np.sum(inliers_filter)
            data_tuple = (pair_id, n, 2, data, 2, F_data, E_data)
            cursor.execute(sqlite_insert, data_tuple)
            con.commit()
        

    def save_matches_into_database(self, data_dir, database_path, holo_cameras, patch2pix_matches, obs_for_images):
        self.prepare_database(data_dir, database_path)
        con = sqlite3.connect(data_dir + database_path)
        self.insert_pv_camera_into_database(con)
        self.insert_pv_images_into_database(con, holo_cameras, obs_for_images)
        self.insert_pv_keypoints_into_database(con, holo_cameras, obs_for_images)
        self.insert_pv_matches_into_database(con, patch2pix_matches, holo_cameras)
        self.insert_pv_inliers_into_database(con, patch2pix_matches, holo_cameras)
        con.close()