from __future__ import print_function

__version__ = "0.1"

from meshroom.core import desc
import shutil
import os
import shutil
import sys


# import mapper packages
dir_path = __file__
for i in range(6):
    dir_path = os.path.dirname(dir_path)
sys.path.append(dir_path)
from src.utils.UtilsContainers import UtilsContainers


class HlocLocalizer(desc.Node):

    category = 'ARTwin'
    documentation = '''
Runs Hloc localization on input images.
                    
'''

    inputs = [
        desc.File(
            name="queryFile",
            label="Query file path",
            description="Path to Hloc query file (.txt)",
            value="",
            uid=[0],
        ),
        desc.File(
            name="hlocMapDir",
            label="Hloc Map directory",
            description="Hloc map directory (database, images, features)",
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
            label="Output folder",
            description="",
            value=desc.Node.internalFolder,
            uid=[],
            ),
    ]

    def processChunk(self, chunk):
        try:
            chunk.logManager.start(chunk.node.verboseLevel.value)
            output_folder = chunk.node.output.value
            
            if not output_folder:
                return

            map_folder = chunk.node.hlocMapDir.value

            if not map_folder:
                chunk.logger.warning('Nothing to process, Hloc map required')
                return

            query_file = chunk.node.queryFile.value
            if not query_file:
                chunk.logger.warning('Nothing to process, query file required')
                return

            if output_folder[-1] != '/':
                output_folder = output_folder + '/'

            if map_folder[-1] != '/':
                map_folder = map_folder + '/'

            
            hloc_container = UtilsContainers("singularity", dir_path + "/hloc.sif", './third_party/Hierarchical-Localization/')
            chunk.logger.info('Running Hloc Localization.')   
            hloc_container.command_dict("python3 ./third_party/Hierarchical-Localization/run_hloc.py " + map_folder + " " + query_file + " " + output_folder, {})


            chunk.logger.info('Localization done.') 

        except AssertionError as err:
            chunk.logger.error("Error in hlocLocalizer selector: " + err)
        finally:
            chunk.logManager.end()
