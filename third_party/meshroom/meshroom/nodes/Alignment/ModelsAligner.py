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
from src.meshroom.MeshroomIO import MeshroomIO

class ModelsAligner(desc.Node):

    category = 'Alignment'
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
            name="ptsTransform",
            label="PTS to transform",
            description="The pointcloud file in format obj or ply.",
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
            name='alignerType',
            label='Transform data',
            description='''Select what data should be transformed.''',
            value=['sfm'],
            values=['pointcloud', 'sfm'],
            exclusive=False,
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
        desc.File(
            name="transforedPts",
            label="Transformed points",
            description="",
            value=os.path.join(desc.Node.internalFolder,'model.obj'),
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

            holo_io = HoloIO()
            meshroom_io = MeshroomIO()
            utils_math = UtilsMath()
            colmap_io = ColmapIO()
            
            chunk.logger.info('Load sfm models.')
            holo_io.copy_all_images(chunk.node.sfmTransform.value, chunk.node.output.value)
            cameras, images, points3D = colmap_io.load_model(chunk.node.sfmTransform.value)
            _, ref_images, _ = colmap_io.load_model(chunk.node.sfmReference.value)

            
            if chunk.node.ptsTransform.value:
                chunk.logger.info('Load dense pointcloud.')
                xyz, rgb = meshroom_io.load_vertices(chunk.node.ptsTransform.value) 


            chunk.logger.info('Find the transformation.')
            transformation = utils_math.estimate_colmap_to_colmap_transformation(ref_images, images)


            if 'sfm' in chunk.node.alignerType.value: 
                chunk.logger.info('Align the models using camera poses.')
                transformed_images = utils_math.transform_colmap_images(images, transformation)
                transformed_points3D = utils_math.transform_colmap_points(points3D, transformation)

                chunk.logger.info('Simplify the reconstruction for Patchmatch.')
                cameras, transformed_images = utils_math.update_camera_ids(cameras, transformed_images)
                
                chunk.logger.info('Save transformed model.')
                colmap_io.write_model(chunk.node.output.value, cameras, transformed_images, transformed_points3D)


            if 'pointcloud' in chunk.node.alignerType.value and chunk.node.ptsTransform.value:
                chunk.logger.info('Transform the pointcloud.')
                transformed_xyz = utils_math.transform_pointcloud(xyz, transformation)
                chunk.logger.info('Saving transformed pointcloud.')
                holo_io.write_pointcloud_to_file(transformed_xyz, chunk.node.transforedPts.value, rgb = rgb)
            
            chunk.logger.info('Aligner done.')
          
        except AssertionError as err:
            chunk.logger.error("Error in keyframe selector: " + err)
        finally:
            chunk.logManager.end()
