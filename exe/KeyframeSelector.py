import os
import sys
import logging
import shutil

# import mapper packages
dir_path = __file__
dir_path = os.path.dirname(dir_path)
sys.path.append(dir_path)
from src.holo.HoloIO import HoloIO
from src.utils.UtilsKeyframes import UtilsKeyframes

# setting 
recordingDir = "/local1/projects/artwin/datasets/Munich/HoloLensRecording__2021_08_02__11_23_59_MUCLab_1"
output = "/local1/projects/artwin/datasets/Munich/HoloLensRecording__2021_08_02__11_23_59_MUCLab_1_keyframes2"
blurThreshold = 23
minFrameOffset = 5

# process
keyframe_selector = UtilsKeyframes()
logger = logging.getLogger('keyframeselector')
logging.basicConfig(level=logging.INFO)


logger.info('Start keyframe selector.')
if not os.path.exists(output):
    os.mkdir(output)

keframe_names = keyframe_selector.copy_pv_keyframes(recordingDir + "/pv", output + "/pv", 
    blurThreshold, minFrameOffset, logger = logger)
    
logger.info('Compose new pv.csv in output directory')
holo_io = HoloIO()
pv_csv = holo_io.read_csv(recordingDir + "/pv.csv")
new_pv_csv = keyframe_selector.filter_pv_csv(keframe_names, pv_csv)
new_pv_csv = keyframe_selector.update_img_names(new_pv_csv,'.ppm','.jpg')
holo_io.write_csv(new_pv_csv, output + "/pv.csv")

logger.info('Keyframe selector is done.')