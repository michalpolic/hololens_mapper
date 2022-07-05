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

class Matcher(desc.Node):

    category = 'Sparse Reconstruction'
    documentation = '''
This node compute matches between selected / all pairs of images.
'''

    inputs = [
        desc.File(
            name='databaseFile',
            label='Database file',
            description='''
            The database in COLMAP format. 
            It must contain cameras, images and keypoints.''',
            value='',
            uid=[0],
        ),
        desc.ChoiceParam(
            name='inputMatchesFormat',
            label='Input matches format',
            description='''
            Does the "Input matches" contain the tentative matches or 
            the image pairs only.''',
            value='image pairs',
            values=['no data','image pairs','image pairs + tentative matches'],
            uid=[0],
            exclusive=True,
        ),
        desc.File(
            name='inputMatches',
            label='Input matches',
            description='''
            File with image pairs or image pairs + tentative matches.
            This file follow the format required by COLMAP matches_importer 
            in the case of matching raw correspondences.''',
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
            value=2,
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
    ]

    def processChunk(self, chunk):
        try:
            chunk.logManager.start(chunk.node.verboseLevel.value)
            
            if not chunk.node.databaseFile:
                chunk.logger.warning('Database file is missing.')
                return
            if chunk.node.inputMatchesFormat.value == 'no data':
                chunk.logger.warning('Tentative matches are missing. Running exhaustive matching.')
            if not chunk.node.output.value:
                return

            chunk.logger.info('Start matching.')
            out_dir = chunk.node.output.value
            copy2(chunk.node.databaseFile.value, out_dir)
            if chunk.node.inputMatchesFormat.value != "no data":
                copy2(chunk.node.inputMatches.value, out_dir)
                rel_path_tentative_matches = '/data/' + os.path.basename(chunk.node.inputMatches.value)

            # init containers
            chunk.logger.info('Init containers')
            if sys.platform == 'win32':
                out_dir = out_dir[0].lower() + out_dir[1::]
                colmap_container = UtilsContainers('docker', 'uodcvip/colmap', '/host_mnt/' + out_dir.replace(':',''))
            else:
                colmap_container = UtilsContainers('singularity', dir_path + '/colmap.sif', out_dir)
            colmap = Colmap(colmap_container)

            # matcher
            if not chunk.node.inputMatches or chunk.node.inputMatchesFormat.value == 'no data':
                chunk.logger.info('COLMAP --> exhaustive matching')
                colmap.exhaustive_matcher('/data/database.db')               # COLMAP matcher
            else:
                if chunk.node.inputMatchesFormat.value == 'image pairs':
                    chunk.logger.info('COLMAP --> matching of imported image pairs')
                    matcher_type = 'pairs'
                if chunk.node.inputMatchesFormat.value == 'image pairs + tentative matches':
                    chunk.logger.info('COLMAP --> matching of imported tentative matches')
                    matcher_type = 'raw'
                colmap.custom_matching('/data/database.db', rel_path_tentative_matches, \
                    match_type = matcher_type, max_error = chunk.node.matchingTreshold.value)

            chunk.logger.info('Matcher done.')
          
        except AssertionError as err:
            chunk.logger.error('Error in keyframe selector: ' + err)
        finally:
            chunk.logManager.end()
