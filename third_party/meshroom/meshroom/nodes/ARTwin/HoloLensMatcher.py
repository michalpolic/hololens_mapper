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
from src.holo.HoloIO import HoloIO
from src.colmap.ColmapIO import ColmapIO
from src.colmap.Colmap import Colmap
from src.utils.UtilsContainers import UtilsContainers
from src.utils.UtilsMatcher import UtilsMatcher

class HoloLensMatcher(desc.Node):

    category = 'ARTwin'
    documentation = '''
This node compute matches between all pairs of HoloLens rgb images.
'''

    inputs = [
        desc.File(
            name="colmapSfM",
            label="Colmap SfM",
            description="The directory containing input camera poses " \
                "saved in COLMAP SfM format.",
            value="",
            uid=[0],
        ),
        desc.File(
            name="imagesFolder",
            label="Directory with images",
            description="The directory containing input images in /pv and /vlc_* folders",
            value="",
            uid=[0],
        ),
        desc.File(
            name="imagePairs",
            label="Image pairs to match",
            description="File with image names to match. " \
                "Each image pair is on one line, e.g. img1 img2.",
            value="",
            uid=[0],
        ),
        desc.ChoiceParam(
            name="algorithm",
            label="Matching algorithm",
            description="The algorithm used to extract matches between images",
            value='SIFT',
            values=['SIFT'], #, 'SuperGlue', 'patch2pix'],
            uid=[0],
            exclusive=True,
            ),
        desc.IntParam(
            name='clusteringRadius',
            label='Clustering radius',
            description='The radius for clustering the observations (Patch2Pix).',
            value=1,
            range=(1, 10, 1),
            uid=[0],
            ),  
        desc.FloatParam(
            name='matchingTreshold',
            label='Matching threshold',
            description='The reprojection threshold for mathces verification using the HoloLens tracking poses.',
            value=10,
            range=(0.1, 30, 0.1),
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
            
            if not chunk.node.colmapSfM:
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
            holo_io.copy_sfm_images(chunk.node.imagesFolder.value, out_dir)

            if chunk.node.imagePairs:
                copy2(chunk.node.imagePairs.value, out_dir)
                rel_path_to_img_pairs = '/data/' + os.path.basename(chunk.node.imagePairs.value)

            # run standard matching
            chunk.logger.info('Init COLMAP container')
            if sys.platform == 'win32':
                out_dir = out_dir[0].lower() + out_dir[1::]
                colmap_container = UtilsContainers("docker", "uodcvip/colmap", "/host_mnt/" + out_dir.replace(":",""))
            else:
                colmap_container = UtilsContainers("singularity", dir_path + "/colmap.sif", out_dir)
            colmap = Colmap(colmap_container)
            matcher = UtilsMatcher(chunk.node.algorithm.value, colmap)          # patch2pix / SuperGlue / SIFT

            # colmap matches_importer --help
            if matcher._matcher_name == "SIFT":
                chunk.logger.info('COLMAP --> compute SIFT features')
                colmap.prepare_database(out_dir + "/database.db", "/data/database.db")
                colmap.extract_features("/data/database.db", "/data")           # COLMAP feature extractor
                if not chunk.node.imagePairs.value:
                    chunk.logger.info('COLMAP --> exhaustive matching')
                    colmap.exhaustive_matcher("/data/database.db")               # COLMAP matcher
                else:
                    chunk.logger.info('COLMAP --> exhaustive matching of imported image pairs')
                    matcher.update_image_pairs_paths(out_dir + '/' + \
                        os.path.basename(chunk.node.imagePairs.value), replace = ['\\', '/'])
                    colmap.custom_matching("/data/database.db", rel_path_to_img_pairs)

            # read the cameras / images
            colmap_io = ColmapIO()
            chunk.logger.info("Loading HoloLens model.")
            cameras, images, points3D = colmap_io.load_model(chunk.node.colmapSfM.value)
            images_db = colmap_io.load_images_from_database(out_dir + "/database.db")
            images = matcher.synchronize_images_ids_with_database(images, images_db)
            
            # run hololens matcher
            chunk.logger.info('Matcher --> run hololens matching')
            obs_for_images, matches = matcher.holo_matcher2(out_dir, cameras, images, 
                database_path = out_dir + "/database.db", err_threshold = chunk.node.matchingTreshold.value)    
            
            chunk.logger.info('Save model into database')
            colmap.prepare_database(out_dir + "/database.db", '/data/database.db')
            images = matcher.update_images_observations(images, obs_for_images)
            colmap_io.write_model_into_database(out_dir, "/database.db", cameras, images, matches)
            
            chunk.logger.info('Matcher done.')
          
        except AssertionError as err:
            chunk.logger.error("Error in keyframe selector: " + err)
        finally:
            chunk.logManager.end()
