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
from src.meshroom.MeshroomIO import MeshroomIO
from src.colmap.Colmap import Colmap
from src.colmap.ColmapIO import ColmapIO
from src.utils.UtilsMath import UtilsMath

Intrinsic = [
    desc.IntParam(name="intrinsicId", label="Id", description="Intrinsic UID", value=-1, uid=[0], range=None),
    desc.ListAttribute(
            name="csvPrefixes",
            elementDesc=desc.StringParam(name="csvPrefix", label="CSV prefix", description="The name of csv and images dir, e.g. pv for pv.csv.", value="", uid=[]),
            label="CSV prefixes",
            description="The name of csv and images dir, e.g. pv for pv.csv. List of names if we have common intrinsics for set of cameras.",
        ),
    desc.IntParam(name="width", label="Width", description="Image Width", value=0, uid=[0], range=(0, 10000, 1)),
    desc.IntParam(name="height", label="Height", description="Image Height", value=0, uid=[0], range=(0, 10000, 1)),
    desc.GroupAttribute(name="pxFocalLength", label="Focal Length", description="Focal Length (in pixels).", groupDesc=[
        desc.FloatParam(name="x", label="x", description="", value=0, uid=[0], range=None),
        desc.FloatParam(name="y", label="y", description="", value=0, uid=[0], range=None),
        ]),
    desc.GroupAttribute(name="principalPoint", label="Principal Point", description="Position of the Optical Center in the Image (i.e. the sensor surface).", groupDesc=[
        desc.FloatParam(name="x", label="x", description="", value=0, uid=[0], range=(0, 10000, 1)),
        desc.FloatParam(name="y", label="y", description="", value=0, uid=[0], range=(0, 10000, 1)),
        ]),
    desc.ListAttribute(
            name="distortionParams",
            elementDesc=desc.FloatParam(name="p", label="", description="", value=0.0, uid=[0], range=(-0.1, 0.1, 0.01)),
            label="Distortion Params",
            description="Distortion Parameters",
        ),
]

class HoloLensIO(desc.Node):
    size = desc.DynamicNodeSize("intrinsics")
    category = "ARTwin"
    documentation = """
This transforms the input HoloLens recording into different data format, e.g., COLMAP or Meshroom. 
The code does not compute visibility of individual 3D points. It only transform available data into
different format.
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
        desc.File(
            name="pointcloudFile",
            label="Dense pointcloud file",
            description="Dense pointcloud from HoloLens depthmaps in the "
                "same coordinate system as the camera poses. Format .obj or .ply.",
            value="",
            uid=[0],
        ),
        desc.IntParam(
            name="hashScale", 
            label="Points hash scale", 
            description="Points hash scale is an multiple of original pointcloud. " 
                "The pointcloud will be sparser with given distace between two neighbouring points."  
                "For example, if the pointcloud is in meters, scale 100 creates an " 
                "hashed point cloud in centimeters grid before projection to images.", 
            value=1, 
            uid=[0], 
            range=(1, 10000, 1),
        ),
        desc.BoolParam(
            name="allPoints", 
            label="Estimate visibility for all points",
            description="If this option is true, all the points will be at the output while visibility " 
                "will be estimated only by hashed points. If false, at the output will be mean points of "
                "the clustered points into the cells by hashing. The hashing can be disabled by seting "
                "hash scale to negative value.",
            value=False, 
            uid=[0]
        ),
        desc.ListAttribute(
            name="intrinsics",
            elementDesc=desc.GroupAttribute(name="intrinsic", label="Intrinsic", description="", groupDesc=Intrinsic),
            label="Camera parameters",
            description="Camera Intrinsics",
            group="",
        ),
        desc.ChoiceParam(
            name="inputSfMFormat",
            label="Input format",
            description="The input data format, e.g., COLMAP or HoloLens recording.",
            value="HoloLens",
            values=["COLMAP", "HoloLens"],   # , "Meshroom"
            exclusive=True,
            uid=[0],
        ),
        desc.ChoiceParam(
            name="outputSfMFormat",
            label="Output format",
            description="The output data format, e.g., COLMAP or Meshroom.",
            value="COLMAP",
            values=["COLMAP", "Meshroom","OBJ"], 
            exclusive=False,
            uid=[0],
        ),
        desc.BoolParam(
            name="cpoyImagesToOutput", 
            label="Copy images to output",
            description="If True, the images are copied into the output directory.",
            value=False, 
            uid=[0]
        ),
        desc.ChoiceParam(
            name="imagesPath", 
            label="Images path",
            description="If container, the path to images is set relatively from Cache folder "
                "with '/data' prefix, e.g. /home/<some_path>/MeshroomCache/abcdefg/pv/01.jpg will be "
                "/data/abcdefg/pv/01.jpg. Such a format can be used in containers with mounted "
                "cached folder. If absolute, the path will be absolute path to images. If original, "
                "the paths should be in the same format as at the input (usualy, e.g., pv/01.jpg or vlc_ll/99.jpg)",
            value="original",
            values=["original", "absolute", "container"], 
            exclusive=True,
            advanced=True,
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
        desc.File(
            name="outputMeshroomSfM",
            label="Meshroom SfM file",
            description="Link to Meshroom SfM if conversion is to Meshroom format.",
            value=desc.Node.internalFolder + "meshroom_sfm.json",
            uid=[],
            group='',
            advanced=True
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
            meshroom_io = MeshroomIO() 
            utils_math = UtilsMath()

            # inputs 
            if chunk.node.inputSfMFormat.value == "HoloLens":
                chunk.logger.info("Loading intrinsics.")
                intrinsics = chunk.node.intrinsics.getPrimitiveValue(exportDefault=True)
                chunk.logger.info("Loading HoloLens tracking.")
                cameras, images, points3D = holo_io.load_model(chunk.node.inputFolder.value, intrinsics)

            if chunk.node.inputSfMFormat.value == "Meshroom":
                assert False, "TODO: Meshroom input format."

            if chunk.node.inputSfMFormat.value == "COLMAP":
                cameras, images, points3D = colmap_io.load_model(chunk.node.inputFolder.value)


            # update the pointcloud and the observations 
            if chunk.node.pointcloudFile.value:
                chunk.logger.info("Loading dense pointcloud.")
                xyz, rgb = meshroom_io.load_vertices(chunk.node.pointcloudFile.value) 
                
                chunk.logger.info("Estimate visibility.")
                visibility_map, new_xyz = utils_math.estimate_visibility(cameras, images, xyz, \
                    xyz_hash_scale = chunk.node.hashScale.value, all_points = chunk.node.allPoints.value)

                chunk.logger.info("Update points in 3D and their observations.")
                images, points3D = colmap.compose_images_and_points3D_from_visibilty(images, visibility_map, new_xyz)
                del visibility_map
                del new_xyz
                
                chunk.logger.info("Update colors of points in 3D.")
                points3D = utils_math.estimate_colors_of_points3D_fast(chunk.node.inputFolder.value, images, points3D)
            else: 
                chunk.logger.info("Dense pointcloud is not available.")


            # update images paths
            working_dir = os.path.dirname(chunk.logFile)
            if chunk.node.imagesPath.value == "absolute":
                images = holo_io.update_images_paths(images, working_dir)

            if chunk.node.imagesPath.value == "container":
                cache_dir = os.path.dirname(os.path.dirname(os.path.dirname(chunk.logFile)))
                rel_path_from_cache_dir = working_dir.replace(cache_dir,'/data')
                images = holo_io.update_images_paths(images, rel_path_from_cache_dir)


            # output structures
            if chunk.node.cpoyImagesToOutput.value:
                holo_io.copy_sfm_images(chunk.node.inputFolder.value, chunk.node.output.value)

            if "COLMAP" in chunk.node.outputSfMFormat.value:
                chunk.logger.info("Saving COLMAP SfM.")
                colmap_io.write_model(chunk.node.output.value, cameras, images, points3D)

            if "Meshroom" in chunk.node.outputSfMFormat.value:
                chunk.logger.info("Saving Meshroom SfM.")
                meshroom_io.write_model(chunk.node.outputMeshroomSfM.value, cameras, images, points3D)

            if "OBJ" in chunk.node.outputSfMFormat.value:
                chunk.logger.info("Saving pointcloud to OBJ.")
                xyz, rgb, xyz_colored, rgb_colored = colmap_io.points3D_to_xyz(points3D)
                holo_io.write_pointcloud_to_file(xyz, chunk.node.output.value + '/model.obj', rgb = rgb)
                holo_io.write_pointcloud_to_file(xyz_colored, chunk.node.output.value + '/model_rgb.obj', rgb = rgb_colored)

            chunk.logger.info("HoloLensIO done.") 

        except AssertionError as err:
            chunk.logger.error("Error in keyframe selector: " + err)
        finally:
            chunk.logManager.end()
