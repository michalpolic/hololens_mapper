from __future__ import print_function

__version__ = "0.1"

from meshroom.core import desc
import shutil
import glob
import os
import sys
from pathlib import Path
from shutil import copy2

# import mapper packages
dir_path = __file__
for i in range(6):
    dir_path = os.path.dirname(dir_path)
sys.path.append(dir_path)
from src.hloc.Hloc import Hloc
from src.utils.UtilsContainers import UtilsContainers
from src.holo.HoloIO import HoloIO


class HlocMapCreator(desc.Node):

    category = 'ARTwin'
    documentation = '''
This node creates HLOC map out of the images and COLMAP SfM.
'''

    inputs = [
        desc.File(
            name="inputSfM",
            label="COLMAP SfM",
            description="The directory containing COLMAP SfM output and images.",
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
            
            if not chunk.node.inputSfM:
                chunk.logger.warning('Transformed SfM directory is missing.')
                return
            if not chunk.node.output.value:
                return

            # copy inputs into the working directory
            out_dir = chunk.node.output.value
            holo_io = HoloIO()
            holo_io.copy_sfm_images(chunk.node.imagesFolder.value, out_dir)
            copy2(chunk.node.inputSfM.value + '/cameras.txt', out_dir)
            copy2(chunk.node.inputSfM.value + '/images.txt', out_dir)
            copy2(chunk.node.inputSfM.value + '/points3D.txt', out_dir)

            # create container
            chunk.logger.info('Init COLMAP container')
            if sys.platform == 'win32':
                out_dir = out_dir[0].lower() + out_dir[1::]
                hloc_container = UtilsContainers("docker", "uodcvip/colmap", "/host_mnt/" + out_dir.replace(":",""))
            else:
                hloc_container = UtilsContainers("singularity", dir_path + "/colmap.sif", out_dir)
            hloc = Hloc(hloc_container)

            # build the map
            hloc.build_map('/data','/data')
            
            chunk.logger.info('HLOC map composer done.')
          
        except AssertionError as err:
            chunk.logger.error("Error in keyframe selector: " + err)
        finally:
            chunk.logManager.end()
