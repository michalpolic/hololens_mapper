from __future__ import print_function
__version__ = "0.1"

from meshroom.core import desc
import shutil
import glob
import os
import sys
os.environ["KMP_DUPLICATE_LIB_OK"]="TRUE"

# import mapper packages
dir_path = __file__
for i in range(6):
    dir_path = os.path.dirname(dir_path)
sys.path.append(dir_path)
from src.holo.HoloIO import HoloIO
from src.holo.HoloIO2 import HoloIO2

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
    category = 'InputPreprocessing'
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

        holo_io = HoloIO()
        xyz = holo_io.compose_common_pointcloud(chunk.node.recordingDir.value + "/long_throw_depth", 
            uvfile_path, chunk.node.recordingDir.value + "/long_throw_depth.csv", logger=chunk.logger) 

        return xyz


    def compose_pointcloud_from_hololens2_recording(self, chunk, params):
        # compose pointcloud from depthmaps
        chunk.logger.info('Reading HoloLens2 pointclouds.')

        holo2_io = HoloIO2()
        xyz = holo2_io.compose_common_pointcloud(chunk.node.recordingDir.value + "/Depth Long Throw", logger=chunk.logger) 

        return xyz    


    def processChunk(self, chunk):
        try:
            chunk.logManager.start(chunk.node.verboseLevel.value)
            
            if not chunk.node.recordingDir:
                chunk.logger.warning('Nothing to process')
                return
            
            # process
            params = chunk.node.parameters.getPrimitiveValue(exportDefault=True)
            if chunk.node.recordingSource.value == 'HoloLens':
                xyz = self.compose_pointcloud_from_hololens_recording(chunk, params)

            if chunk.node.recordingSource.value == 'HoloLens2':
                xyz = self.compose_pointcloud_from_hololens2_recording(chunk, params)

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
