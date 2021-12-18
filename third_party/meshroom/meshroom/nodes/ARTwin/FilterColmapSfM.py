from __future__ import print_function

__version__ = "0.1"

from meshroom.core import desc
import os
import sys
import numpy as np

# import mapper packages
dir_path = __file__
for i in range(6):
    dir_path = os.path.dirname(dir_path)
sys.path.append(dir_path)
from src.holo.HoloIO import HoloIO
from src.colmap.Colmap import Colmap
from src.colmap.ColmapIO import ColmapIO



class FilterColmapSfM(desc.Node):
    category = "ARTwin"
    documentation = """
This node load SfM structures and remove images which you select. 
"""

    inputs = [
        desc.File(
            name="inputFolder",
            label="Input Folder",
            description="COLMAP SfM (cameras.txt, images.txt, points3D.thx) "
                "or HoloLens recording directory (images in pv/*.jpg, "
                "depth in long_throw_depth/*.pgm, etc. + related .csv).",
            value="",
            uid=[0]
        ),
        desc.BoolParam(
            name="subsamplePoints3D", 
            label="Subsample points 3D",
            description="If this option is true, we assume just a random subset of "
                "'Number of points in 3D' for the filtering the images.",
            value=False, 
            uid=[0]
        ),
        desc.IntParam(
            name="numberOfPoints3D", 
            label="Number of points in 3D", 
            description="Number of points used for filtering the images.", 
            value=1000, 
            uid=[0], 
            range=(100, 1000000, 100),
        ),
        desc.IntParam(
            name="minNumberOfObservations", 
            label="Min. number of observations", 
            description="This value is used for filtering of points in 3D. "
                "A random point in 3D is removed only if there remain this "
                "number of observations in images.", 
            value=50, 
            uid=[0], 
            range=(3, 1000, 1),
        ),
        desc.BoolParam(
            name="filterPV", 
            label="Filter PV",
            description="If this option is true, all pv images and related "
                "structures (observations and points in 3D) will be removed from the model.",
            value=False, 
            uid=[0]
        ),
        desc.BoolParam(
            name="filterVLC", 
            label="Filter VLS",
            description="If this option is true, all tracking images and related "
                "structures (observations and points in 3D) will be removed from the model.",
            value=False, 
            uid=[0]
        ),
        desc.BoolParam(
            name="cpoyImagesToOutput", 
            label="Copy images to output",
            description="If True, the images are copied into the output directory.",
            value=False, 
            uid=[0]
        ),
        desc.ChoiceParam(
            name="verboseLevel",
            label="Verbose Level",
            description="verbosity level (critical, error, warning, info, debug).",
            value="info",
            values=["critical", "error", "warning", "info", "debug"],
            exclusive=True,
            uid=[],
        )
    ]

    outputs = [
        desc.File(
            name="output",
            label="Output Folder",
            description="Folder with SfM files.",
            value=desc.Node.internalFolder,
            uid=[],
        ),
    ]


    def processChunk(self, chunk):
        try:
            chunk.logManager.start(chunk.node.verboseLevel.value)
            
            if not chunk.node.inputFolder:
                chunk.logger.warning("Nothing to process")
                return
            if not chunk.node.output.value:
                return

            # init nescessary classes
            colmap = Colmap()
            colmap_io = ColmapIO()
            holo_io = HoloIO()

            # inputs 
            cameras, images, points3D = colmap_io.load_model(chunk.node.inputFolder.value)

            # update colmap structures
            if chunk.node.subsamplePoints3D.value:
                images, points3D = colmap.select_subset_of_points3D(chunk.node.numberOfPoints3D.value, \
                    chunk.node.minNumberOfObservations.value, images, points3D)

            if chunk.node.filterPV.value:
                chunk.logger.info("Removing PV images")
                images, points3D = colmap.remove_images_from_model('pv', images, points3D)

            if chunk.node.filterVLC.value:
                chunk.logger.info("Removing VLC images")
                images, points3D = colmap.remove_images_from_model('vlc_', images, points3D)

            # output structures
            if chunk.node.cpoyImagesToOutput.value:
                holo_io.copy_sfm_images(chunk.node.inputFolder.value, chunk.node.output.value)

            chunk.logger.info("Saving COLMAP SfM.")
            colmap_io.write_model(chunk.node.output.value, cameras, images, points3D)

            chunk.logger.info("FilterColmapSfM done.") 

        except AssertionError as err:
            chunk.logger.error("Error in keyframe selector: " + err)
        finally:
            chunk.logManager.end()
