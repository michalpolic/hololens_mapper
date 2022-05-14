from __future__ import print_function

__version__ = "0.1"

from meshroom.core import desc
import shutil
import glob
import os
import sys
import numpy as np

# import mapper packages
dir_path = __file__
for i in range(6):
    dir_path = os.path.dirname(dir_path)
sys.path.append(dir_path)
from src.holo.HoloIO import HoloIO
from src.holo.HoloIO2 import HoloIO2
from src.utils.UtilsKeyframes import UtilsKeyframes

class KeyframeSelector(desc.Node):

    category = 'Input Preprocessing'
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
        desc.ChoiceParam(
            name='recordingSource',
            label='Recording source',
            description='The device/algorithm used to create recording folder.',
            value='HoloLens',
            values=['HoloLens', 'HoloLens2', 'COLMAP', 'ORB SLAM', 'BAD SLAM','IOS AR', 'Android AR'],
            exclusive=True,
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

    def get_params_for_hololens_recording(self, chunk):
        params = {}
        params['tracking_files'] = ["/pv.csv", "/vlc_lf.csv", "/vlc_ll.csv", "/vlc_rf.csv", "/vlc_rr.csv"]
        params['orig_images_extensions'] = ["ppm", "pgm", "pgm", "pgm", "pgm"]
        params['new_images_extensions'] = ["jpg", "jpg", "jpg", "jpg", "jpg"]
        params['blur_thresholds'] = [chunk.node.pvBlurThreshold.value, -1, -1, -1, -1]
        pv_offset = chunk.node.pvMinFrameOffset.value
        vlc_offset = chunk.node.vlcMinFrameOffset.value
        params['min_frame_offsets'] = [pv_offset, vlc_offset, vlc_offset, vlc_offset, vlc_offset]

        params['input_images_folders'] = [chunk.node.recordingDir.value + "/pv", \
            chunk.node.recordingDir.value + "/vlc_lf", chunk.node.recordingDir.value + "/vlc_ll", \
            chunk.node.recordingDir.value + "/vlc_rf", chunk.node.recordingDir.value + "/vlc_rr"]
        params['output_images_folders'] = [chunk.node.output.value + "/pv", \
            chunk.node.output.value + "/vlc_lf", chunk.node.output.value + "/vlc_ll", \
            chunk.node.output.value + "/vlc_rf", chunk.node.output.value + "/vlc_rr"]  
        return params


    def get_params_for_hololens2_recording(self, chunk):
        params = {}
        recordingDir = chunk.node.recordingDir.value
        pv_files = [f for f in os.listdir(recordingDir) if len(f)>7 and f[-7:]=='_pv.txt']
        assert len(pv_files) > 0, 'Failed to find the tracking info for PV camera in recording dir.'
        params['tracking_files'] = ["/" + pv_files[0], "/VLC LF_rig2world.txt", "/VLC LL_rig2world.txt", 
            "/VLC RF_rig2world.txt", "/VLC RR_rig2world.txt"]
        params['skip_n_lines'] = [1, 0, 0, 0, 0]
        params['orig_images_extensions'] = ["png", "pgm", "pgm", "pgm", "pgm"]
        params['new_images_extensions'] = ["png", "pgm", "pgm", "pgm", "pgm"]
        params['blur_thresholds'] = [chunk.node.pvBlurThreshold.value, -1, -1, -1, -1]
        pv_offset = chunk.node.pvMinFrameOffset.value
        vlc_offset = chunk.node.vlcMinFrameOffset.value
        params['min_frame_offsets'] = [pv_offset, vlc_offset, vlc_offset, vlc_offset, vlc_offset]

        params['input_images_folders'] = [recordingDir + "/PV", \
            recordingDir + "/VLC LF", recordingDir + "/VLC LL", \
            recordingDir + "/VLC RF", recordingDir + "/VLC RR"]
        params['output_images_folders'] = [chunk.node.output.value + "/pv", \
            chunk.node.output.value + "/vlc_lf", chunk.node.output.value + "/vlc_ll", \
            chunk.node.output.value + "/vlc_rf", chunk.node.output.value + "/vlc_rr"]  
        return params

    def compose_new_hololens_tracking_files(self, chunk, keyframe_selector, keyframe_names, params):
        holo_io = HoloIO()
        for i in range(len(params['tracking_files'])):
            csv_data = holo_io.read_csv(chunk.node.recordingDir.value + params['tracking_files'][i])
            new_csv_data = keyframe_selector.filter_pv_csv(keyframe_names[i], csv_data)
            new_csv_data = keyframe_selector.update_img_names(new_csv_data, \
                params['orig_images_extensions'][i], params['new_images_extensions'][i])
            holo_io.write_csv(new_csv_data, chunk.node.output.value + params['tracking_files'][i])

    def compose_new_hololens2_tracking_files(self, chunk, keyframe_selector, \
        keyframe_names, params, max_time_diff = 100):
        holo_io2 = HoloIO2()
        for i in range(len(params['tracking_files'])):
            csv_data, skipped = holo_io2.read_csv(
                chunk.node.recordingDir.value + params['tracking_files'][i], 
                params['skip_n_lines'][i])
            keyframes = keyframe_names[i]
            keyframes_ext = params['orig_images_extensions'][i]
            new_csv_data = {}
            csv_time = np.array(list(map(int,csv_data.keys())))
            for keyframe in keyframes:
                keyframe_time = int(keyframe[:-(len(keyframes_ext)+1)])
                csv_id = np.argmin(np.abs(csv_time - keyframe_time))
                if np.abs(csv_time[csv_id] - keyframe_time) < max_time_diff:
                    csv_line = csv_data[str(csv_time[csv_id])]
                    new_csv_data[str(keyframe_time)] = csv_line.replace(str(csv_time[csv_id]), str(keyframe_time))
            holo_io2.write_csv(skipped, new_csv_data, chunk.node.output.value + params['tracking_files'][i])

    def copy_extrinsic_files(self, chunk):
        recordingDir = chunk.node.recordingDir.value
        extrinsics_files = [f for f in os.listdir(recordingDir) if len(f)>15 and f[-15:]=='_extrinsics.txt']
        for extrinsics_file in extrinsics_files:
            shutil.copy2(recordingDir + '/' + extrinsics_file, chunk.node.output.value)


    def processChunk(self, chunk):
        try:
            chunk.logManager.start(chunk.node.verboseLevel.value)
            
            if not chunk.node.recordingDir:
                chunk.logger.warning('Nothing to process')
                return
            if not chunk.node.output.value:
                return

            # setting
            if chunk.node.recordingSource.value == 'HoloLens':
                params = self.get_params_for_hololens_recording(chunk)

            if chunk.node.recordingSource.value == 'HoloLens2':
                params = self.get_params_for_hololens2_recording(chunk)

            if chunk.node.recordingSource.value in ['COLMAP', 'ORB SLAM', 'BAD SLAM','IOS AR', 'Android AR']:
                chunk.logger.warning('This input is not supported yet.')
                return
             
            # process
            keyframe_selector = UtilsKeyframes()
            if not os.path.exists(chunk.node.output.value):
                os.mkdir(chunk.node.output.value)

            chunk.logger.info('Select and copy keyframes.')    
            keyframe_names = keyframe_selector.copy_keyframes(
                params['input_images_folders'],
                params['output_images_folders'], 
                params['blur_thresholds'],
                params['min_frame_offsets'], 
                params['new_images_extensions'],
                logger = chunk.logger)

            chunk.logger.info('Compose new tracking files')
            if chunk.node.recordingSource.value == 'HoloLens':
                self.compose_new_hololens_tracking_files(chunk, keyframe_selector, keyframe_names, params)

            if chunk.node.recordingSource.value == 'HoloLens2':
                self.compose_new_hololens2_tracking_files(chunk, keyframe_selector, keyframe_names, params)
                self.copy_extrinsic_files(chunk)

            chunk.logger.info('Keyframe selector is done.') 

        except AssertionError as err:
            chunk.logger.error("Error in keyframe selector: " + err)
        finally:
            chunk.logManager.end()
