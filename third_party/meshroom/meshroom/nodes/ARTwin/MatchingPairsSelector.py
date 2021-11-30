from __future__ import print_function

from src import colmap

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
from src.colmap.ColmapIO import ColmapIO
from src.utils.UtilsMath import UtilsMath

class MatchingPairsSelector(desc.Node):
    category = "ARTwin"
    documentation = """
This node select image pairs looking at the same 3D structure, i.e., images with specified overlap. 
"""

    inputs = [
        desc.File(
            name="sfmFile",
            label="SfM file(s)",
            description="The output of SfM or any course composition of SfM output.",
            value="",
            uid=[0],
        ),
        desc.ChoiceParam(
            name="inputSfMFormat",
            label="Input format",
            description="The input data format, e.g., COLMAP or Meshroom.",
            value="COLMAP",
            values=["COLMAP"],  #, "Meshroom"
            exclusive=True,
            uid=[],
            ),
        desc.ChoiceParam(
            name="outputSfMFormat",
            label="Output format",
            description="The output data format, e.g., COLMAP or Meshroom.",
            value="COLMAP",
            values=["COLMAP"],  #, "Meshroom"
            exclusive=True,
            uid=[0],
        ),
        desc.IntParam(
            name='minCommonPts',
            label='Min. common points',
            description='Min. number of common points between image pair ' + \
                'to report the image pair.',
            value=200,
            range=(1, 10000, 10),
            uid=[0],
        ),
        desc.ChoiceParam(
            name="verboseLevel",
            label="Verbose Level",
            description="verbosity level (critical, error, warning, info, debug).",
            value="info",
            values=["critical", "error", "warning", "info", "debug"],
            exclusive=True,
            uid=[],
            ),
    ]

    outputs = [
        desc.File(
            name="output",
            label="Output Folder",
            description="",
            value=desc.Node.internalFolder + "/image_pairs.txt",
            uid=[],
            ),
    ]


    def processChunk(self, chunk):
        try:
            chunk.logManager.start(chunk.node.verboseLevel.value)
            
            if not chunk.node.sfmFile:
                chunk.logger.warning("Nothing to process")
                return
            if not chunk.node.output.value:
                return

            # TODO: implement other formats loading and saving (e.g., Meshroom) 

            # load HoloLens from CSV files
            colmap_io = ColmapIO()
            chunk.logger.info("Loading SfM model.")
            cameras, images, points3D = colmap_io.load_model(chunk.node.sfmFile.value)

            # get view graph
            utils_math = UtilsMath()
            images_to_ids, view_graph = utils_math.get_view_graph(images, points3D)

            # save the image pairs with more than defined number of points
            colmap_io.save_image_pairs(chunk.node.output.value, images, \
                view_graph, chunk.node.minCommonPts.value)

            chunk.logger.info("Image pairs exported.") 

        except AssertionError as err:
            chunk.logger.error("Error in keyframe selector: " + err)
        finally:
            chunk.logManager.end()
