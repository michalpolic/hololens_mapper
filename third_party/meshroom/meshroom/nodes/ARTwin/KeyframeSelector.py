from __future__ import print_function

__version__ = "0.1"

from meshroom.core import desc
import shutil
import glob
import os
import sys

# import mapper packages
dir_path = __file__
for i in range(6):
    dir_path = os.path.dirname(dir_path)
sys.path.append(dir_path)
from src.holo.HoloIO import HoloIO
from src.utils.UtilsKeyframes import UtilsKeyframes

class KeyframeSelector(desc.Node):

    category = 'ARTwin'
    documentation = '''
This node select subset of images (keyframes) and copy them to output path. 
'''

    inputs = [
        desc.File(
            name="recordingDir",
            label="Recording Folder",
            description="HoloLens recording directory (images in pv/*.jpg, " \
                "depth in long_throw_depth/*.pgm, etc. + related .csv).",
            value="",
            uid=[0],
        ),
        desc.FloatParam(
            name='pvBlurThreshold',
            label='PV: Blur Threshold',
            description="The threshold for minimal laplacian variation in the image.",
            value=25.0,
            range=(1.0, 1000.0, 1.0),
            uid=[0],
            ),
        desc.IntParam(
            name='pvMinFrameOffset',
            label='PV: Min. Frames Offset',
            description='The minimal number of skipped frames from PV image sequence.',
            value=13,
            range=(0, 100, 1),
            uid=[0],
            ),            
        desc.IntParam(
            name='vlcMinFrameOffset',
            label='VLC: Min. Frames Offset',
            description='The minimal number of skipped frames from tracking image sequence.',
            value=30,
            range=(0, 600, 1),
            uid=[0],
            ),  
        desc.ChoiceParam(
            name='verboseLevel',
            label='Verbose Level',
            description='''verbosity level (critical, error, warning, info, debug).''',
            value='info',
            values=['critical', 'error', 'warning', 'info', 'debug'],
            exclusive=True,
            uid=[],
            ),
        ]

    outputs = [
        desc.File(
            name="output",
            label="Output Folder",
            description="",
            value=desc.Node.internalFolder,
            uid=[],
            ),
    ]

    def processChunk(self, chunk):
        try:
            chunk.logManager.start(chunk.node.verboseLevel.value)
            
            if not chunk.node.recordingDir:
                chunk.logger.warning('Nothing to process')
                return
            if not chunk.node.output.value:
                return

             
            # setting
            tracking_csvs = ["/pv.csv", "/vlc_lf.csv", "/vlc_ll.csv", "/vlc_rf.csv", "/vlc_rr.csv"]
            orig_images_extensions = ["ppm", "pgm", "pgm", "pgm", "pgm"]
            new_images_extensions = ["jpg", "jpg", "jpg", "jpg", "jpg"]
            blur_thresholds = [chunk.node.pvBlurThreshold.value, -1, -1, -1, -1]
            pv_offset = chunk.node.pvMinFrameOffset.value
            vlc_offset = chunk.node.vlcMinFrameOffset.value
            min_frame_offsets = [pv_offset, vlc_offset, vlc_offset, vlc_offset, vlc_offset]

            input_images_folders = [chunk.node.recordingDir.value + "/pv", \
                chunk.node.recordingDir.value + "/vlc_lf", chunk.node.recordingDir.value + "/vlc_ll", \
                chunk.node.recordingDir.value + "/vlc_rf", chunk.node.recordingDir.value + "/vlc_rr"]
            output_images_folders = [chunk.node.output.value + "/pv", \
                chunk.node.output.value + "/vlc_lf", chunk.node.output.value + "/vlc_ll", \
                chunk.node.output.value + "/vlc_rf", chunk.node.output.value + "/vlc_rr"]    


            # process
            holo_io = HoloIO()
            keyframe_selector = UtilsKeyframes()
            if not os.path.exists(chunk.node.output.value):
                os.mkdir(chunk.node.output.value)

            chunk.logger.info('Select and copy keyframes.')    
            keyframe_names = keyframe_selector.copy_keyframes(
                input_images_folders,
                output_images_folders, 
                blur_thresholds,
                min_frame_offsets, 
                new_images_extensions,
                logger = chunk.logger)

            chunk.logger.info('Compose new csv files')
            for i in range(len(tracking_csvs)):
                csv_data = holo_io.read_csv(chunk.node.recordingDir.value + tracking_csvs[i])
                new_csv_data = keyframe_selector.filter_pv_csv(keyframe_names[i], csv_data)
                new_csv_data = keyframe_selector.update_img_names(new_csv_data, \
                    orig_images_extensions[i], new_images_extensions[i])
                holo_io.write_csv(new_csv_data, chunk.node.output.value + tracking_csvs[i])

            chunk.logger.info('Copy depthmaps and long_throw_depth.csv')
            shutil.copytree(chunk.node.recordingDir.value + "/long_throw_depth", chunk.node.output.value + "/long_throw_depth") 
            shutil.copy(chunk.node.recordingDir.value + "/long_throw_depth.csv", chunk.node.output.value + "/long_throw_depth.csv") 

            chunk.logger.info('Keyframe selector is done.') 

        except AssertionError as err:
            chunk.logger.error("Error in keyframe selector: " + err)
        finally:
            chunk.logManager.end()
