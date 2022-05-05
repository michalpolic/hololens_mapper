from __future__ import print_function
import shutil

__version__ = '0.1'

from meshroom.core import desc
import os
import sys
from pathlib import Path
from shutil import copy2

# import mapper packages
dir_path = __file__
for i in range(6):
    dir_path = os.path.dirname(dir_path)
sys.path.append(dir_path)
from src.holo.HoloIO import HoloIO
from src.colmap.Colmap import Colmap
from src.utils.UtilsContainers import UtilsContainers


class KeypointsDetector(desc.Node):

    category = 'Sparse Reconstruction'
    documentation = '''
This node compute keypoints in the images and save them into the database.
The database is in the COLMAP format.
'''

    inputs = [
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
        desc.File(
            name='database',
            label='Input database',
            description='''
            The database with keypoints and matches for some subreconstruction. 
            The keypoints will be find for the new images.''',
            value='',
            uid=[0],
        ),
        desc.ChoiceParam(
            name='algorithm',
            label='Detector',
            description='The algorithm used to extract keypoints and descriptors.',
            value='SIFT',
            values=['SIFT'],
            uid=[0],
            exclusive=True,
        ),  
        desc.BoolParam(
            name='removeImages', 
            label='Remove images',
            description='Remove images from cache after keypoint detection.',
            value=True,
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

    outputs = [
        desc.File(
            name='output',
            label='Database file',
            description='',
            value=os.path.join(desc.Node.internalFolder,'database.db'),
            uid=[],
            ),
    ]

    def processChunk(self, chunk):
        try:
            chunk.logManager.start(chunk.node.verboseLevel.value)
            
            if not chunk.node.imageDirectory:
                chunk.logger.warning('Folder with images is missing.')
                return
            if not chunk.node.imageFolderNames or chunk.node.imageFolderNames.value == '':
                chunk.logger.warning('File specifying folder names missing, assuming default hololens folder structure.')
            if not chunk.node.output.value:
                return

            chunk.logger.info('Start matching.')
            out_dir = os.path.dirname(chunk.node.output.value)
            holo_io = HoloIO()

            # get folder names and copy image to out dir
            if chunk.node.imageFolderNames and chunk.node.imageFolderNames.value != '':
                with open(chunk.node.imageFolderNames.value, "r") as f:
                    img_folders = f.read().splitlines()
                holo_io.copy_sfm_images(chunk.node.imageDirectory.value, out_dir, imgs_dir_list=img_folders)
            else:
                holo_io.copy_sfm_images(chunk.node.imageDirectory.value, out_dir)
            
            # init contriners
            chunk.logger.info('Init COLMAP container')
            if sys.platform == 'win32':
                out_dir = out_dir[0].lower() + out_dir[1::]
                colmap_container = UtilsContainers('docker', 'uodcvip/colmap', '/host_mnt/' + out_dir.replace(':',''))
            else:
                colmap_container = UtilsContainers('singularity', dir_path + '/colmap.sif', out_dir)
            colmap = Colmap(colmap_container)       

            # init db for keypoints 
            if not chunk.node.database.value:
                colmap.prepare_database(out_dir + '/database.db', '/data/database.db')
            else:
                shutil.copy2(chunk.node.database.value, chunk.node.output.value)

            # COLMAP detector
            if chunk.node.algorithm.value == 'SIFT':
                chunk.logger.info('COLMAP --> compute SIFT features')
                additional_settings = {
                    "ImageReader.camera_model": "OPENCV_FISHEYE",
                    "ImageReader.camera_params": '"1.1886892840742685e+03, 1.1893016496137716e+03, 1.6319484444597201e+03, 1.2428175443297432e+03, -6.5074864654844314e-02, 2.2948182911307041e-02, -3.9319897787193784e-03, -3.7411424922587362e-03"'
                }
                colmap.extract_features('/data/database.db', '/data', settings=additional_settings)           # COLMAP feature extractor
            
            # remove images in cache
            if chunk.node.removeImages.value:
                holo_io.remove_images_from_cache(out_dir)

            chunk.logger.info('KeypointsDetector done.')
          
        except AssertionError as err:
            chunk.logger.error('Error in keyframe selector: ' + err)
        finally:
            chunk.logManager.end()
