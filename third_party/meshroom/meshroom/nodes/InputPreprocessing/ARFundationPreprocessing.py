from __future__ import print_function
from curses import endwin

from sklearn.cluster import estimate_bandwidth

__version__ = "0.1"


from meshroom.core import desc
import os
import sys
import glob
from pathlib import Path
from py7zr import unpack_7zarchive
import shutil

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
            name="recordingFolder",
            label="Recording folder",
            description='''Path to the folder containing *Color.bin, *Depth.[bin,tar], and *Data.xml files.
            The paths are primary loaded from ColorFile, DepthFile, and DataFile.
            If these variables are empty, the script load the folders in RecordingFolder.''',
            value="",
            uid=[0],
        ),
        desc.File(
            name="colorFile",
            label="Color file",
            description="Path to the *color.bin file",
            value="",
            uid=[0],
        ),
        desc.File(
            name="depthFile",
            label="Depth file",
            description="Path to the *depth.bin file",
            value="",
            uid=[0],
        ),
        desc.File(
            name="dataFile",
            label="Data file",
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
        

    def decompress_and_get_paths(self, chunk):
        colorFile = chunk.node.colorFile.value 
        depthFile = chunk.node.depthFile.value
        dataFile = chunk.node.dataFile.value
        recordingFolder = chunk.node.recordingFolder.value
        
        if colorFile and depthFile and dataFile:
            return ([colorFile], [depthFile], [dataFile])
        if not recordingFolder:
            chunk.logger.error('Missing recording file / files.')

        if recordingFolder.endswith('.7z'):
            Path(recordingFolder[0:-3]).mkdir(exist_ok=True)
            shutil.register_unpack_format('7zip', ['.7z'], unpack_7zarchive)
            shutil.unpack_archive(recordingFolder, recordingFolder[0:-3])
            recordingFolder = recordingFolder[0:-3]
            
        if not colorFile:
            colorFile = sorted(glob.glob(recordingFolder + '/*_Color.bin'))
        if not dataFile:
            dataFile = sorted(glob.glob(recordingFolder + '/*_Data.xml'))

        if not depthFile:
            depthFile = sorted(glob.glob(recordingFolder + '/*_Depth.bin'))
        if not depthFile:
            depthFile = glob.glob(recordingFolder + '/*_Depth.7z')  
            for df in depthFile:
                shutil.unpack_archive(df, recordingFolder)
                os.remove(df) 
            depthFile = sorted(glob.glob(recordingFolder + '/*_Depth.bin'))

        # final check
        if not colorFile:
            chunk.logger.error('Missing color data file (*_Color.bin)')
        if not depthFile:
            chunk.logger.error('Missing depth data file (*_Depth.bin).')
        if not dataFile:
            chunk.logger.error('Missing data file (*_Data.xml).')
        return (colorFile, depthFile, dataFile)
    
    def processChunk(self, chunk):
        try:
            chunk.logManager.start(chunk.node.verboseLevel.value)
            chunk.logger.info('Decompress files and prepare paths.') 
            colorFiles, depthFiles, dataFiles = self.decompress_and_get_paths(chunk)
            
            convertor = ARFundationIO()
            for i in range(len(colorFiles)):
                color_file_path = Path(colorFiles[i])
                chunk.logger.info('Converting ' + color_file_path.stem[0:-6]) 
                out_dir = Path(chunk.node.output.value) / color_file_path.stem[0:-6]
                out_dir.mkdir(exist_ok=True)

                xml = ET.parse(dataFiles[i]).getroot()
                convertor.convert_rgb_images(colorFiles[i], xml, out_dir)
                convertor.convert_depth_images(depthFiles[i], xml, out_dir)

            chunk.logger.info('Conversion finished') 

        except AssertionError as err:
            chunk.logger.error("Error: " + err)
        finally:
            chunk.logManager.end()

