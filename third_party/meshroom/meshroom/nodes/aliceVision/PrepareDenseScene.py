__version__ = "3.0"

from meshroom.core import desc, Version


class PrepareDenseScene(desc.CommandLineNode):
    commandLine = 'aliceVision_prepareDenseScene {allParams}'
    # size = desc.DynamicNodeSize('input')
    # parallelization = desc.Parallelization(blockSize=40)
    # commandLineRange = '--rangeStart {rangeStart} --rangeSize {rangeBlockSize}'

    category = 'Dense Reconstruction'
    documentation = '''
This node export undistorted images so the depth map and texturing can be computed on Pinhole images without distortion.
'''

    inputs = [
        desc.StringParam(
            name="containerName", 
            label="AliceVision container",
            description="If you would like to run the comnands inside a container, "
                "set the path (Singularity) or name (Docker) of the container to run.", 
            value="", 
            uid=[],
<<<<<<< HEAD
            advanced=True,
=======
            advanced=True
>>>>>>> dbf29fe57ab7ecd1734479c51159b27d8fd0a81b
        ),
        desc.StringParam(
            name="containerPrefix", 
            label="Container prefix",
            description="If you would like to run the comnands inside a container, "
                "set the internal path to executables inside the container. "
                "If the container is build with executables in path, let this variable empty.", 
            value="", 
            uid=[],
<<<<<<< HEAD
            advanced=True,
=======
            advanced=True
>>>>>>> dbf29fe57ab7ecd1734479c51159b27d8fd0a81b
        ),
        desc.File(
            name='input',
            label='SfMData',
            description='''SfMData file.''',
            value='',
            uid=[0],
        ),
        desc.ListAttribute(
            elementDesc=desc.File(
                name="imagesFolder",
                label="Images Folder",
                description="",
                value="",
                uid=[0],
            ),
            name="imagesFolders",
            label="Images Folders",
            description='Use images from specific folder(s). Filename should be the same or the image uid.',
        ),
        desc.ListAttribute(
            elementDesc=desc.File(
                name="masksFolder",
                label="Masks Folder",
                description="",
                value="",
                uid=[0],
            ),
            name="masksFolders",
            label="Masks Folders",
            description='Use masks from specific folder(s). Filename should be the same or the image uid.',
        ),
        desc.ChoiceParam(
            name='outputFileType',
            label='Output File Type',
            description='Output file type for the undistorted images.',
            value='exr',
            values=['jpg', 'png', 'tif', 'exr'],
            exclusive=True,
            uid=[0],
            advanced=True
        ),
        desc.BoolParam(
            name='saveMetadata',
            label='Save Metadata',
            description='Save projections and intrinsics information in images metadata (only for .exr images).',
            value=True,
            uid=[0],
            advanced=True
        ),
        desc.BoolParam(
            name='saveMatricesTxtFiles',
            label='Save Matrices Text Files',
            description='Save projections and intrinsics information in text files.',
            value=False,
            uid=[0],
            advanced=True
        ),
        desc.BoolParam(
            name='evCorrection',
            label='Correct images exposure',
            description='Apply a correction on images Exposure Value',
            value=False,
            uid=[0],
            advanced=True
        ),
        desc.ChoiceParam(
            name='verboseLevel',
            label='Verbose Level',
            description='''verbosity level (fatal, error, warning, info, debug, trace).''',
            value='info',
            values=['fatal', 'error', 'warning', 'info', 'debug', 'trace'],
            exclusive=True,
            uid=[],
        ),
    ]

    outputs = [
        desc.File(
            name='output',
            label='Images Folder',
            description='''Output folder.''',
            value=desc.Node.internalFolder,
            uid=[],
        ),
        desc.File(
            name='outputUndistorted',
            label='Undistorted Images',
            description='List of undistorted images.',
            value=desc.Node.internalFolder + '*.{outputFileTypeValue}',
            uid=[],
            group='',
            advanced=True
            ),
    ]
