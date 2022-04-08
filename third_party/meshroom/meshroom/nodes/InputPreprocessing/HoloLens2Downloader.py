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
from src.holo.HoloIO import HoloIO

class HoloLens2Downloader(desc.Node):

    category = 'InputPreprocessing'
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

            # init
            holo_io = HoloIO()
            folder = chunk.node.recordingsFolder.value
            sensors = ["pv", "vlc_ll", "vlc_lf", "vlc_rf", "vlc_rr", "long_throw_depth"]
            holo_io.mkdir_if_not_exists(folder, logger = chunk.logger)

            # list recordings
            url, records, package_full_name = holo_io.connect(chunk.node.ip.value, \
                chunk.node.username.value, chunk.node.password.value, logger = chunk.logger)
            
            # download recordings
            if chunk.node.download.value:
                holo_io.download_recordings(url, package_full_name, records, folder, logger = chunk.logger)

                #extract tars
                if len(records) > 0:
                    chunk.logger.info("Extracting images")
                    for recording in records:
                        tarfiles_to_remove = []
                        for sensor in sensors:
                            tarpath = os.path.join(folder,recording,sensor + ".tar")
                            if os.path.isfile(tarpath):
                                chunk.logger.info("Extracting from: " + tarpath)
                                with tarfile.open(tarpath) as tar:
                                    tar.extractall(os.path.join(folder,recording) + "/")
                                tarfiles_to_remove.append(tarpath)

                        # wait until the extraction ends
                        for tarpath in tarfiles_to_remove:
                            file_removed = False
                            while not file_removed:
                                try:
                                    os.remove(tarpath) 
                                except Exception as e:
                                    time.sleep(1)
                                finally:
                                    if not os.path.isfile(tarpath):
                                        file_removed = True

                        # convert PV and rotate vlc images
                        chunk.logger.info("Converting image files")
                        cams = sensors[0:5]
                        for cam in cams:
                            chunk.logger.info("Converting files in: " + folder + recording + "/" + cam)
                            holo_io.convert_images(os.path.join(folder,recording,cam))
                        

            # delete recordings on device
            if chunk.node.delete.value:
                holo_io.delete_recordings(url, package_full_name, records, logger = chunk.logger)

            chunk.logger.info('HoloLens1Downloader is done.') 

        except AssertionError as err:
            chunk.logger.error("Error in keyframe selector: " + err)
        finally:
            chunk.logManager.end()
