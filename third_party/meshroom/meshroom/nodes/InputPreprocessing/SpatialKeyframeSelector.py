from __future__ import print_function
from src.utils.UtilsKeyframes import UtilsKeyframes
from src.holo.HoloIO2 import HoloIO2
from src.holo.HoloIO import HoloIO

__version__ = "0.1"

from meshroom.core import desc
import shutil
import glob
import os
import sys
import numpy as np
from igraph import *
from pathlib import Path
import pickle

# import mapper packages
dir_path = __file__
for i in range(6):
    dir_path = os.path.dirname(dir_path)
sys.path.append(dir_path)

Intrinsic = [
    desc.IntParam(name='intrinsicId', label='Id', description='Intrinsic UID', value=-1, uid=[0], range=None),
    desc.StringParam(name='trackingFile', label='Tracking file', description='Abreviation for the tracking file, e.g., pv for pv.csv or <record.>_pv.txt.', value='', uid=[0]),
    desc.IntParam(name='width', label='Width', description='Image Width', value=0, uid=[0], range=(0, 10000, 1)),
    desc.IntParam(name='height', label='Height', description='Image Height', value=0, uid=[0], range=(0, 10000, 1)),
    desc.GroupAttribute(name='pxFocalLength', label='Focal Length', description='Focal Length (in pixels).', groupDesc=[
        desc.FloatParam(name='x', label='x', description='', value=0, uid=[0], range=None),
        desc.FloatParam(name='y', label='y', description='', value=0, uid=[0], range=None),
        ]),
    desc.GroupAttribute(name='principalPoint', label='Principal Point', description='Position of the Optical Center in the Image (i.e. the sensor surface).', groupDesc=[
        desc.FloatParam(name='x', label='x', description='', value=0, uid=[0], range=(0, 10000, 1)),
        desc.FloatParam(name='y', label='y', description='', value=0, uid=[0], range=(0, 10000, 1)),
        ]),
    desc.ListAttribute(
        name='distortionParams',
        elementDesc=desc.FloatParam(name='p', label='', description='', value=0.0, uid=[0], range=(-2, 2, 0.01)),
        label='Distortion Params',
        description='Distortion Parameters',
    ),
]

class SpatialKeyframeSelector(desc.Node):
    size = desc.DynamicNodeSize('intrinsics')
    category = 'Input Preprocessing'
    documentation = '''
This node select subset of images (keyframes) and copy them to output path. 
'''

    inputs = [
        desc.File(
            name="recordingDir",
            label="Recording Folder",
            description="HoloLens recording directory (images in pv/*.jpg, "
            "depth in long_throw_depth/*.pgm, etc. + related .csv).",
            value="",
            uid=[0],
        ),
        desc.File(
            name='imageFolderNames',
            label='Image Folder Names',
            description='''
            A textfile containing the list of folder names, which have images.
            If not supplied, the folder default hololens folder structure is assumed.''',
            value='',
            uid=[0],
        ),
        desc.ChoiceParam(
            name='recordingSource',
            label='Recording source',
            description='The device/algorithm used to create recording folder.',
            value='HoloLens2',
            values=['HoloLens', 'HoloLens2', 'COLMAP',
                    'ORB SLAM', 'BAD SLAM', 'IOS AR', 'Android AR', 'BROCA'],
            exclusive=True,
            uid=[0],
        ),
        desc.ListAttribute(
            name='intrinsics',
            elementDesc=desc.GroupAttribute(
                name='intrinsic', 
                label='Intrinsic', 
                description='', 
                groupDesc=Intrinsic,
            ),
            label='Camera parameters',
            description='Camera Intrinsics',
            group='',
        ),
        desc.FloatParam(
            name='minImgsOverlap',
            label='Minimal overlap [%]',
            description="Minimal overlap between the image and any other image.",
            value=25.0,
            range=(5.0, 80.0, 1.0),
            uid=[0],
        ),
        desc.FloatParam(
            name='minSpatialDistance',
            label='Min. spatial distance [m]',
            description='The maximal distance between two frames.',
            value=0.35,
            range=(0, 5, 0.01),
            uid=[0],
        ),
        desc.FloatParam(
            name='maxSpatialDistance',
            label='Max. spatial distance [m]',
            description='The maximal distance between two frames.',
            value=0.5,
            range=(0.1, 10, 0.01),
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

    def get_params_for_hololens2_recording(self, chunk):
        params = {}
        recordingDir = chunk.node.recordingDir.value
        pv_files = [f for f in os.listdir(recordingDir) if len(
            f) > 7 and f[-7:] == '_pv.txt']
        assert len(
            pv_files) > 0, 'Failed to find the tracking info for PV camera in recording dir.'
        params['tracking_files'] = ["/" + pv_files[0], "/VLC LF_rig2world.txt", "/VLC LL_rig2world.txt",
                                    "/VLC RF_rig2world.txt", "/VLC RR_rig2world.txt"]
        params['skip_n_lines'] = [1, 0, 0, 0, 0]
        params['orig_images_extensions'] = ["png", "pgm", "pgm", "pgm", "pgm"]
        params['new_images_extensions'] = ["png", "pgm", "pgm", "pgm", "pgm"]
        params['input_images_folders'] = [recordingDir + "/PV",
                                          recordingDir + "/VLC LF", recordingDir + "/VLC LL",
                                          recordingDir + "/VLC RF", recordingDir + "/VLC RR"]
        params['output_images_folders'] = [chunk.node.output.value + "/pv",
                                           chunk.node.output.value + "/vlc_lf", chunk.node.output.value + "/vlc_ll",
                                           chunk.node.output.value + "/vlc_rf", chunk.node.output.value + "/vlc_rr"]
        return params

    def compose_new_hololens2_tracking_files(self, chunk, keyframe_selector,
                                             keyframe_names, params, max_time_diff=100):
        holo_io2 = HoloIO2()
        for i in range(len(params['tracking_files'])):
            csv_data, skipped = holo_io2.read_csv(
                chunk.node.recordingDir.value + params['tracking_files'][i],
                params['skip_n_lines'][i])
            keyframes = keyframe_names[i]
            keyframes_ext = params['orig_images_extensions'][i]
            new_csv_data = {}
            csv_time = np.array(list(map(int, csv_data.keys())))
            for keyframe in keyframes:
                keyframe_time = int(keyframe[:-(len(keyframes_ext)+1)])
                csv_id = np.argmin(np.abs(csv_time - keyframe_time))
                if np.abs(csv_time[csv_id] - keyframe_time) < max_time_diff:
                    csv_line = csv_data[str(csv_time[csv_id])]
                    new_csv_data[str(keyframe_time)] = csv_line.replace(
                        str(csv_time[csv_id]), str(keyframe_time))
            holo_io2.write_csv(
                skipped, new_csv_data, chunk.node.output.value + params['tracking_files'][i])

    def copy_extrinsic_files(self, chunk):
        recordingDir = chunk.node.recordingDir.value
        extrinsics_files = [f for f in os.listdir(recordingDir) if len(
            f) > 15 and f[-15:] == '_extrinsics.txt']
        for extrinsics_file in extrinsics_files:
            shutil.copy2(recordingDir + '/' + extrinsics_file,
                         chunk.node.output.value)

    def processChunk(self, chunk):
        try:
            chunk.logManager.start(chunk.node.verboseLevel.value)

            if not chunk.node.recordingDir:
                chunk.logger.warning('Nothing to process')
                return
            if not chunk.node.output.value:
                return
            if (not chunk.node.imageFolderNames or chunk.node.imageFolderNames.value == '') and \
                    chunk.node.recordingSource.value == 'BROCA':
                chunk.logger.warning(
                    'File specifying folder names missing. It has to be supplied when using BROCA.')
                return

            # setting
            holo_io = HoloIO()
            holo_io2 = HoloIO2()
            if chunk.node.recordingSource.value == 'HoloLens2':
                chunk.logger.info('Loading intrinsics.')
                intrinsics = chunk.node.intrinsics.getPrimitiveValue(exportDefault=True)
                cameras, images, _ = holo_io2.load_model(chunk.node.recordingDir.value, intrinsics)
                depth_data_dir = Path(chunk.node.recordingDir.value) / 'Depth Long Throw'

            if chunk.node.recordingSource.value in ['HoloLens', 'COLMAP',
                                                    'ORB SLAM', 'BAD SLAM', 'IOS AR', 'Android AR', 'BROCA']:
                chunk.logger.warning('This input is not supported yet.')
                return

            # process
            keyframe_selector = UtilsKeyframes()
            out_path = Path(chunk.node.output.value)
            out_path.mkdir(exist_ok=True)

            # image_weights = keyframe_selector.estimate_images_blur(chunk.node.recordingDir.value, images)
            # with open(out_path / "tmp_image_weights.pkl", "wb") as output_file:
            #     pickle.dump(image_weights, output_file)
            # with open(out_path / "tmp_image_weights.pkl", "rb") as input_file:
            #     image_weights = pickle.load(input_file)

            # G = keyframe_selector.compose_view_graph(images, depth_data_dir, \
            #     cameras, chunk.node.minImgsOverlap.value, chunk.node.minSpatialDistance.value , \
            #     chunk.node.maxSpatialDistance.value)
            # with open(out_path / "tmp_igraph_G.pkl", "wb") as output_file:
            #     pickle.dump(G, output_file)
            # with open(out_path / "tmp_igraph_G.pkl", "rb") as input_file:
            #     G = pickle.load(input_file)

            # EG, edge_weights = keyframe_selector.convert_edges_to_vertices(G, image_weights)
            # with open(out_path / "tmp_igraph_EG.pkl", "wb") as output_file:
            #     pickle.dump(EG, output_file)
            # with open(out_path / "tmp_edge_weights.pkl", "wb") as output_file:
            #     pickle.dump(edge_weights, output_file)
            with open(out_path / "tmp_igraph_EG.pkl", "rb") as input_file:
                EG = pickle.load(input_file)
            with open(out_path / "tmp_edge_weights.pkl", "rb") as input_file:
                edge_weights = pickle.load(input_file)

            ESTG = EG.spanning_tree(edge_weights)
            selected_images = keyframe_selector.get_utilized_images(images, ESTG)

            print('There was selected ' + str(len(selected_images)) + ' images out of ' + str(len(images)) + ' images.')
            # chunk.logger.info('Select and copy keyframes.')
            # keyframe_names = keyframe_selector.copy_keyframes(
            #     params['input_images_folders'],
            #     params['output_images_folders'],
            #     params['blur_thresholds'],
            #     params['min_frame_offsets'],
            #     params['new_images_extensions'],
            #     logger = chunk.logger)

            # if chunk.node.recordingSource.value == 'HoloLens2':
            #     self.compose_new_hololens2_tracking_files(chunk, keyframe_selector, keyframe_names, params)
            #     self.copy_extrinsic_files(chunk)

            chunk.logger.info('Keyframe selector is done.')

        except AssertionError as err:
            chunk.logger.error("Error in keyframe selector: " + err)
        finally:
            chunk.logManager.end()
