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

class HololensPointcloudComposer(desc.Node):

    category = 'ARTwin'
    documentation = '''
This node transform the depthmaps from hololens recording into one coordinate system.
'''

    inputs = [
        desc.File(
            name="recording_dir",
            label="Recording Folder",
            description="HoloLens recording directory (images in pv/*.jpg, " \
                "depth in long_throw_depth/*.pgm, + related .csv).",
            value="",
            uid=[0],
        ),
        desc.File(
            name="uv_file",
            label="UV decoding file",
            description="Text file with transformation data from depthmap to " \
                "depth camera coordinte system (uvdata.txt).",
            value="",
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
            
            if not chunk.node.recording_dir:
                chunk.logger.warning('Nothing to process')
                return
            if not chunk.node.uv_file:
                chunk.logger.warning('Missing depth decoding file (uvdata.txt)')
                return
            if not chunk.node.output.value:
                return

            # process
            holo_io = HoloIO()
            
            chunk.logger.info('Reading HoloLens depthmaps.')
            holo_xyz = holo_io.read_dense_pointcloud(chunk.node.recording_dir.value + "/long_throw_depth", 
                chunk.node.uv_file.value, chunk.node.recording_dir.value + "/long_throw_depth.csv",
                logger=chunk.logger) 

            if not os.path.exists(chunk.node.output.value):
                os.mkdir(chunk.node.output.value)
            chunk.logger.info('Saving model.obj')
            holo_io.write_pointcloud_to_file(holo_xyz, chunk.node.output.value + "/model.obj")
            chunk.logger.info('Hololens pointcloud composer is done.')

        except AssertionError as err:
            chunk.logger.error("Error in HoloLens dense pointlcoud composer: " + err)
        finally:
            chunk.logManager.end()
