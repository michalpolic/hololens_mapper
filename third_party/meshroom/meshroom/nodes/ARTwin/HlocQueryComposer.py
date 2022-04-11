from __future__ import print_function

from matplotlib import use

__version__ = "0.1"

from meshroom.core import desc
import shutil
import os
import shutil
import sys


# import mapper packages
dir_path = __file__
for i in range(6):
    dir_path = os.path.dirname(dir_path)
sys.path.append(dir_path)
from src.utils.UtilsContainers import UtilsContainers

Intrinsic = [
    desc.StringParam(name="cameraModel", label="Camera model", description="Camera model", value="", uid=[0]),
    desc.IntParam(name="width", label="Width", description="Image Width", value=0, uid=[0], range=(0, 10000, 1)),
    desc.IntParam(name="height", label="Height", description="Image Height", value=0, uid=[0], range=(0, 10000, 1)),
    desc.StringParam(name="params", label="Parameters", description="Camera parameters", value="", uid=[0])
]


class HlocQueryComposer(desc.Node):

    category = 'ARTwin'
    documentation = '''
Compose query file for Hloc on input images.
                    
'''

    inputs = [
        desc.BoolParam(
            name="imageDir",
            label="Localize all directory",
            description="Use all images in query image directory (or localize specified images)",
            value="True",
            uid=[0],
        ),
        desc.ListAttribute(
            name="images",
            elementDesc=desc.StringParam(name="imagePath", label="ImagePath", description="Path to query images (.jpg)", value="", uid=[0]),
            label="Images",
            description="Paths to image files (.jpg)",
            group="",
        ),
        desc.File(
            name="hlocMapDir",
            label="Hloc Map directory",
            description="Hloc map directory (database, images, features)",
            value="",
            uid=[0],
        ),
        desc.File(
            name="queryImageDir",
            label="Query images directory",
            description="Directory containing query images",
            value="",
            uid=[0],
        ),
        desc.BoolParam(
            name="sameCamera",
            label="Same camera for all images",
            description="Same camera for all images",
            value="True",
            uid=[],
        ),
        desc.ListAttribute(
            name="intrinsics",
            elementDesc=desc.GroupAttribute(name="intrinsic", label="Intrinsic", description="", groupDesc=Intrinsic),
            label="Camera parameters",
            description="Camera Intrinsics",
            group="",
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
            label="Output query file",
            description="",
            value=desc.Node.internalFolder + 'hloc_queries.txt',
            uid=[],
            ),
    ]

    def processChunk(self, chunk):
        try:
            chunk.logManager.start(chunk.node.verboseLevel.value)
            output_file = chunk.node.output.value
            
            if not output_file:
                return

            images = chunk.node.images.getPrimitiveValue(exportDefault=True)
            use_dir = chunk.node.imageDir.value

            map_folder = chunk.node.hlocMapDir.value

            if not map_folder:
                chunk.logger.warning('Nothing to process, Hloc map required')
                return

            if map_folder[-1] != '/':
                map_folder = map_folder + '/'

            if (not use_dir) and len(images) < 1:
                chunk.logger.warning('Nothing to process, at least 1 image required')
                return

            image_folder = chunk.node.queryImageDir.value

            if use_dir and not map_folder:
                chunk.logger.warning('Nothing to process, at least image folder required')
                return


            if image_folder[-1] != '/':
                image_folder = image_folder + '/'

            intr = chunk.node.intrinsics.getPrimitiveValue(exportDefault=True)
            if len(intr) <  1 :
                chunk.logger.warning('Nothing to process, at least one camera intrinsics input required')
                return               

            queryfolder = map_folder + 'query/'

            
            # TODO Write code for more camera params! So far only one implemented

            params = ' ' + intr[0]['cameraModel'] + ' ' + str(intr[0]['width']) + ' ' + str(intr[0]['height']) + ' ' + intr[0]['params']

            if not os.path.isdir(queryfolder):
                os.mkdir(queryfolder)

            output_file = open(output_file, 'w')
            if not use_dir:
                for f in images:
                    im_name = f.split('/')[-1]
                    output_file.write('query/' + im_name + params + '\n')
                    if not os.path.isfile(queryfolder + im_name):
                        shutil.copyfile(f, queryfolder + im_name)

            else:
                for r, d, f in os.walk(image_folder):
                    for file in f:
                        if file.endswith('.jpg'):
                            im_name = file.split('/')[-1]
                            output_file.write('query/' + im_name + params + '\n')
                            if not os.path.isfile(queryfolder + im_name):
                                shutil.copyfile(r + file, queryfolder + im_name)
            output_file.close()

            chunk.logger.info('Query file composer done.') 

        except AssertionError as err:
            chunk.logger.error("Error in HlocQueryComposer selector: " + err)
        finally:
            chunk.logManager.end()
