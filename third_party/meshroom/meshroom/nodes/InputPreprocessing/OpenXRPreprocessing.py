from __future__ import print_function

from numpy import False_

__version__ = '0.1'

from meshroom.core import desc
import shutil
import glob
import os
import time
import sys
import tarfile

# import mapper packages
dir_path = __file__
for i in range(6):
    dir_path = os.path.dirname(dir_path)
sys.path.append(dir_path)
from src.holo.HoloIO import HoloIO

class OpenXRPreprocessing(desc.Node):

    category = 'Input Preprocessing'
    documentation = '''
This node download the recordings available at HoloLens 1. 
The data are formated such a way to be processed by OI Convertor.
'''

    inputs = [
        desc.File(
            name='recordingsFolder',
            label='Recordings folder',
            description='The folder where to download all the recordings.',
            value='',
            uid=[0],
        ),        
        desc.BoolParam(
            name="delete", 
            label="Delete binaries",
            description="Delete the binaries after unpacking.",
            value=False,
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
            
            if not chunk.node.recordingsFolder:
                chunk.logger.warning('Missing recordings folder field.')
                return

            # # init
            # holo_io = HoloIO()
            # folder = chunk.node.recordingsFolder.value
            # sensors = ["pv", "vlc_ll", "vlc_lf", "vlc_rf", "vlc_rr", "long_throw_depth"]
            # holo_io.mkdir_if_not_exists(folder, logger = chunk.logger)


                        

            # delete recordings on device
            if chunk.node.delete.value:
                pass

            chunk.logger.info('HoloLens1Downloader is done.') 

        except AssertionError as err:
            chunk.logger.error("Error in keyframe selector: " + err)
        finally:
            chunk.logManager.end()