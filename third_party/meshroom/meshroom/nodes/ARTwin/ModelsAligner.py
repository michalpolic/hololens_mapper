from __future__ import print_function

__version__ = "0.1"

from meshroom.core import desc
import shutil
import glob
import os
import sys
from pathlib import Path

# import mapper packages
dir_path = __file__
for i in range(6):
    dir_path = os.path.dirname(dir_path)
sys.path.append(dir_path)
from src.holo.HoloIO import HoloIO
from src.colmap.ColmapIO import ColmapIO
from src.utils.UtilsMath import UtilsMath

class ModelsAligner(desc.Node):

    category = 'ARTwin'
    documentation = '''
This node COLMAP mapper on database which contains matches.
'''

    inputs = [
        desc.File(
            name="sfmTransform",
            label="SfM to transform",
            description="The directory containing COLMAP SfM output.",
            value="",
            uid=[0],
        ),
        desc.File(
            name="sfmReference",
            label="Reference SfM",
            description="The directory containing COLMAP SfM output.",
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
            label="Output Folder",
            description="",
            value=desc.Node.internalFolder,
            uid=[],
            ),
        ]

    def processChunk(self, chunk):
        try:
            chunk.logManager.start(chunk.node.verboseLevel.value)
            
            if not chunk.node.sfmTransform:
                chunk.logger.warning('Transformed SfM directory is missing.')
                return
            if not chunk.node.sfmReference:
                chunk.logger.warning('Reference SfM directory is missing.')
                return
            if not chunk.node.output.value:
                return

            # copy required resources
            holo_io = HoloIO()
            holo_io.copy_sfm_images(chunk.node.sfmTransform.value, chunk.node.output.value)
            
            # load models
            colmap_io = ColmapIO()
            cameras, images, points3D = colmap_io.load_model(chunk.node.sfmTransform.value)
            _, ref_images, _ = colmap_io.load_model(chunk.node.sfmReference.value)

            # align the models using camera poses
            utils_math = UtilsMath()
            transformation = utils_math.estimate_colmap_to_colmap_transformation(ref_images, images)
            transformed_images = utils_math.transform_colmap_images(images, transformation)
            transformed_points3D = utils_math.transform_colmap_points(points3D, transformation)

            # save transformed model
            colmap_io.write_model(chunk.node.output.value, cameras, transformed_images, transformed_points3D)

            chunk.logger.info('Aligner done.')
          
        except AssertionError as err:
            chunk.logger.error("Error in keyframe selector: " + err)
        finally:
            chunk.logManager.end()
