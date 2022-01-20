from __future__ import print_function

__version__ = "0.1"

from meshroom.core import desc
import shutil
import glob
import os
import os.path 
import sys
from pathlib import Path
from shutil import copy2

# import mapper packages
dir_path = __file__
for i in range(6):
    dir_path = os.path.dirname(dir_path)
sys.path.append(dir_path)
from src.colmap.Colmap import Colmap
from src.holo.HoloIO import HoloIO
from src.utils.UtilsContainers import UtilsContainers

class Patchmatchnet(desc.Node):

    category = 'ARTwin'
    documentation = '''
This node prepare inputs for PatchmatchNet and run it. The output are depthmaps and 
fused pointcloud file.
'''

    inputs = [
        desc.File(
            name="colmapFolder",
            label="Colmap folder",
            description="The directory containing colmap SfM files in txt format and image direcories.",
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
        desc.File(
            name="outputPLY",
            label="Output pointcloud",
            description="",
            value=desc.Node.internalFolder + "/fused.ply",
            uid=[],
            ),
        ]

    def processChunk(self, chunk):
        try:
            chunk.logManager.start(chunk.node.verboseLevel.value)
            
            if not chunk.node.colmapFolder:
                chunk.logger.warning('COLMAP directory is missing.')
                return
            if not chunk.node.output.value:
                return

            # copy required resources
            out_dir = chunk.node.output.value
            holo_io = HoloIO()
            holo_io.copy_sfm_images(chunk.node.colmapFolder.value, out_dir)
            copy2(chunk.node.colmapFolder.value + '/cameras.txt', out_dir)
            copy2(chunk.node.colmapFolder.value + '/images.txt', out_dir)
            copy2(chunk.node.colmapFolder.value + '/points3D.txt', out_dir)

            # run standard matching
            chunk.logger.info('Init COLMAP container')
            if sys.platform == 'win32':
                out_dir = out_dir[0].lower() + out_dir[1::]
                colmap_container = UtilsContainers("docker", "uodcvip/colmap", "/host_mnt/" + out_dir.replace(":",""))
                patchmatchnet_container = UtilsContainers("docker", "patchmatchnet", "/host_mnt/" + out_dir.replace(":",""))
            else:
                colmap_container = UtilsContainers("singularity", dir_path + "/colmap.sif", out_dir)
                patchmatchnet_container = UtilsContainers("singularity", dir_path + "/patchmatchnet.sif", out_dir)
            colmap = Colmap(colmap_container)
            
            # init COLMAP dense reconstruction folders and files
            Path(chunk.node.output.value + "/dense/sparse").mkdir(parents=True, exist_ok=True)
            Path(chunk.node.output.value + "/dense/images").mkdir(parents=True, exist_ok=True)
            colmap.model_converter("/data", "/data/dense/sparse", "BIN")
            colmap.images_undistortion("/data", "/data/dense/sparse", "/data/dense")

            # transform the COLMAP dense structures to PatchmatchNet input format
            patchmatchnet_container.command_dict("python3 /app/colmap_input.py", 
                {"input_folder": "/data/dense"})

            # run PatchmatchNet
            patchmatchnet_container.command_dict("python3 /app/eval.py", 
                {"input_folder": "/data/dense", 
                "output_folder": "/data",
                "checkpoint_path": "/app/checkpoints/params_000007.ckpt",
                "num_views": 7,
                "image_max_dim": 2048,
                "geo_mask_thres": 5,
                "photo_thres": 0.8
                })
            
            chunk.logger.info('Patchmatchnet done.')
          
        except AssertionError as err:
            chunk.logger.error("Error in patchmatchnet: " + err)
        finally:
            chunk.logManager.end()
