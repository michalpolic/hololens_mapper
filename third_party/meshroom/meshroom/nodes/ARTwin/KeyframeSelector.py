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
from src.utils.UtilsKeyframes import UtilsKeyframes

class KeyframeSelector(desc.Node):

    category = 'ARTwin'
    documentation = '''
This node select subset of images (keyframes) and copy them to output path. 
'''

    inputs = [
        desc.File(
            name="input",
            label="Recording directory",
            description="The directory containing input images in /pv folder",
            value="",
            uid=[0],
        ),
        desc.FloatParam(
            name='blurThreshold',
            label='Blur Threshold',
            description="The threshold for minimal laplacian variation in the image.",
            value=25.0,
            range=(1.0, 1000.0, 1.0),
            uid=[0],
            ),
        desc.IntParam(
            name='minFrameOffset',
            label='Min. Frames Offset',
            description='The minimal number of skipped frames from image sequence.',
            value=13,
            range=(0, 100, 1),
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
            
            if not chunk.node.input:
                chunk.logger.warning('Nothing to process')
                return
            if not chunk.node.output.value:
                return

            # process
            keyframe_selector = UtilsKeyframes()

            chunk.logger.info('Start keyframe selector.')
            if not os.path.exists(chunk.node.output.value):
                os.mkdir(chunk.node.output.value)
            keyframe_selector.copy_keyframes(chunk.node.input.value + "/pv", chunk.node.output.value + "/pv", 
                chunk.node.blurThreshold.value, chunk.node.minFrameOffset.value, logger = chunk.logger)
            chunk.logger.info('Keyframe selector is done.')    
          
        except AssertionError as err:
            chunk.logger.error("Error in keyframe selector: " + err)
        finally:
            chunk.logManager.end()
