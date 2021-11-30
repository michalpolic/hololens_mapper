from __future__ import print_function

__version__ = "0.1"

from meshroom.core import desc
import shutil
import glob
import os
import sys
from pathlib import Path
from distutils.dir_util import copy_tree

# import mapper packages
dir_path = __file__
for i in range(6):
    dir_path = os.path.dirname(dir_path)
sys.path.append(dir_path)
from src.holo.HoloIO import HoloIO
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
            name="input",
            label="Recording directory",
            description="The directory containing input images in /pv folder",
            value="",
            uid=[0],
        ),
        desc.ChoiceParam(
            name="algorithm",
            label="Matching algorithm",
            description="The algorithm used to extract matches between images",
            value='SIFT',
            values=['SIFT', 'SuperGlue', 'patch2pix'],
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
            
            if not chunk.node.input:
                chunk.logger.warning('Nothing to process')
                return
            if not chunk.node.output.value:
                return

            # 1) read the cameras 
            chunk.logger.info('Read camera info.')
            holo_io = HoloIO()
            holo_cameras = holo_io.read_hololens_csv(chunk.node.input.value + "/pv.csv")

            # 2) run matching
            chunk.logger.info('Start matching.')
            out_dir = chunk.node.output.value
            Path(out_dir + "/colmap/sparse").mkdir(parents=True, exist_ok=True)
            copy_tree(chunk.node.input.value, out_dir)

            chunk.logger.info('Init COLMAP container')
            if sys.platform == 'win32':
                colmap_container = UtilsContainers("docker", "uodcvip/colmap", "/data/" + out_dir.replace(":",""))
            else:
                colmap_container = UtilsContainers("singularity", dir_path + "/colmap.sif", out_dir)
            colmap = Colmap(colmap_container)
            matcher = UtilsMatcher(chunk.node.algorithm.value, colmap)      # patch2pix / SuperGlue / SIFT
            
            # colmap matches_importer --help
            if matcher._matcher_name == "SIFT":
                chunk.logger.info('COLMAP --> compute SIFT features')
                colmap.extract_features("/data/colmap/database.db", "/data/pv")     # COLMAP feature extractor
                chunk.logger.info('COLMAP --> exhaustive matching')
                colmap.exhaustive_matcher("/data/colmap/database.db")               # COLMAP matcher

            chunk.logger.info('Matcher --> run hololens matching')
            obs_for_images, matches = matcher.holo_matcher(out_dir + "/pv", holo_cameras, 
                database_path = out_dir + "/colmap/database.db", radius = chunk.node.clusteringRadius.value, 
                err_threshold = chunk.node.matchingTreshold.value)    
            
            chunk.logger.info('Save matches into database')
            colmap.save_matches_into_database(out_dir, "/colmap/database.db", 
                holo_cameras, matches, obs_for_images)
            chunk.logger.info('Matches saved into database.')    
          
        except AssertionError as err:
            chunk.logger.error("Error in keyframe selector: " + err)
        finally:
            chunk.logManager.end()
