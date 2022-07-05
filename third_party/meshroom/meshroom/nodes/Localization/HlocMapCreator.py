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
from src.colmap.Colmap import Colmap
from src.utils.UtilsContainers import UtilsContainers
from src.holo.HoloIO import HoloIO
from src.colmap.ColmapIO import ColmapIO


class HlocMapCreator(desc.Node):

    category = 'Localization'
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
        desc.File(
            name='imageDirectory',
            label='Image Directory',
            description='''
            The directory containing input image folders.
            Select a file specifying the subdirectories from with images are taken in "Image Folder Names".''',
            value='',
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
        desc.BoolParam(
            name='copyDensePts', 
            label='Copy dense points',
            description='''Copy dense point cloud if available in COLMAP SfM folder.''',
            value=False, 
            uid=[0]
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
            if not chunk.node.imageDirectory:
                chunk.logger.warning('Transformed images directory is missing.')
                return
            if not chunk.node.imageFolderNames or chunk.node.imageFolderNames.value == '':
                chunk.logger.warning('File specifying folder names missing, assuming default hololens folder structure.')
            if not chunk.node.output.value:
                return

            # copy inputs into the working directory
            out_dir = chunk.node.output.value
            holo_io = HoloIO()
            # get folder names and copy image to out dir
            if chunk.node.imageFolderNames and chunk.node.imageFolderNames.value != '':
                with open(chunk.node.imageFolderNames.value, "r") as f:
                    img_folders = f.read().splitlines()
                holo_io.copy_sfm_images(chunk.node.imageDirectory.value, out_dir, imgs_dir_list=img_folders)
            else:
                holo_io.copy_sfm_images(chunk.node.imageDirectory.value, out_dir)
            copy2(chunk.node.inputSfM.value + '/cameras.txt', out_dir)
            copy2(chunk.node.inputSfM.value + '/images.txt', out_dir)
            copy2(chunk.node.inputSfM.value + '/points3D.txt', out_dir)

            # create container
            chunk.logger.info('Init COLMAP container')
            if sys.platform == 'win32':
                out_dir = out_dir[0].lower() + out_dir[1::]
                hloc_container = UtilsContainers("docker", "hloc:latest", "/host_mnt/" + out_dir.replace(":",""))
                colmap_container = UtilsContainers("docker", "uodcvip/colmap", "/host_mnt/" + out_dir.replace(":",""))
            else:
                hloc_container = UtilsContainers("singularity", dir_path + "/hloc.sif", out_dir)
                colmap_container = UtilsContainers("singularity", dir_path + "/colmap.sif", out_dir)
            hloc = Hloc(hloc_container)
            colmap = Colmap(colmap_container)

            # update image names 
            colmap_io = ColmapIO()
            cameras, images, points3D = colmap_io.load_model(out_dir)
            images = hloc.update_image_names(images)
            colmap_io.write_model(out_dir, cameras, images, points3D)

            # convert COLMAP SfM in TXT to bin 
            colmap.model_converter('/data','/data', 'BIN')

            # build the map
            hloc.build_map('/data','/data')

            # copy dense point cloud if available
            if chunk.node.copyDensePts.value and os.path.isfile(chunk.node.inputSfM.value + '/model.obj'):
                copy2(chunk.node.inputSfM.value + '/model.obj' , out_dir)

            chunk.logger.info('HLOC map composer done.')
          
        except AssertionError as err:
            chunk.logger.error("Error in keyframe selector: " + err)
        finally:
            chunk.logManager.end()
