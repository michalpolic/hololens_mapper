from __future__ import print_function

__version__ = "0.1"

from meshroom.core import desc
import shutil
import glob
import os
import sys


class InitMeshroomContainer(desc.Node):

    category = 'ARTwin'
    documentation = '''
This node initialize nescessary enviroment variables to run Meshroom nodes. 
'''

    inputs = [
        desc.File(
            name="workingDir",
            label="Working directory",
            description="The path to working directory. This directory will be wisible in the container as /data dir. " + \
                "All the files has to be in this folder or any subfolder. All absolute paths will be automaticaly " + \
                "adjusted to run in the container. Do not adujst paths in Meshroom nodes.",
            value="",
            uid=[0],
        ), 
        desc.StringParam(
            name="containerId",
            label="Container ID",
            description="The name of the container for docker (Windows) or path to Singularity container (Linux).",
            value="",
            uid=[],
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

    def processChunk(self, chunk):
        try:
            chunk.logManager.start(chunk.node.verboseLevel.value)
            
            if not chunk.node.workingDir.value:
                chunk.logger.warning('Nothing to process')
                return

            chunk.logger.info('Setup working directory.') 
            os.environ.set('MESHROOM_WORKING_DIR', chunk.node.workingDir.value)

            chunk.logger.info('Setup container name/path.') 
            if not chunk.node.containerId.value:
                singularity_container_found = False
                dir_path = __file__
                for i in range(20):
                    dir_path = os.path.dirname(dir_path)
                    files_list = os.listdir(dir_path)
                    for file_path in files_list:
                        if (file_path.find("alicevision.sif") != -1):
                            singularity_container_found = True
                            containerId = file_path
                assert singularity_container_found, "The AliceVision container was not found."
            else:
                containerId = chunk.node.containerId.value
            os.environ.set('MESHROOM_CONTAINER', containerId)
            chunk.logger.info('OS variables was setuped correctly.') 

        except AssertionError as err:
            chunk.logger.error("Error in keyframe selector: " + err)
        finally:
            chunk.logManager.end()

