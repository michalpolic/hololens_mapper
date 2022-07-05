import sys
import logging
from pathlib import Path

# import mapper packages
root = Path(__file__).resolve().parent.parent
sys.path.append(str(root))
from src.holo.HoloIO import HoloIO
from src.utils.UtilsMath import UtilsMath
from src.meshroom.MeshroomIO import MeshroomIO

# setting 
densePointcloud = "/local/artwin/data/Munich/2021_09_22__merge_dense_pointclouds/model_merged.ply"   
neighbourDistance = 0.05
minNeighbours = 50
output = "/local/artwin/data/Munich/2021_09_22__merge_dense_pointclouds/model_merged_filtered2.obj"


# init
holo_io = HoloIO()
meshroom_io = MeshroomIO()
utils_math = UtilsMath()
logger = logging.getLogger('poitcloudfilter')
logging.basicConfig(level=logging.INFO)


logger.info('Loading dense pointcloud.')
is_pointcloud_loaded = False 
if densePointcloud[-4::] == ".obj":
    xyz, rgb = meshroom_io.load_obj_vertices(densePointcloud) 
    is_pointcloud_loaded = True
if densePointcloud[-4::] == ".ply":
    xyz, rgb = meshroom_io.load_ply_vertices(densePointcloud) 
    is_pointcloud_loaded = True

assert is_pointcloud_loaded, 'Failed to load dense pointcloud.'


logger.info('Filtering dnese pointcloud.')
xyz_fitered, rgb_filterd = utils_math.filter_dense_pointcloud_noise_KDtree(xyz, \
    neighbourDistance, minNeighbours, rgb = rgb)


logger.info('Saving filtered pointcloud.')
holo_io.write_pointcloud_to_file(xyz_fitered, output, rgb = rgb_filterd)
logger.info('Dense poincloud filtering is done.') 