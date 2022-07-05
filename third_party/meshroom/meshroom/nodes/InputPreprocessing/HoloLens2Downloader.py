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

# import mapper packages
dir_path = __file__
for i in range(6):
    dir_path = os.path.dirname(dir_path)
sys.path.append(dir_path)
from src.holo.HoloIO2 import HoloIO2

sys.path.append(os.path.join(dir_path, 'third_party', 'HoloLens2ForCV','Samples','StreamRecorder','StreamRecorderConverter'))
from recorder_console import *
from process_all import process_all

class HoloLens2Downloader(desc.Node):

    category = 'Input Preprocessing'
    documentation = '''
This node download the recordings available at HoloLens 2. 
The data are formated such a way to be processed by OI Convertor.
'''

    inputs = [
        desc.StringParam(
            name='username',
            label='Username',
            description='The username for loging the HoloLens console.',
            value='',
            uid=[0],
        ),
        desc.StringParam(
            name='password',
            label='Password',
            description='The password for loging the HoloLens console.',
            value='',
            uid=[0],
        ),
        desc.StringParam(
            name='ip',
            label='IP adress',
            description='The threshold for minimal laplacian variation in the image.',
            value='',
            uid=[0],
        ),
        desc.File(
            name='recordingsFolder',
            label='Recordings folder',
            description='The folder where to download all the recordings.',
            value='',
            uid=[0],
        ),
        desc.BoolParam(
            name="download", 
            label="Download recordings",
            description="Download recordings from device.",
            value=True,
            uid=[0],
        ),            
        desc.BoolParam(
            name="delete", 
            label="Delete recordings",
            description="Delete the recordings on device.",
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

    outputs = []

    def is_locked(self, filepath):
        """Checks if a file is locked by opening it in append mode.
        If no exception thrown, then the file is not locked.
        """
        locked = None
        file_object = None
        try:
            file_object = open(filepath, 'a', 8)
            if file_object:
                locked = False
        except IOError:
            locked = True
        finally:
            if file_object:
                file_object.close()
        return locked
    

    def filter_auxilary_files(self, w_path):
        onlydirs = [f for f in os.listdir(w_path) if os.path.isdir(os.path.join(w_path, f))]
        for dir_name in onlydirs:
            recodring_dir = os.path.join(w_path, dir_name)
            files = os.listdir(recodring_dir)
            for file in files:
                if file[-4:] == ".tar":
                    os.remove(os.path.join(recodring_dir,file))
                if file == "Depth Long Throw":      
                    depth_files = os.listdir(os.path.join(recodring_dir,file))
                    for depth_file in depth_files:
                        if depth_file[-4:] == ".pgm":
                            os.remove(os.path.join(recodring_dir,file,depth_file))


    def processChunk(self, chunk):
        try:
            chunk.logManager.start(chunk.node.verboseLevel.value)
            
            if not chunk.node.username:
                chunk.logger.warning('Missing username field.')
                return
            if not chunk.node.password:
                chunk.logger.warning('Missing password field.')
                return
            if not chunk.node.ip:
                chunk.logger.warning('Missing ip adress field.')
                return
            if not chunk.node.recordingsFolder:
                chunk.logger.warning('Missing recordings folder field.')
                return

            w_path = Path(chunk.node.recordingsFolder.value)
            w_path.mkdir(exist_ok=True)

            dev_portal_browser = DevicePortalBrowser()
            dev_portal_browser.connect(chunk.node.ip.value,
                               chunk.node.username.value,
                               chunk.node.password.value)
            dev_portal_browser.list_recordings()

            # download from device
            rs = RecorderShell(w_path, dev_portal_browser)
            if chunk.node.download.value:
                rs.do_download_all(None)

            # decompress files
            recording_names = sorted(w_path.glob("*"))
            for recording_name in recording_names:
                process_all(recording_name)

            # delete recordings on device
            if chunk.node.delete.value:
                for i in range(len(dev_portal_browser.recording_names)):
                    dev_portal_browser.delete_recording(i)

            # clear tar and binary files
            self.filter_auxilary_files(w_path)

            chunk.logger.info('HoloLens2Downloader is done.') 

        except AssertionError as err:
            chunk.logger.error("Error in keyframe selector: " + err)
        finally:
            chunk.logManager.end()
