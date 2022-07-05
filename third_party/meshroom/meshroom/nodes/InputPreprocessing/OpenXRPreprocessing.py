from __future__ import print_function

from numpy import False_

__version__ = '0.1'

from meshroom.core import desc
import shutil
import glob
import os
import time
import sys
import tarfile

import numpy as np
from PIL import Image
import xml.etree.ElementTree as ET

# import mapper packages
dir_path = __file__
for i in range(6):
    dir_path = os.path.dirname(dir_path)
sys.path.append(dir_path)
from src.holo.HoloIO import HoloIO

class OpenXRPreprocessing(desc.Node):

    category = 'Input Preprocessing'
    documentation = '''
This node download the recordings available at HoloLens 1. 
The data are formated such a way to be processed by OI Convertor.
'''

    inputs = [
        desc.File(
            name='dataFile',
            label='Data file',
            description='The file with *.xml data.',
            value='',
            uid=[0],
        ),
        desc.File(
            name='colorFile',
            label='Color file',
            description='The file with *color.bin data.',
            value='',
            uid=[0],
        ),
        desc.File(
            name='depthFile',
            label='Depth file',
            description='The file with *depth.bin data.',
            value='',
            uid=[0],
        ),
        desc.BoolParam(
            name="delete", 
            label="Delete binaries",
            description="Delete the binaries after unpacking.",
            value=False,
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
            
            if not chunk.node.dataFile:
                chunk.logger.warning('Missing data file (*.xml).')
                return

            if not chunk.node.colorFile:
                chunk.logger.warning('Missing color data file (*_color.bin).')
                return

            if not chunk.node.depthFile:
                chunk.logger.warning('Missing depth data file (*_depth.bin).')
                return
            # # init
            # holo_io = HoloIO()
            # folder = chunk.node.recordingsFolder.value
            # sensors = ["pv", "vlc_ll", "vlc_lf", "vlc_rf", "vlc_rr", "long_throw_depth"]
            # holo_io.mkdir_if_not_exists(folder, logger = chunk.logger)

        dtype = np.dtype('B')
        camera_id = "1"
        root = tree.getroot()

            # Convertor takes only "depth" or "color" as arguments
        def Convertor(type):
            for data in root.findall(type):
                index = data.get("index")
                width = data.get("width")
                height = data.get("height")
                length = data.get("length")
                position = data.get("position")
                
                width = int(width)
                height = int(height)
                length = int(length)
                position = int(position)

                if type == "color":
                    with open(clrFile, mode="rb") as file:
                        numpy_data = np.fromfile(file, dtype, length, sep='', offset=position)

                    array = np.reshape(numpy_data, (height, width, 4))
                    im = Image.fromarray(array)
                    im.save(clrPath + "Color" + index + ".png")
                
                if type == "depth":
                    with open(dpthFile, mode="rb") as file:
                        numpy_data = np.fromfile(file, dtype, length, sep='', offset=position)

                    array = np.reshape(numpy_data, (height, width, 4))
                    im = Image.fromarray(array)
                    im.save(dpthPath + "Depth" + index + ".png")

        # Convertor("color")
        # Convertor("depth")


        with open(txtPath + "Pose1.txt", "w+") as f:
            f.write("#   IMAGE_ID, QW, QX, QY, QZ, TX, TY, TZ, CAMERA_ID, NAME")

            for data in root.findall("pose"):
                index = data.get("index")
                
                tx = data.find("pos").get("x")
                ty = data.find("pos").get("y")
                tz = data.find("pos").get("z")

                qw = data.find("rot").get("w")
                qx = data.find("rot").get("x")
                qy = data.find("rot").get("y")
                qz = data.find("rot").get("z")

                f.write("\n" + index +" "+ qw+" "+ qx +" "+ qy +" "+ qz +" "+ tx +" "+ ty +" "+ tz +" "+ camera_id + " Image" + index + ".png")


        for data in root.findall("color"):
            index = data.get("index")
            width = data.get("width")
            height = data.get("height")
            length = data.get("length")
            position = data.get("position")
            
            width = int(width)
            height = int(height)
            length = int(length)
            position = int(position)

            with open(clrFile, mode="rb") as file:
                numpy_data = np.fromfile(file, dtype, length, sep='', offset=position)

            array = np.reshape(numpy_data, (height, width, 4))
            im = Image.fromarray(array)
            im.save(clrPath + "Color" + index + ".png")


        for data in root.findall("depth"):
            index = data.get("index")
            width = data.get("width")
            height = data.get("height")
            length = data.get("length")
            position = data.get("position")
            
            width = int(width)
            height = int(height)
            length = int(length)
            position = int(position)

            with open(dpthFile, mode="rb") as file:
                numpy_data = np.fromfile(file, dtype, length, sep='', offset=position)

            array = np.reshape(numpy_data, (height, width, 4))
            im = Image.fromarray(array)
            im.save(dpthPath + "Depth" + index + ".png")

            # delete recordings on device
            if chunk.node.delete.value:
                pass

            chunk.logger.info('HoloLens1Downloader is done.') 

        except AssertionError as err:
            chunk.logger.error("Error in keyframe selector: " + err)
        finally:
            chunk.logManager.end()