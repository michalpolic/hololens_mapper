import os
import sys
import logging
import numpy as np

# import mapper packages
dir_path = __file__
dir_path = os.path.dirname(dir_path)
sys.path.append(dir_path)
from src.holo.HoloIO import HoloIO
from src.utils.UtilsMath import UtilsMath
from src.meshroom.MeshroomIO import MeshroomIO
from src.colmap.ColmapIO import ColmapIO
from src.utils.UtilsContainers import UtilsContainers
from src.meshroom.Meshroom import Meshroom

# setting 
workingDir = "/local/artwin/data"
recordingDir = "/local/artwin/data/Munich/HoloLensRecording__2021_08_02__11_23_59_MUCLab_1_keyframes"
inputPointcloud = "/local/artwin/data/Munich/2021_09_22__merge_dense_pointclouds/model_merged_filtered2.obj"
# inputPointcloud = "/local/artwin/data/Munich/2021_09_22__merge_dense_pointclouds/model0.ply"
output = "/local/artwin/data/Munich/HoloLensRecording__2021_08_02__11_23_59_MUCLab_1_keyframes"


# init
holo_io = HoloIO()
meshroom_io = MeshroomIO()
utils_math = UtilsMath()
logger = logging.getLogger('poitcloudfilter')
logging.basicConfig(level=logging.INFO)


# logger.info('Loading HoloLens model.')
# holo_cameras, holo_images, holo_points3D = holo_io.load_model(recordingDir + "/pv.csv")

# logger.info('Loading dense pointcloud.')
# # xyz, rgb = meshroom_io.load_obj_vertices(inputPointcloud)  
# xyz, rgb = meshroom_io.load_ply_vertices(inputPointcloud)  

# logger.info('Estimating visibility.')
# visibility_map = utils_math.estimate_visibility(holo_cameras, holo_images, xyz)

# # test 
# np.save(output+"/visibility_map.npy", np.array(visibility_map))
# np.save(output+"/xyz.npy", xyz)
# np.save(output+"/rgb.npy", rgb)

# visibility_map = np.load(output+"/visibility_map.npy")
# xyz = np.load(output+"/xyz.npy")
# rgb = np.load(output+"/rgb.npy")

# logger.info('Saving the results to Meshroom JSON.')
# meshroom_io.save_merged_mvs_to_json(output + "/mvs.json", \
#     recordingDir.replace(workingDir,'') + "/pv/", holo_cameras, holo_images, xyz, visibility_map, rgb)

logger.info('Convert Meshroom JSON into .abc file.')
alicevision_sif = UtilsContainers("singularity", \
    "/local/artwin/mapping/codes/hololens_mapper/alicevision.sif", \
    workingDir, "/opt/AliceVision_install/bin/")    
meshroom = Meshroom(alicevision_sif)
meshroom.convert_sfm(recordingDir.replace(workingDir,'/data') + "/mvs.json", recordingDir.replace(workingDir,'/data') + "/mvs.abc")

logger.info('All work done.')