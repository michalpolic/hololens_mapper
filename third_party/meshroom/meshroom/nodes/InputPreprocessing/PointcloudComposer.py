from __future__ import print_function
__version__ = "0.1"

from meshroom.core import desc
import shutil
import glob
import os
import sys
import numpy as np
os.environ["KMP_DUPLICATE_LIB_OK"]="TRUE"

# import mapper packages
dir_path = __file__
for i in range(6):
    dir_path = os.path.dirname(dir_path)
sys.path.append(dir_path)
from src.holo.HoloIO import HoloIO
from src.holo.HoloIO2 import HoloIO2
from src.utils.UtilsMath import UtilsMath

Parameters = [
    desc.ChoiceParam(
        name='name',
        label='Name',
        description='The parameter name.',
        value='HoloLens: UVfile',
        values=['HoloLens: UVfile'],
        exclusive=True,
        uid=[],
        ),
    desc.StringParam(name="value", label="Value", description="The value for selected parameter.", value="", uid=[]),
]

class PointcloudComposer(desc.Node):
    size = desc.DynamicNodeSize("parameters")
    category = 'Input Preprocessing'
    documentation = '''
This node creates single sparse/dense pointcloud out of the input recording directory.
Supported recodring direcotries are HoloLens, HoloLens 2. 

Required parameres for idividual recordings:
HoloLens: 
- UVfile: the path to uvdata.txt with lookup table for mapping depthmaps into cartesian coordinate system

HoloLens 2:
- all parameters are included in the recording
'''

    inputs = [
        desc.File(
            name="recordingDir",
            label="Recording Folder",
            description="The recording directory.",
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
            name='mindepth',
            label='Minimal depth',
            description='The threshold for minimal assumed depth. Smaller values will be filtered out.',
            value=0.0,
            range=(0.0, 25, 0.01),
            uid=[0],
        ),
        desc.FloatParam(
            name='maxdepth',
            label='Maximal depth',
            description='The threshold for maximal assumed depth. Larger values will be filtered out.',
            value=25.0,
            range=(0.5, 100, 0.1),
            uid=[0],
        ),
        desc.IntParam(
            name='hashScale', 
            label='Points hash scale', 
            description='''
            Points hash scale is an multiple of original pointcloud. 
            The pointcloud will be sparser with given distace between two neighbouring points.
            For example, if the pointcloud is in meters, scale 100 creates an 
            hashed point cloud in centimeters grid before projection to images.
            For value < 1 return the original point cloud.''', 
            value=-1, 
            uid=[0], 
            range=(-1, 10000, 1),
        ),
        desc.ListAttribute(
            name="parameters",
            elementDesc=desc.GroupAttribute(name="parameters", label="Parameters", description="", groupDesc=Parameters),
            label="Recording parameters",
            description="The parameters required to compose sigle pointcloud.",
            group="",
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
            label="Output File",
            description="",
            value=desc.Node.internalFolder + "/model.obj",
            uid=[],
            ),
    ]


    def compose_pointcloud_from_hololens_recording(self, chunk, params):
        # check the decoding file for depthmaps
        uvfile_path = None
        for param in params:
            if param['name'] == 'HoloLens: UVfile':
                uvfile_path = param['value']
        if uvfile_path == None:
            chunk.logger.warning('Missing depth decoding file (uvdata.txt)')
            return []

        # compose pointcloud from depthmaps
        chunk.logger.info('Reading HoloLens depthmaps.')
        chunk.logger.warning('The depth filtering for HoloLens is not implemented.')

        holo_io = HoloIO()
        xyz = holo_io.compose_common_pointcloud(chunk.node.recordingDir.value + "/long_throw_depth", 
            uvfile_path, chunk.node.recordingDir.value + "/long_throw_depth.csv", logger=chunk.logger) 
        if chunk.node.hashScale.value > 0:
            utils_math = UtilsMath()
            pts, _, _ = utils_math.hash_points(pts, chunk.node.hashScale.value)
        return xyz


    def compose_pointcloud_from_hololens2_recording(self, chunk, params, mindepth, maxdepth):
        # compose pointcloud from depthmaps
        chunk.logger.info('Reading HoloLens2 pointclouds.')

        # load camera centers
        camera_centers = {}
        rig2campath = os.path.join(chunk.node.recordingDir.value, "Depth Long Throw_extrinsics.txt")
        rig2world_path = os.path.join(chunk.node.recordingDir.value, "Depth Long Throw_rig2world.txt")
        rig2cam = np.loadtxt(str(rig2campath), delimiter=',').reshape((4, 4))
        data = np.loadtxt(str(rig2world_path), delimiter=',')
        for value in data:
            timestamp = int(value[0])
            world2rig = np.linalg.inv(value[1:].reshape((4, 4)))
            world2cam = rig2cam @ world2rig
            camera_centers[timestamp] = - world2cam[0:3,0:3].T @ world2cam[0:3,3]

        holo2_io = HoloIO2()
        xyz = holo2_io.compose_common_pointcloud(
            chunk.node.recordingDir.value + "/Depth Long Throw", logger=chunk.logger, \
            camera_centers = camera_centers, mindepth = mindepth, maxdepth = maxdepth, \
            hash_scale = chunk.node.hashScale.value) 

        return xyz    


    def processChunk(self, chunk):
        try:
            chunk.logManager.start(chunk.node.verboseLevel.value)
            
            if not chunk.node.recordingDir:
                chunk.logger.warning('Nothing to process')
                return
            
            # process
            params = chunk.node.parameters.getPrimitiveValue(exportDefault=True)
            mindepth = chunk.node.mindepth.value
            maxdepth = chunk.node.maxdepth.value
            if chunk.node.recordingSource.value == 'HoloLens':
                xyz = self.compose_pointcloud_from_hololens_recording(chunk, params)

            if chunk.node.recordingSource.value == 'HoloLens2':
                xyz = self.compose_pointcloud_from_hololens2_recording(chunk, params, mindepth, maxdepth)

            if chunk.node.recordingSource.value in ['COLMAP', 'ORB SLAM', 'BAD SLAM','IOS AR', 'Android AR']:
                chunk.logger.warning('This input is not supported yet.')
                return

            # save output    
            chunk.logger.info('Saving common pointcloud into: model.obj')
            holo_io = HoloIO()
            holo_io.write_pointcloud_to_file(xyz, chunk.node.output.value)
            
            chunk.logger.info('Pointcloud composer is done.')

        except AssertionError as err:
            chunk.logger.error("Error in HoloLens dense pointlcoud composer: " + err)
        finally:
            chunk.logManager.end()
