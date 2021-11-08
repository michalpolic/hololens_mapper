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


Intrinsic = [
    desc.IntParam(name="intrinsicId", label="Id", description="Intrinsic UID", value=-1, uid=[0], range=None),
    desc.ListAttribute(
            name="csvPrefixes",
            elementDesc=desc.StringParam(name="csvPrefix", label="CSV prefix", description="The name of csv and images dir, e.g. pv for pv.csv.", value="", uid=[]),
            label="CSV prefixes",
            description="The name of csv and images dir, e.g. pv for pv.csv. List of names if we have common intrinsics for set of cameras.",
        ),
    desc.IntParam(name="width", label="Width", description="Image Width", value=0, uid=[], range=(0, 10000, 1)),
    desc.IntParam(name="height", label="Height", description="Image Height", value=0, uid=[], range=(0, 10000, 1)),
    desc.FloatParam(name="pxFocalLength", label="Focal Length", description="Focal Length (in pixels).", value=-1.0, uid=[0], range=None),
    desc.GroupAttribute(name="principalPoint", label="Principal Point", description="Position of the Optical Center in the Image (i.e. the sensor surface).", groupDesc=[
        desc.FloatParam(name="x", label="x", description="", value=0, uid=[], range=(0, 10000, 1)),
        desc.FloatParam(name="y", label="y", description="", value=0, uid=[], range=(0, 10000, 1)),
        ]),
    desc.ListAttribute(
            name="distortionParams",
            elementDesc=desc.FloatParam(name="p", label="", description="", value=0.0, uid=[0], range=(-0.1, 0.1, 0.01)),
            label="Distortion Params",
            description="Distortion Parameters",
        ),
]

class HoloLensIO(desc.Node):
    size = desc.DynamicNodeSize('intrinsics')
    category = 'ARTwin'
    documentation = '''
This transforms the input HoloLens recording into different data format, e.g., COLMAP or Meshroom. 
The code does not compute visibility of individual 3D points. It only transform available data into
different format.
'''

    inputs = [
        desc.File(
            name="recordingDir",
            label="Recording Folder",
            description="HoloLens recording directory (images in pv/*.jpg, " \
                "depth in long_throw_depth/*.pgm, etc. + related .csv).",
            value="",
            uid=[0],
        ),
        desc.File(
            name="pointcloudFile",
            label="Dense pointcloud file",
            description="Dense pointcloud from HoloLens depthmaps in the " \
                "same coordinate system as the camera poses. Format .obj or .ply.",
            value="",
            uid=[0],
        ),
        desc.ListAttribute(
            name="intrinsics",
            elementDesc=desc.GroupAttribute(name="intrinsic", label="Intrinsic", description="", groupDesc=Intrinsic),
            label="Camera parameters",
            description="Camera Intrinsics",
            group="",
        ),
        desc.ChoiceParam(
            name="outputSfMFormat",
            label="Output format",
            description="The output data format, e.g., COLMAP or Meshroom.",
            value='COLMAP',
            values=['COLMAP'],  #, 'Meshroom'
            exclusive=True,
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
            
            if not chunk.node.recordingDir:
                chunk.logger.warning('Nothing to process')
                return
            if not chunk.node.output.value:
                return

            # setting
            intrinsics = chunk.node.intrinsics.getPrimitiveValue(exportDefault=True)
            input_csv_files = [chunk.node.recordingDir.value + "/pv.csv", \
                chunk.node.recordingDir.value + "/vlc_lf.csv", chunk.node.recordingDir.value + "/vlc_ll.csv", \
                chunk.node.recordingDir.value + "/vlc_rf.csv", chunk.node.recordingDir.value + "/vlc_rr.csv"]


            # load dense pointcloud
            xyz = np.array((3,0))
            rgb = np.array((3,0))
            if chunk.node.output.value:
                meshroom_io = MeshroomIO() 
                chunk.logger.info('Loading HoloLens model.')
                xyz, rgb = meshroom_io.load_vertices(chunk.node.pointcloudFile.value) 
            else: 
                chunk.logger.info('Dense pointcloud is not available.')



            # load HoloLens from CSV files
            holo_io = HoloIO()
            chunk.logger.info('Loading HoloLens model.')
            holo_cameras, holo_images, holo_points3D = holo_io.load_model(input_csv_files)


            # save structures

             
            chunk.logger.info('Data are transformed.') 

        except AssertionError as err:
            chunk.logger.error("Error in keyframe selector: " + err)
        finally:
            chunk.logManager.end()
