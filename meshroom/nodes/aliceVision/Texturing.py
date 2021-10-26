__version__ = "6.0"

from meshroom.core import desc, Version, pyCompatibility
import logging


class Texturing(desc.CommandLineNode):
    commandLine = 'aliceVision_texturing {allParams}'
    cpu = desc.Level.INTENSIVE
    ram = desc.Level.INTENSIVE

    category = 'Dense Reconstruction'
    documentation = '''
This node computes the texturing on the mesh.

If the mesh has no associated UV, it automatically computes UV maps.

For each triangle, it uses the visibility information associated to each vertex to retrieve the texture candidates.
It select the best cameras based on the resolution covering the triangle. Finally it averages the pixel values using multiple bands in the frequency domain.
Many cameras are contributing to the low frequencies and only the best ones contributes to the high frequencies.

## Online
[https://alicevision.org/#photogrammetry/texturing](https://alicevision.org/#photogrammetry/texturing)
'''

    inputs = [
        desc.File(
            name='input',
            label='Dense SfMData',
            description='SfMData file.',
            value='',
            uid=[0],
        ), 
        desc.File(
            name='imagesFolder',
            label='Images Folder',
            description='Use images from a specific folder instead of those specify in the SfMData file.\nFilename should be the image uid.',
            value='',
            uid=[0],
        ),
        desc.File(
            name='inputMesh',
            label='Mesh',
            description='Optional input mesh to texture. By default, it will texture the result of the reconstruction.',
            value='',
            uid=[0],
        ),
        desc.File(
            name='inputRefMesh',
            label='Ref Mesh',
            description='Optional input mesh to compute height maps and normal maps. If not provided, no additional maps with geometric information will be generated.',
            value='',
            uid=[0],
        ),
        desc.ChoiceParam(
            name='textureSide',
            label='Texture Side',
            description='''Output texture size''',
            value=8192,
            values=(1024, 2048, 4096, 8192, 16384),
            exclusive=True,
            uid=[0],
        ),
        desc.ChoiceParam(
            name='downscale',
            label='Texture Downscale',
            description='''Texture downscale factor''',
            value=2,
            values=(1, 2, 4, 8),
            exclusive=True,
            uid=[0],
        ),
        desc.ChoiceParam(
            name='outputMeshFileType',
            label='Mesh File Type',
            description='File Type',
            value='obj',
            values=('obj', 'gltf', 'fbx', 'stl'),
            exclusive=True,
            uid=[0],
        ),
        desc.GroupAttribute(name="colorMapping", label="Color Mapping", description="Color Map Parameters",
            enabled=lambda node: (node.imagesFolder.value != ''),
            group=None,
            groupDesc=[
                desc.BoolParam(
                    name='enable',
                    label='Enable',
                    description='Generate Textures',
                    value=True,
                    uid=[],
                    group=None,
                ),
                desc.ChoiceParam(
                    name='colorMappingFileType',
                    label='File Type',
                    description='Texture File Type',
                    value='exr',
                    values=('exr', 'png', 'tiff', 'jpg'),
                    exclusive=True,
                    uid=[0],
                    enabled=lambda node: node.colorMapping.enable.value,
                ),
            ],
        ),
        desc.GroupAttribute(name="bumpMapping", label="Bump Mapping", description="Bump Mapping Parameters",
            enabled=lambda node: (node.inputRefMesh.value != ''),
            group=None,
            groupDesc=[
                desc.BoolParam(
                    name='enable',
                    label='Enable',
                    description='Generate Normal / Bump Maps',
                    value=True,
                    uid=[],
                    group=None,
                ),
                desc.ChoiceParam(
                    name='bumpType',
                    label='Bump Type',
                    description='Export Normal Map or Height Map',
                    value='Normal',
                    values=('Height', 'Normal'),
                    exclusive=True,
                    uid=[0],
                    enabled=lambda node: node.bumpMapping.enable.value,
                ),
                desc.ChoiceParam(
                    name='normalFileType',
                    label='File Type',
                    description='NormalMap Texture File Type',
                    value='exr',
                    values = ('exr', 'png', 'tiff', 'jpg'),
                    exclusive=True,
                    uid=[0],
                    enabled=lambda node: node.bumpMapping.enable.value and node.bumpMapping.bumpType.value == "Normal",
                ),
                desc.ChoiceParam(
                    name='heightFileType',
                    label='File Type',
                    description='HeightMap Texture File Type',
                    value='exr',
                    values=('exr',),
                    exclusive=True,
                    uid=[0],
                    enabled=lambda node: node.bumpMapping.enable.value and node.bumpMapping.bumpType.value == "Height",
                ),
            ],
        ),
        desc.GroupAttribute(name="displacementMapping", label="Displacement Mapping", description="Displacement Mapping Parameters",
            enabled=lambda node: (node.inputRefMesh.value != ''),
            group=None,
            groupDesc=[
                desc.BoolParam(
                    name='enable',
                    label='Enable',
                    description='Generate Height Maps for Displacement',
                    value=True,
                    uid=[],
                    group=None,
                ),
                desc.ChoiceParam(
                    name='displacementMappingFileType',
                    label='File Type',
                    description='HeightMap Texture File Type',
                    value='exr',
                    values=('exr',),
                    exclusive=True,
                    uid=[0],
                    enabled=lambda node: node.displacementMapping.enable.value,
                ),
            ],
        ),
        desc.ChoiceParam(
            name='unwrapMethod',
            label='Unwrap Method',
            description='Method to unwrap input mesh if it does not have UV coordinates.\n'
                        ' * Basic (> 600k faces) fast and simple. Can generate multiple atlases.\n'
                        ' * LSCM (<= 600k faces): optimize space. Generates one atlas.\n'
                        ' * ABF (<= 300k faces): optimize space and stretch. Generates one atlas.',
            value="Basic",
            values=("Basic", "LSCM", "ABF"),
            exclusive=True,
            uid=[0],
        ),
        desc.BoolParam(
            name='useUDIM',
            label='Use UDIM',
            description='Use UDIM UV mapping.',
            value=True,
            uid=[0],
        ),
        desc.BoolParam(
            name='fillHoles',
            label='Fill Holes',
            description='Fill Texture holes with plausible values',
            value=False,
            uid=[0],
        ),
        desc.IntParam(
            name='padding',
            label='Padding',
            description='''Texture edge padding size in pixel''',
            value=5,
            range=(0, 20, 1),
            uid=[0],
            advanced=True,
        ),
        desc.IntParam(
            name='multiBandDownscale',
            label='Multi Band Downscale',
            description='''Width of frequency bands for multiband blending''',
            value=4,
            range=(0, 8, 2),
            uid=[0],
            advanced=True,
        ),
        desc.GroupAttribute(
            name="multiBandNbContrib",
            label="MultiBand contributions",
            groupDesc=[
                desc.IntParam(name="high", label="High Freq", description="High Frequency Band", value=1, uid=[0], range=None),
                desc.IntParam(name="midHigh", label="Mid-High Freq", description="Mid-High Frequency Band", value=5, uid=[0], range=None),
                desc.IntParam(name="midLow", label="Mid-Low Freq", description="Mid-Low Frequency Band", value=10, uid=[0], range=None),
                desc.IntParam(name="low", label="Low Freq", description="Low Frequency Band", value=0, uid=[0], range=None),
            ],
            description='''Number of contributions per frequency band for multiband blending (each frequency band also contributes to lower bands)''',
            advanced=True,
        ),
        desc.BoolParam(
            name='useScore',
            label='Use Score',
            description='Use triangles scores (ie. reprojection area) for multiband blending.',
            value=True,
            uid=[0],
            advanced=True,
        ),
        desc.FloatParam(
            name='bestScoreThreshold',
            label='Best Score Threshold',
            description='''(0.0 to disable filtering based on threshold to relative best score)''',
            value=0.1,
            range=(0.0, 1.0, 0.01),
            uid=[0],
            advanced=True,
        ),
        desc.FloatParam(
            name='angleHardThreshold',
            label='Angle Hard Threshold',
            description='''(0.0 to disable angle hard threshold filtering)''',
            value=90.0,
            range=(0.0, 180.0, 0.01),
            uid=[0],
            advanced=True,
        ),
        desc.ChoiceParam(
            name='processColorspace',
            label='Process Colorspace',
            description="Colorspace for the texturing internal computation (does not impact the output file colorspace).",
            value='sRGB',
            values=('sRGB', 'LAB', 'XYZ'),
            exclusive=True,
            uid=[0],
            advanced=True,
        ),
        desc.BoolParam(
            name='correctEV',
            label='Correct Exposure',
            description='Uniformize images exposure values.',
            value=False,
            uid=[0],
        ),
        desc.BoolParam(
            name='forceVisibleByAllVertices',
            label='Force Visible By All Vertices',
            description='''Triangle visibility is based on the union of vertices visiblity.''',
            value=False,
            uid=[0],
            advanced=True,
        ),
        desc.BoolParam(
            name='flipNormals',
            label='Flip Normals',
            description='''Option to flip face normals. It can be needed as it depends on the vertices order in triangles and the convention change from one software to another.''',
            value=False,
            uid=[0],
            advanced=True,
        ),
        desc.ChoiceParam(
            name='visibilityRemappingMethod',
            label='Visibility Remapping Method',
            description='''Method to remap visibilities from the reconstruction to the input mesh (Pull, Push, PullPush, MeshItself).''',
            value='PullPush',
            values=['Pull', 'Push', 'PullPush', 'MeshItself'],
            exclusive=True,
            uid=[0],
            advanced=True,
        ),
        desc.FloatParam(
            name='subdivisionTargetRatio',
            label='Subdivision Target Ratio',
            description='''Percentage of the density of the reconstruction as the target for the subdivision (0: disable subdivision, 0.5: half density of the reconstruction, 1: full density of the reconstruction).''',
            value=0.8,
            range=(0.0, 1.0, 0.001),
            uid=[0],
            advanced=True,
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
            label='Folder',
            description='Folder for output mesh: OBJ, material and texture files.',
            value=desc.Node.internalFolder,
            uid=[],
        ),
        desc.File(
            name='outputMesh',
            label='Mesh',
            description='Output Mesh file.',
            value=desc.Node.internalFolder + 'texturedMesh.{outputMeshFileTypeValue}',
            uid=[],
            group='',
            ),
        desc.File(
            name='outputMaterial',
            enabled= lambda node: node.outputMeshFileType.value == "obj",
            label='Material',
            description='Output Material file.',
            value=desc.Node.internalFolder + 'texturedMesh.mtl',
            uid=[],
            group='',
            ),
        desc.File(
            name='outputTextures',
            label='Textures',
            description='Output Texture files.',
            value= lambda attr: desc.Node.internalFolder + 'texture_*.' + attr.node.colorMapping.colorMappingFileType.value if attr.node.colorMapping.enable.value else '',
            uid=[],
            group='',
            ),
    ]

    def upgradeAttributeValues(self, attrValues, fromVersion):
        if fromVersion < Version(6, 0):
            outputTextureFileType = attrValues['outputTextureFileType']
            if isinstance(outputTextureFileType, pyCompatibility.basestring):
                attrValues['colorMapping'] = {}
                attrValues['colorMapping']['colorMappingFileType'] = outputTextureFileType
        return attrValues
