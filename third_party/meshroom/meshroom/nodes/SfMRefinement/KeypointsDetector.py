from __future__ import print_function

__version__ = '0.1'

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
from src.holo.HoloIO import HoloIO
from src.colmap.ColmapIO import ColmapIO
from src.colmap.Colmap import Colmap
from src.utils.UtilsContainers import UtilsContainers
from src.utils.UtilsMatcher import UtilsMatcher

class KeypointsDetector(desc.Node):

    category = 'SfMRefinement'
    documentation = '''
This node compute keypoints in the images and save them into the database.
The database is in the COLMAP format.
'''

    inputs = [
        desc.File(
            name='inputSfM',
            label='Input SfM',
            description='''
            The directory containing rough input SfM in COLMAP format. 
            The camera models are in cameras.txt, poses are in images.txt 
            and points in points3D.txt.''',
            value='',
            uid=[0],
        ),
        desc.File(
            name='imagesFolder',
            label='Directory with images',
            description='''
            The directory containing input images.
            The subdirectories are specified in images.txt.''',
            value='',
            uid=[0],
        ),
        desc.File(
            name='imagePairs',
            label='Image pairs to match',
            description='File with image names to match. ' \
                'Each image pair is on one line, e.g. img1 img2.',
            value='',
            uid=[0],
        ),
        desc.ChoiceParam(
            name='algorithm',
            label='Matching algorithm',
            description='The algorithm used to extract matches between images',
            value='SIFT',
            values=['SIFT'], #, 'SuperGlue', 'patch2pix'],
            uid=[0],
            exclusive=True,
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
            label='Output Folder',
            description='',
            value=desc.Node.internalFolder,
            uid=[],
            ),
    ]

    def processChunk(self, chunk):
        try:
            chunk.logManager.start(chunk.node.verboseLevel.value)
            
            if not chunk.node.inputSfM:
                chunk.logger.warning('COLMAP SfM directory is missing.')
                return
            if not chunk.node.imagesFolder:
                chunk.logger.warning('Folder with images is missing.')
                return
            if not chunk.node.imagePairs.value:
                chunk.logger.info('Image pairs missing, all pairs will be assumed.')
            if not chunk.node.output.value:
                return

            chunk.logger.info('Start matching.')
            out_dir = chunk.node.output.value
            holo_io = HoloIO()

            # copy images/image_pairs.txt to working directory
            holo_io.copy_sfm_images(chunk.node.imagesFolder.value, out_dir)
            if chunk.node.imagePairs:
                copy2(chunk.node.imagePairs.value, out_dir)
                rel_path_to_img_pairs = '/data/' + os.path.basename(chunk.node.imagePairs.value)
            
            # init contriners
            chunk.logger.info('Init COLMAP container')
            if sys.platform == 'win32':
                out_dir = out_dir[0].lower() + out_dir[1::]
                colmap_container = UtilsContainers('docker', 'uodcvip/colmap', '/host_mnt/' + out_dir.replace(':',''))
            else:
                colmap_container = UtilsContainers('singularity', dir_path + '/colmap.sif', out_dir)
            colmap = Colmap(colmap_container)
            matcher = UtilsMatcher(chunk.node.algorithm.value, colmap)        

            # init db for keypoints 
            colmap.prepare_database(out_dir + '/database.db', '/data/database.db')

            # COLMAP detector
            if matcher._matcher_name == 'SIFT':
                chunk.logger.info('COLMAP --> compute SIFT features')
                colmap.extract_features('/data/database.db', '/data')           # COLMAP feature extractor
            
            chunk.logger.info('KeypointsDetector done.')
          
        except AssertionError as err:
            chunk.logger.error('Error in keyframe selector: ' + err)
        finally:
            chunk.logManager.end()
