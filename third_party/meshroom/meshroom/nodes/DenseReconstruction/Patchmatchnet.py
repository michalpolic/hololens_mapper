from __future__ import print_function

__version__ = "0.1"

from meshroom.core import desc
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

    category = 'Dense Reconstruction'
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
        desc.IntParam(
            name='numViews', 
            label='Number of neighbouring views', 
            description='The number of assumed neighbouring views in PatchmatchNet.', 
            value=7, 
            uid=[0], 
            range=(3, 30, 1),
        ),
        desc.IntParam(
            name='imageMaxDim', 
            label='Max. image dimension', 
            description='The maximal dimension of image edges.', 
            value=2048, 
            uid=[0], 
            range=(256, 4096, 1),
        ),
        desc.IntParam(
            name='geoMaskThres', 
            label='Geometric mask threshold', 
            description='The threshold for geometric consistency filtering. More details in PatchmatchNet paper.', 
            value=5, 
            uid=[0], 
            range=(1, 20, 1),
        ),
        desc.FloatParam(
            name='photoThres', 
            label='Photometric consistency threshold', 
            description='The threshold for photometric consistency filtering. More details in PatchmatchNet paper.', 
            value=0.8, 
            uid=[0], 
            range=(0.01, 1, 0.01),
        ),
        desc.FloatParam(
            name='geoPixelThres', 
            label='Geometric pixel threshold', 
            description='The pixel threshold for geometric consistency filtering. More details in PatchmatchNet paper.', 
            value=1.0, 
            uid=[0], 
            range=(0.1, 10, 0.1),
        ),
        desc.FloatParam(
            name='geoDepthThres', 
            label='Geometric depth threshold', 
            description='The depth threshold for geometric consistency filtering. More details in PatchmatchNet paper.', 
            value=0.01, 
            uid=[0], 
            range=(0.001, 1, 0.001),
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
            holo_io.copy_all_images(chunk.node.colmapFolder.value, out_dir)
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
                "num_views": chunk.node.numViews.value,
                "image_max_dim": chunk.node.imageMaxDim.value,
                "geo_mask_thres": chunk.node.geoMaskThres.value,
                "photo_thres": chunk.node.photoThres.value,
                "geo_pixel_thres": chunk.node.geoPixelThres.value,
                "geo_depth_thres": chunk.node.geoDepthThres.value
                })

            chunk.logger.info('Patchmatchnet done.')
          
        except AssertionError as err:
            chunk.logger.error("Error in patchmatchnet: " + err)
        finally:
            chunk.logManager.end()
