from __future__ import print_function

__version__ = "0.1"

from meshroom.core import desc
import shutil
import glob
import os
import sys
import numpy as np

# import mapper packages
dir_path = __file__
for i in range(6):
    dir_path = os.path.dirname(dir_path)
sys.path.append(dir_path)
from src.holo.HoloIO import HoloIO
from src.utils.UtilsMath import UtilsMath
from src.meshroom.MeshroomIO import MeshroomIO

class DensePonitcloudsAligner(desc.Node):

    category = 'ARTwin'
    documentation = '''
This filter loads two dense pointclouds and merge them into one. 
'''
    # TODO: add more pointcloud to merge and the merging strategy, i.e., the order of merging the pointclouds

    inputs = [
        desc.File(
            name="inputPointcloud1",
            label="Dense pointcloud file",
            description="The path to dense pointcloud in .obj or .ply format",
            value="",
            uid=[0],
        ),
        desc.File(
            name="inputPointcloud2",
            label="Dense pointcloud file",
            description="The path to dense pointcloud in .obj or .ply format",
            value="",
            uid=[0],
        ),
        desc.ChoiceParam(
            name='alignmentMehod',
            label='Alignment method',
            description="Method for aligning the pointclouds.",
            value='concatenation',
            values=['concatenation'], # TODO: R-ICP, Predator, Teaserpp-Magsacpp, ...
            exclusive=True,
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
            name="output",
            label="Output folder",
            description="",
            value=desc.Node.internalFolder + "/model.obj",
            uid=[],
            ),
    ]

    def processChunk(self, chunk):
        try:
            chunk.logManager.start(chunk.node.verboseLevel.value)
            
            if not chunk.node.inputPointcloud1 or not chunk.node.inputPointcloud2:
                chunk.logger.warning('Nothing to process')
                return
            if not chunk.node.output.value:
                return

            holo_io = HoloIO()
            meshroom_io = MeshroomIO()
            utils_math = UtilsMath()

            # load the pointclouds
            chunk.logger.info('Loading dense pointcloud 1.')
            xyz1, rgb1 = meshroom_io.load_vertices(chunk.node.inputPointcloud1.value) 
            chunk.logger.info('Loading dense pointcloud 2.')
            xyz2, rgb2 = meshroom_io.load_vertices(chunk.node.inputPointcloud2.value) 

            # alignment
            common_xyz = np.array((3,0), dtype=float)
            common_rgb = np.array((3,0), dtype=np.uint8)
            if chunk.node.alignmentMehod.value == "concatenation":
                common_xyz = np.concatenate((xyz1, xyz2), axis=1)
                common_rgb = np.concatenate((rgb1, rgb2), axis=1)

            # save the common pointcloud
            chunk.logger.info('Saving filtered pointcloud.')
            holo_io.write_pointcloud_to_file(common_xyz, \
                chunk.node.output.value, rgb = common_rgb)

            chunk.logger.info('Dense poincloud alignment done.') 

        except AssertionError as err:
            chunk.logger.error("Error in keyframe selector: " + err)
        finally:
            chunk.logManager.end()
