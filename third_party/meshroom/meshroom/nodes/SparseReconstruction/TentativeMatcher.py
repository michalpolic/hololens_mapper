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

class TentativeMatcher(desc.Node):

    category = 'Sparse Reconstruction'
    documentation = '''
This node compute tentative matches between selected / all pairs of images.
'''

    inputs = [
        desc.File(
            name='sfmfolder',
            label='SfM Folder',
            description='The directory containing input camera poses ' \
                'saved in COLMAP SfM format.',
            value='',
            uid=[0],
        ),
        desc.File(
            name='databaseFile',
            label='Database file',
            description='''
            The database in COLMAP format. 
            It must contain cameras, images, keypoints and descriptors.''',
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
            description='The algorithm used to extract tentative matches between images',
            value='COLMAP',
            values=['COLMAP'],
            uid=[0],
            exclusive=True,
        ),
        desc.FloatParam(
            name='matchingTreshold',
            label='Matching threshold',
            description='''
            The error threshold for mathces using tracking poses.''',
            value=10,
            range=(0.1, 30, 0.1),
            uid=[0],
        ),  
        desc.BoolParam(
            name="removeImages", 
            label="Remove images",
            description="Remove images from cache after keypoint detection.",
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
            label='Output folder',
            description='',
            value=desc.Node.internalFolder,
            uid=[],
        ),
        desc.File(
            name='databaseOutputFile',
            label='Database file',
            description='',
            value=os.path.join(desc.Node.internalFolder,'database.db'),
            uid=[],
        ),
        desc.File(
            name='tentativeMatches',
            label='Tentative matches',
            description='',
            value=os.path.join(desc.Node.internalFolder,'tentative_matches.txt'),
            uid=[],
        ),
    ]

    def processChunk(self, chunk):
        try:
            chunk.logManager.start(chunk.node.verboseLevel.value)
            
            if not chunk.node.sfmfolder.value:
                chunk.logger.warning('SfM directory is missing.')
                return
            if not chunk.node.databaseFile.value:
                chunk.logger.warning('Database file is missing.')
                return
            if not chunk.node.imagePairs.value:
                chunk.logger.info('Image pairs missing, all pairs will be assumed.')
            if not chunk.node.output.value:
                return

            chunk.logger.info('Start matching.')
            out_dir = chunk.node.output.value
            holo_io = HoloIO()
            holo_io.copy_sfm_images(chunk.node.imagesFolder.value, out_dir)
            if chunk.node.imagePairs:
                copy2(chunk.node.imagePairs.value, out_dir)
                rel_path_to_img_pairs = '/data/' + os.path.basename(chunk.node.imagePairs.value)
            if os.path.isfile(chunk.node.databaseFile.value):
                copy2(chunk.node.databaseFile.value, out_dir)

            # init containers
            chunk.logger.info('Init COLMAP container')
            if sys.platform == 'win32':
                out_dir = out_dir[0].lower() + out_dir[1::]
                colmap_container = UtilsContainers('docker', 'uodcvip/colmap', '/host_mnt/' + out_dir.replace(':',''))
            else:
                colmap_container = UtilsContainers('singularity', dir_path + '/colmap.sif', out_dir)
            colmap = Colmap(colmap_container)
            matcher = UtilsMatcher(chunk.node.algorithm.value, colmap)          # patch2pix / SuperGlue / SIFT

            # colmap matcher
            if not chunk.node.imagePairs.value:
                chunk.logger.info('COLMAP --> exhaustive matching')
                colmap.exhaustive_matcher('/data/database.db')               # COLMAP matcher
            else:
                chunk.logger.info('COLMAP --> exhaustive matching of imported image pairs')
                matcher.update_image_pairs_paths(out_dir + '/' + \
                    os.path.basename(chunk.node.imagePairs.value), replace = ['\\', '/'])
                colmap.custom_matching('/data/database.db', rel_path_to_img_pairs)

            # read the cameras / images
            colmap_io = ColmapIO()
            chunk.logger.info('Loading HoloLens model.')
            cameras, images, points3D = colmap_io.load_model(chunk.node.sfmfolder.value)
            images_db = colmap_io.load_images_from_database(out_dir + '/database.db')
            images = matcher.synchronize_images_ids_with_database(images, images_db)
            
            # run hololens matcher
            chunk.logger.info('Matcher --> run hololens matching')
            obs_for_images, matches = matcher.holo_matcher2(out_dir, cameras, images, 
                database_path = out_dir + '/database.db', err_threshold = chunk.node.matchingTreshold.value)    
            
            chunk.logger.info('Save model into database')
            colmap.prepare_database(out_dir + '/database.db', '/data/database.db')
            images = matcher.update_images_observations(images, obs_for_images)
            colmap_io.insert_cameras_into_database(out_dir + '/database.db', cameras)
            colmap_io.insert_images_into_database(out_dir + '/database.db', images)
            colmap_io.insert_keypoints_into_database(out_dir + '/database.db', images)
            colmap_io.write_tentative_matches_into_file(chunk.node.tentativeMatches.value, images, matches)
            
            # remove images in cache
            if chunk.node.removeImages.value:
                holo_io.remove_images_from_cache(out_dir)

            chunk.logger.info('Matcher done.')
          
        except AssertionError as err:
            chunk.logger.error('Error in keyframe selector: ' + err)
        finally:
            chunk.logManager.end()
