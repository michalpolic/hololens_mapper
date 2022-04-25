from __future__ import print_function

from src.holo.HoloIO import HoloIO

__version__ = "0.1"

from meshroom.core import desc
import shutil
import os
import shutil
import sys
from pathlib import Path

# import mapper packages
dir_path = __file__
for i in range(6):
    dir_path = os.path.dirname(dir_path)
sys.path.append(dir_path)
from src.utils.UtilsContainers import UtilsContainers
from src.utils.UtilsMath import UtilsMath
from src.colmap.ColmapIO import ColmapIO
from src.holo.HoloIO import HoloIO
from src.hloc.Hloc import Hloc

class HlocLocalizer(desc.Node):

    category = 'Localization'
    documentation = '''
Runs Hloc localization on input images.
                    
'''

    inputs = [
        desc.File(
            name="queryFile",
            label="Query file path",
            description="Path to Hloc query file (.txt)",
            value="",
            uid=[0],
        ),
        desc.File(
            name="hlocMapDir",
            label="Hloc Map directory",
            description="Hloc map directory (database, images, features)",
            value="",
            uid=[0],
        ),
        desc.File(
            name="localSfM",
            label="SfM folder",
            description="Path to folder with images and local SfM.",
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
            value=desc.Node.internalFolder,
            uid=[],
        ),
        desc.File(
            name="image_pairs",
            label="Image Pairs",
            description="",
            value=os.path.join(desc.Node.internalFolder,'image_pairs.txt'),
            uid=[],
        ),
        desc.File(
            name="localization",
            label="Localization results",
            description="",
            value=os.path.join(desc.Node.internalFolder,'query_localization_results.txt'),
            uid=[],
        ),
    ]

    def copy_map_images(self, images, map_folder, output_folder):
        for img in images.values():
            new_img_path = os.path.join(output_folder, img['name'])
            Path(new_img_path).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(os.path.join(map_folder,img['name']), new_img_path)


    def processChunk(self, chunk):
        try:
            chunk.logManager.start(chunk.node.verboseLevel.value)
            output_folder = chunk.node.output.value
            map_folder = chunk.node.hlocMapDir.value
            query_file = chunk.node.queryFile.value

            if not map_folder:
                chunk.logger.warning('Nothing to process, Hloc map required')
                return
            if not query_file:
                chunk.logger.warning('Nothing to process, query file required')
                return

            if output_folder[-1] != '/':
                output_folder = output_folder + '/'
            if map_folder[-1] != '/':
                map_folder = map_folder + '/'

            # localize the images
            hloc_container = UtilsContainers("singularity", dir_path + "/hloc.sif", './third_party/Hierarchical-Localization/')
            chunk.logger.info('Running Hloc Localization.')   
            hloc_container.command("python3 ./third_party/Hierarchical-Localization/run_hloc.py " + map_folder + " " + query_file + " " + output_folder)

            # copy used map images into common directories
            colmap_io = ColmapIO()
            db_cameras, db_images, db_points3D = colmap_io.load_model(output_folder)
            self.copy_map_images(db_images, map_folder, output_folder)

            # copy local sfm images
            if chunk.node.localSfM.value:
                holo_io = HoloIO()
                holo_io.copy_sfm_images(chunk.node.localSfM.value, output_folder)
                
                # update the local sfm
                um = UtilsMath()
                hloc = Hloc()
                q_cameras, q_images, q_points3D = colmap_io.load_model(chunk.node.localSfM.value)
                loc_images = hloc.get_imgs_from_localization_results(chunk.node.localization.value)
                cameras, images, points3D = um.align_local_and_global_sfm(db_cameras, db_images, db_points3D, \
                    q_cameras, q_images, q_points3D, loc_images)
                colmap_io.write_model(output_folder, cameras, images, points3D)

            chunk.logger.info('Localization done.') 

        except AssertionError as err:
            chunk.logger.error("Error in hlocLocalizer selector: " + err)
        finally:
            chunk.logManager.end()
