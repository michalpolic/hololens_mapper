from __future__ import print_function

__version__ = "0.1"

from meshroom.core import desc
import shutil
import glob
import os
import sys
import numpy as np
import enum

# import mapper packages
dir_path = __file__
for i in range(6):
    dir_path = os.path.dirname(dir_path)
sys.path.append(dir_path)
from src.holo.HoloIO import HoloIO
from src.utils.UtilsMath import UtilsMath
from src.meshroom.MeshroomIO import MeshroomIO
from src.utils.UtilsContainers import UtilsContainers

class DensePonitcloudsConcatenator(desc.Node):

    category = 'Alignment'
    documentation = '''Loads two dense pointclouds and merge them into one.'''

    inputs = [
        desc.File(
            name="pointcloud1",
            label="Pointcloud 1",
            description="Path to the first point cloud",
            value="",
            uid=[0],
        ),
        desc.File(
            name="pointcloud2",
            label="Pointcloud 2",
            description="Path to the second point cloud",
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
            value=desc.Node.internalFolder + "/model.obj",
            uid=[],
            ),
    ]

    def concatenate(self, chunk, holo_io, meshroom_io, outfile, pc1, pc2):
        # load the pointclouds
        chunk.logger.info('Loading dense point cloud 1.')
        xyz1, rgb1 = meshroom_io.load_vertices(pc1) 
        chunk.logger.info('Loading dense point cloud 2.')
        xyz2, rgb2 = meshroom_io.load_vertices(pc2) 
        
        # alignment
        common_xyz = np.concatenate((xyz1, xyz2), axis=1)
        common_rgb = np.concatenate((rgb1, rgb2), axis=1)

        # save the common pointcloud
        chunk.logger.info('Saving mergerd point cloud.')
        holo_io.write_pointcloud_to_file(common_xyz, \
            outfile, rgb = common_rgb)
        
    
    def processChunk(self, chunk):
        try:
            chunk.logManager.start(chunk.node.verboseLevel.value)
            
            if not chunk.node.pointcloud1.value:
                chunk.logger.warning('Nothing to process')
                return
            if not chunk.node.pointcloud2.value:
                chunk.logger.warning('Nothing to process')
                return

            holo_io = HoloIO()
            meshroom_io = MeshroomIO()
            outfile = chunk.node.output.value
            self.concatenate(chunk, holo_io, meshroom_io, outfile, \
                chunk.node.pointcloud1.value, chunk.node.pointcloud2.value)

            chunk.logger.info('Dense pointcloud concatenation done.') 

        except AssertionError as err:
            chunk.logger.error("Error in keyframe selector: " + err)
        finally:
            chunk.logManager.end()
