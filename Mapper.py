# 1) read dense pointcloud in world coordinates from HoloLens depthmaps 
# 2) run COLMAP to find "correct" camera poses
# 3) load COLMAP & load HoloLens camera poses
# 4) transform colmap cameras to HoloLens coordinate system
# 5) save SfM results to Meshroom SfM JSON file
# 6) run Meshroom: undistortion, depthmap estimation, depth filtering, meshing with output dense pointcloud
# 7) load MVS dense pointcloud
# 8) compose common dense pointcloud
# 9) filter out noise
# 10) calculate the visibility of dense points and save Meshroom SfM JSON file
# 11) run Meshroom: meshing and texturing

import sys
import os
from pathlib import Path
import numpy as np
import json
import pickle
import logging
from src.holo.HoloIO import HoloIO
from src.colmap.ColmapIO import ColmapIO
from src.colmap.Colmap import Colmap
from src.meshroom.MeshroomIO import MeshroomIO
from src.meshroom.Meshroom import Meshroom
from src.utils.UtilsMath import UtilsMath
from src.utils.UtilsContainers import UtilsContainers
from src.utils.UtilsKeyframes import UtilsKeyframes
from src.utils.UtilsMatcher import UtilsMatcher
from third_party.patch2pix.utils.common.plotting import plot_matches

class Mapper():

    def __init__(self, data_dir):
        """Init mapper directory with datasets"""
        self._data_dir = data_dir

    def save_obj(self, obj, file_path):
        with open(file_path, 'wb+') as f:
            pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

    def load_obj(self, file_path):
        with open(file_path, 'rb') as f:
            return pickle.load(f)

    def run(self, recoring_dir, uvdata_path, out_dir):
        logger = logging.getLogger('mapper')
        logging.basicConfig(level=logging.INFO)

        # init the communication layer with Singularity images
        alicevision_sif = UtilsContainers("singularity", os.path.dirname(__file__) + "/alicevision.sif", self._data_dir, "/opt/AliceVision_install/bin/")
        colmap_sif = UtilsContainers("singularity", os.path.dirname(__file__) + "/colmap.sif", self._data_dir)

        # init the Meshroom and Colmap objects
        meshroom = Meshroom(alicevision_sif)
        colmap = Colmap(colmap_sif)

        # init paths
        recoring_dir_abs = self._data_dir + recoring_dir
        uvdata_path_abs = self._data_dir + uvdata_path
        out_dir_abs = self._data_dir + out_dir
        out_cache_dir_abs = out_dir_abs + "/MeshroomCache"
 
        # # 1) read dense pointcloud in world coordinates from HoloLens depthmaps 
        holo_io = HoloIO()
        holo_cameras = holo_io.read_hololens_csv(recoring_dir_abs + "/pv.csv")
        holo_xyz = holo_io.read_dense_pointcloud(recoring_dir_abs + "/long_throw_depth", uvdata_path_abs, recoring_dir_abs + "/long_throw_depth.csv", logger=logger) 
        # holo_io.write_pointcloud_to_file(holo_xyz, out_dir_abs + "/desk.obj")

        # 1b) keyframe selection
        keyframe_selector = UtilsKeyframes()
        keyframe_selector.copy_pv_keyframes(recoring_dir_abs + "/pv", out_dir_abs + "/pv", 23, 8, logger=logger)

        # 2) run COLMAP to find "correct" camera poses
        Path(out_dir_abs + "/colmap/sparse").mkdir(parents=True, exist_ok=True)
        matcher = UtilsMatcher("SIFT", colmap)         # patch2pix / SuperGlue / SIFT
        if matcher._matcher_name == "SIFT":
            colmap.extract_features(out_dir + "/colmap/database.db", out_dir + "/pv")     # COLMAP feature extractor
            colmap.exhaustive_matcher(out_dir + "/colmap/database.db")                    # COLMAP matcher
        obs_for_images, matches = matcher.holo_matcher(out_dir_abs + "/pv", holo_cameras, database_path=out_dir_abs + "/colmap/database.db")    
        colmap.save_matches_into_database(self._data_dir, out_dir + "/colmap/database.db", holo_cameras, matches, obs_for_images)
        colmap.mapper(out_dir + "/colmap/database.db", out_dir + "/pv", out_dir + "/colmap/sparse")

        # # 3) load COLMAP & load HoloLens camera poses
        colmap_io = ColmapIO()
        colmap_cameras, colmap_images, colmap_points = colmap_io.load_model(out_dir_abs + "/colmap/sparse/0")

        # # 4) estimate transformation of colmap cameras to HoloLens coordinate system
        utils_math = UtilsMath()
        colmap_to_holo_transform = utils_math.estimate_colmap_to_holo_transformation(colmap_images, holo_cameras)
        colmap_images = utils_math.transform_colmap_images(colmap_images, colmap_to_holo_transform)
        colmap_points = utils_math.transform_colmap_points(colmap_points, colmap_to_holo_transform)

        # # 5) save SfM results to Meshroom SfM JSON file
        meshroom_io = MeshroomIO()
        meshroom_io.save_colmap_to_json(out_dir_abs + "/sfm.json", out_dir + "/pv/", colmap_cameras, colmap_images, colmap_points)

        # # 6) run Meshroom: undistortion, depthmap estimation, depth filtering, meshing with output dense pointcloud, convert resluts to obj
        out_cache_dir = out_dir + "/MeshroomCache"
        sfm_abc_path = out_dir + "/MeshroomCache/ConvertSfMFormat/test/sfm.abc"
        meshroom.convert_sfm(out_dir + "/sfm.json", sfm_abc_path)
        meshroom.undistort_imgs(sfm_abc_path, out_cache_dir + "/PrepareDenseScene/test")
        meshroom.estimate_depthmaps(sfm_abc_path,  out_cache_dir + "/DepthMap/test", out_cache_dir + "/PrepareDenseScene/test")
        meshroom.filter_depthmaps(sfm_abc_path, out_cache_dir + "/DepthMapFilter/test", out_cache_dir + "/DepthMap/test")
        meshroom.meshing(sfm_abc_path, out_cache_dir + "/Meshing/test/densePointCloud.abc", out_cache_dir + "/Meshing/test/mesh.obj", out_cache_dir + "/DepthMap/test")
        meshroom.convert_sfm(out_cache_dir + "/Meshing/test/densePointCloud_raw.abc", out_cache_dir + "/ConvertSfMFormat/test/mvs_raw.ply")
       
        # # 7) load MVS dense pointcloud
        mvs_xyz = meshroom_io.load_ply_vertices(out_cache_dir_abs + "/ConvertSfMFormat/test/mvs_raw.ply")

        # 8) compose common dense pointcloud
        common_xyz = np.concatenate((holo_xyz, mvs_xyz), axis=1)
        holo_io.write_pointcloud_to_file(common_xyz, out_dir_abs + "/common_pointcloud.obj")

        # # 9) filter out noise
        # common_xyz = meshroom_io.load_obj_vertices(out_dir_abs + "/common_pointcloud.obj")  # just for testing
        common_xyz_fitered = utils_math.filter_dense_pointcloud_noise_KDtree(common_xyz, 0.05, 35)
        holo_io.write_pointcloud_to_file(common_xyz_fitered, out_dir_abs + "/common_pointcloud_filtered.obj")

        # 10) calculate the visibility of dense points and save Meshroom SfM JSON file
        # common_xyz_fitered = meshroom_io.load_obj_vertices(out_dir_abs + "/common_pointcloud_filtered.obj")  # just for testing
        visibility_map = utils_math.estimate_visibility(colmap_cameras, colmap_images, common_xyz_fitered)
        meshroom_io.save_merged_mvs_to_json(out_dir_abs + "/holo_and_mvs.json", out_dir + "/pv/", colmap_cameras, colmap_images, common_xyz_fitered, visibility_map)

        # 11) run Meshroom: meshing and texturing
        meshroom.convert_sfm(out_dir + "/holo_and_mvs.json", out_cache_dir + "/ConvertSfMFormat/test_merged/sfm.abc")
        meshroom.undistort_imgs(out_cache_dir + "/ConvertSfMFormat/test_merged/sfm.abc", out_cache_dir + "/PrepareDenseScene/test_merged")

        # new solution - new data
        meshroom.meshing2(out_cache_dir + "/ConvertSfMFormat/test_merged/sfm.abc", out_cache_dir + "/Meshing/test_merged/densePointCloud.abc", out_cache_dir + "/Meshing/test_merged/mesh.obj")
        meshroom.convert_sfm(out_cache_dir + "/Meshing/test_merged/densePointCloud_raw.abc", out_cache_dir + "/ConvertSfMFormat/test_merged/mvs_raw.ply")

        meshroom.texturing(out_cache_dir + "/Meshing/test_merged/densePointCloud.abc", out_cache_dir + "/PrepareDenseScene/test_merged", out_cache_dir + "/Meshing/test_merged/mesh.obj", out_cache_dir + "/Texturing/test_merged")