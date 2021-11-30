from __future__ import print_function

__version__ = "0.1"

from meshroom.core import desc
import shutil
import glob
import os
import sys

# import mapper packages
dir_path = __file__
for i in range(6):
    dir_path = os.path.dirname(dir_path)
sys.path.append(dir_path)
from src.holo.HoloIO import HoloIO
from src.utils.UtilsMath import UtilsMath
from src.meshroom.MeshroomIO import MeshroomIO

class DensePointcloudFilter(desc.Node):

    category = 'ARTwin'
    documentation = '''
This filter noise out of the dense pointcloud. 
'''

    inputs = [
        desc.File(
            name="densePointcloud",
            label="Dense pointcloud file",
            description="The path to dense pointcloud in .obj or .ply format",
            value="",
            uid=[0],
        ),
        desc.FloatParam(
            name='neighbourDistance',
            label='Neighbours distance [m]',
            description="The distance in which are points assumed as neighbours.",
            value=0.05,
            range=(0.005, 0.5, 0.005),
            uid=[0],
            ),
        desc.IntParam(
            name='minNeighbours',
            label='Min. neighbours',
            description='Points with smaller number of neighbours are filtered out.',
            value=50,
            range=(1, 500, 1),
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

    def processChunk(self, chunk):
        try:
            chunk.logManager.start(chunk.node.verboseLevel.value)
            
            if not chunk.node.densePointcloud:
                chunk.logger.warning('Nothing to process')
                return
            if not chunk.node.output.value:
                return

            holo_io = HoloIO()
            meshroom_io = MeshroomIO()
            utils_math = UtilsMath()

            chunk.logger.info('Loading dense pointcloud.')
            xyz, rgb = meshroom_io.load_vertices(chunk.node.densePointcloud.value) 
            is_pointcloud_loaded = True

            assert is_pointcloud_loaded, 'Failed to load dense pointcloud.'

            chunk.logger.info('Filtering dnese pointcloud.')
            xyz_fitered, rgb_filterd = utils_math.filter_dense_pointcloud_noise_KDtree(xyz, \
                chunk.node.neighbourDistance.value, chunk.node.minNeighbours.value, rgb = rgb)
            
            chunk.logger.info('Saving filtered pointcloud.')
            holo_io.write_pointcloud_to_file(xyz_fitered, \
                chunk.node.output.value, rgb = rgb_filterd)

            chunk.logger.info('Dense poincloud filtering is done.') 

        except AssertionError as err:
            chunk.logger.error("Error in keyframe selector: " + err)
        finally:
            chunk.logManager.end()
