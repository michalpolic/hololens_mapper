from __future__ import print_function

__version__ = "0.1"


from meshroom.core import desc
import os
import sys

import xml.etree.ElementTree as ET


# import mapper packages
dir_path = __file__
for i in range(6):
    dir_path = os.path.dirname(dir_path)
sys.path.append(dir_path)

from src.arfundation.ARFundationIO import ARFundationIO

class ARFundationPreprocessing(desc.Node):

    category = 'Input Preprocessing'
    documentation = '''Converts color.bin and depth.bin files to images and writes camera information into .txt file.'''

    inputs = [
        desc.File(
            name="colorFile",
            label="ColorFile",
            description="Path to the *color.bin file",
            value="",
            uid=[0],
        ),
        desc.File(
            name="depthFile",
            label="DepthFile",
            description="Path to the *depth.bin file",
            value="",
            uid=[0],
        ),
        desc.File(
            name="dataFile",
            label="DataFile",
            description="Path to the *data.xml file",
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
    ]
        
    
    def processChunk(self, chunk):
        try:
            chunk.logManager.start(chunk.node.verboseLevel.value)
            
            if not chunk.node.colorFile.value:
                chunk.logger.warning('Missing color data file (*_color.bin)')
                return
            if not chunk.node.depthFile.value:
                chunk.logger.warning('Missing depth data file (*_depth.bin).')
                return
            if not chunk.node.dataFile.value:
                chunk.logger.warning('Missing data file (*.xml).')
                return

            convertor = ARFundationIO()
            xml = ET.parse(chunk.node.dataFile.value).getroot()
            convertor.convert_rgb_images(chunk.node.colorFile.value, xml, chunk.node.output.value)
            convertor.convert_depth_images(chunk.node.depthFile.value, xml, chunk.node.output.value)

            chunk.logger.info('Conversion finished') 

        except AssertionError as err:
            chunk.logger.error("Error: " + err)
        finally:
            chunk.logManager.end()

