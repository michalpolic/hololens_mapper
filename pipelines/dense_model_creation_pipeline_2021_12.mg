{
    "header": {
        "pipelineVersion": "2.2",
        "releaseVersion": "2021.1.0",
        "fileVersion": "1.1",
        "nodesVersions": {
            "HololensPointcloudComposer": "0.1",
            "ModelsAligner": "0.1",
            "DepthMap": "2.0",
            "MatchingPairsSelector": "0.1",
            "ConvertSfMFormat": "2.1",
            "PrepareDenseScene": "3.0",
            "HoloLensMatcher": "0.1",
            "DensePonitcloudsAligner": "0.1",
            "KeyframeSelector": "0.1",
            "Texturing": "6.0",
            "FilterColmapSfM": "0.1",
            "DensePointcloudFilter": "0.1",
            "DepthMapFilter": "3.0",
            "MeshFiltering": "3.0",
            "HoloLensIO": "0.1",
            "ColmapMapper": "0.1",
            "Meshing": "7.0"
        }
    },
    "graph": {
        "HololensPointcloudComposer_1": {
            "nodeType": "HololensPointcloudComposer",
            "position": [
                -118,
                33
            ],
            "parallelization": {
                "blockSize": 0,
                "size": 1,
                "split": 1
            },
            "uids": {
                "0": "9d95bda95ee9c497fbd68bf647b7d059f82819db"
            },
            "internalFolder": "{cache}/{nodeType}/{uid0}/",
            "inputs": {
                "recordingDir": "/local1/projects/artwin/datasets/Munich/HoloLensRecording__2021_08_02__11_23_59_MUCLab_1",
                "UVfile": "/local1/projects/artwin/datasets/uvdata.txt",
                "verboseLevel": "info"
            },
            "outputs": {
                "output": "{cache}/{nodeType}/{uid0}//model.obj"
            }
        },
        "KeyframeSelector_1": {
            "nodeType": "KeyframeSelector",
            "position": [
                64,
                -11
            ],
            "parallelization": {
                "blockSize": 0,
                "size": 1,
                "split": 1
            },
            "uids": {
                "0": "f84a14d469b4990d95dadb88c385c518bdc2db54"
            },
            "internalFolder": "{cache}/{nodeType}/{uid0}/",
            "inputs": {
                "recordingDir": "{HololensPointcloudComposer_1.recordingDir}",
                "pvBlurThreshold": 15.0,
                "pvMinFrameOffset": 5,
                "vlcMinFrameOffset": 5,
                "verboseLevel": "info"
            },
            "outputs": {
                "output": "{cache}/{nodeType}/{uid0}/"
            }
        },
        "DensePointcloudFilter_1": {
            "nodeType": "DensePointcloudFilter",
            "position": [
                57,
                124
            ],
            "parallelization": {
                "blockSize": 0,
                "size": 1,
                "split": 1
            },
            "uids": {
                "0": "933b7ad41cecd8ec0753e9ba91c17d917a1cc711"
            },
            "internalFolder": "{cache}/{nodeType}/{uid0}/",
            "inputs": {
                "densePointcloud": "{HololensPointcloudComposer_1.output}",
                "neighbourDistance": 0.05,
                "minNeighbours": 50,
                "verboseLevel": "info"
            },
            "outputs": {
                "output": "{cache}/{nodeType}/{uid0}//model.obj"
            }
        },
        "MatchingPairsSelector_1": {
            "nodeType": "MatchingPairsSelector",
            "position": [
                415,
                81
            ],
            "parallelization": {
                "blockSize": 0,
                "size": 1,
                "split": 1
            },
            "uids": {
                "0": "012bf86830d98b88781acdf6cf7915ca77f7c4dc"
            },
            "internalFolder": "{cache}/{nodeType}/{uid0}/",
            "inputs": {
                "sfmFile": "{HoloLensIO_1.output}",
                "inputSfMFormat": "COLMAP",
                "outputSfMFormat": "COLMAP",
                "minCommonPts": 200,
                "verboseLevel": "info"
            },
            "outputs": {
                "output": "{cache}/{nodeType}/{uid0}//image_pairs.txt"
            }
        },
        "HoloLensMatcher_1": {
            "nodeType": "HoloLensMatcher",
            "position": [
                583,
                -39
            ],
            "parallelization": {
                "blockSize": 0,
                "size": 1,
                "split": 1
            },
            "uids": {
                "0": "811f16ca6ed92da51c81cee73c30879b6bcb0f6b"
            },
            "internalFolder": "{cache}/{nodeType}/{uid0}/",
            "inputs": {
                "colmapSfM": "{HoloLensIO_1.output}",
                "imagesFolder": "{KeyframeSelector_1.output}",
                "imagePairs": "{MatchingPairsSelector_1.output}",
                "algorithm": "SIFT",
                "clusteringRadius": 1,
                "matchingTreshold": 10,
                "verboseLevel": "info"
            },
            "outputs": {
                "output": "{cache}/{nodeType}/{uid0}/"
            }
        },
        "ColmapMapper_1": {
            "nodeType": "ColmapMapper",
            "position": [
                766,
                -13
            ],
            "parallelization": {
                "blockSize": 0,
                "size": 1,
                "split": 1
            },
            "uids": {
                "0": "021b4a355a739dad4a6d468adfcaefe316814960"
            },
            "internalFolder": "{cache}/{nodeType}/{uid0}/",
            "inputs": {
                "colmapFolder": "{HoloLensMatcher_1.output}",
                "verboseLevel": "info"
            },
            "outputs": {
                "output": "{cache}/{nodeType}/{uid0}/"
            }
        },
        "ModelsAligner_1": {
            "nodeType": "ModelsAligner",
            "position": [
                965,
                7
            ],
            "parallelization": {
                "blockSize": 0,
                "size": 1,
                "split": 1
            },
            "uids": {
                "0": "6d75c3b281d2eb8027426b1b99377e2d3ae2e6f1"
            },
            "internalFolder": "{cache}/{nodeType}/{uid0}/",
            "inputs": {
                "sfmTransform": "{ColmapMapper_1.output}",
                "sfmReference": "{HoloLensIO_1.output}",
                "verboseLevel": "info"
            },
            "outputs": {
                "output": "{cache}/{nodeType}/{uid0}/"
            }
        },
        "ConvertSfMFormat_1": {
            "nodeType": "ConvertSfMFormat",
            "position": [
                1325,
                -91
            ],
            "parallelization": {
                "blockSize": 0,
                "size": 1,
                "split": 1
            },
            "uids": {
                "0": "0ccf7b246a3cbdda24ee85a16b469c7213750aa4"
            },
            "internalFolder": "{cache}/{nodeType}/{uid0}/",
            "inputs": {
                "containerName": "/local/artwin/mapping/codes/hololens_mapper/alicevision.sif",
                "containerPrefix": "/opt/AliceVision_install/bin/",
                "input": "{HoloLensIO_2.outputMeshroomSfM}",
                "fileExt": "abc",
                "describerTypes": [
                    "sift",
                    "unknown"
                ],
                "imageWhiteList": [],
                "views": true,
                "intrinsics": true,
                "extrinsics": true,
                "structure": true,
                "observations": true,
                "verboseLevel": "info"
            },
            "outputs": {
                "output": "{cache}/{nodeType}/{uid0}/sfm.{fileExtValue}"
            }
        },
        "PrepareDenseScene_1": {
            "nodeType": "PrepareDenseScene",
            "position": [
                1508,
                -110
            ],
            "parallelization": {
                "blockSize": 0,
                "size": 1,
                "split": 1
            },
            "uids": {
                "0": "453cb1174fd4137b3296e142884cca08e99b8da4"
            },
            "internalFolder": "{cache}/{nodeType}/{uid0}/",
            "inputs": {
                "containerName": "{ConvertSfMFormat_1.containerName}",
                "containerPrefix": "{ConvertSfMFormat_1.containerPrefix}",
                "input": "{ConvertSfMFormat_1.output}",
                "imagesFolders": [],
                "masksFolders": [],
                "outputFileType": "exr",
                "saveMetadata": true,
                "saveMatricesTxtFiles": false,
                "evCorrection": false,
                "verboseLevel": "info"
            },
            "outputs": {
                "output": "{cache}/{nodeType}/{uid0}/",
                "outputUndistorted": "{cache}/{nodeType}/{uid0}/*.{outputFileTypeValue}"
            }
        },
        "DepthMap_1": {
            "nodeType": "DepthMap",
            "position": [
                1705,
                -97
            ],
            "parallelization": {
                "blockSize": 3,
                "size": 1,
                "split": 1
            },
            "uids": {
                "0": "9fe6ff7d310892eb2f71928288f22860c6ca42ac"
            },
            "internalFolder": "{cache}/{nodeType}/{uid0}/",
            "inputs": {
                "containerName": "{PrepareDenseScene_1.containerName}",
                "containerPrefix": "{PrepareDenseScene_1.containerPrefix}",
                "input": "{PrepareDenseScene_1.input}",
                "imagesFolder": "{PrepareDenseScene_1.outputUndistorted}",
                "downscale": 2,
                "minViewAngle": 2.0,
                "maxViewAngle": 70.0,
                "sgmMaxTCams": 10,
                "sgmWSH": 4,
                "sgmGammaC": 5.5,
                "sgmGammaP": 8.0,
                "refineMaxTCams": 6,
                "refineNSamplesHalf": 150,
                "refineNDepthsToRefine": 31,
                "refineNiters": 100,
                "refineWSH": 3,
                "refineSigma": 15,
                "refineGammaC": 15.5,
                "refineGammaP": 8.0,
                "refineUseTcOrRcPixSize": false,
                "exportIntermediateResults": false,
                "nbGPUs": 0,
                "verboseLevel": "info"
            },
            "outputs": {
                "output": "{cache}/{nodeType}/{uid0}/"
            }
        },
        "DepthMapFilter_1": {
            "nodeType": "DepthMapFilter",
            "position": [
                1903,
                -97
            ],
            "parallelization": {
                "blockSize": 0,
                "size": 1,
                "split": 1
            },
            "uids": {
                "0": "835f7649c919981939be0fc6595aaa8489d81c44"
            },
            "internalFolder": "{cache}/{nodeType}/{uid0}/",
            "inputs": {
                "containerName": "{DepthMap_1.containerName}",
                "containerPrefix": "{DepthMap_1.containerPrefix}",
                "input": "{DepthMap_1.input}",
                "depthMapsFolder": "{DepthMap_1.output}",
                "minViewAngle": 2.0,
                "maxViewAngle": 70.0,
                "nNearestCams": 10,
                "minNumOfConsistentCams": 3,
                "minNumOfConsistentCamsWithLowSimilarity": 4,
                "pixSizeBall": 0,
                "pixSizeBallWithLowSimilarity": 0,
                "computeNormalMaps": false,
                "verboseLevel": "info"
            },
            "outputs": {
                "output": "{cache}/{nodeType}/{uid0}/"
            }
        },
        "Meshing_1": {
            "nodeType": "Meshing",
            "position": [
                2090,
                -108
            ],
            "parallelization": {
                "blockSize": 0,
                "size": 1,
                "split": 1
            },
            "uids": {
                "0": "afa5df98c9555370cc687c982f454326aa457340"
            },
            "internalFolder": "{cache}/{nodeType}/{uid0}/",
            "inputs": {
                "containerName": "{DepthMapFilter_1.containerName}",
                "containerPrefix": "{DepthMapFilter_1.containerPrefix}",
                "input": "{DepthMapFilter_1.input}",
                "depthMapsFolder": "{DepthMapFilter_1.output}",
                "outputMeshFileType": "obj",
                "useBoundingBox": false,
                "boundingBox": {
                    "bboxTranslation": {
                        "x": 0.0,
                        "y": 0.0,
                        "z": 0.0
                    },
                    "bboxRotation": {
                        "x": 0.0,
                        "y": 0.0,
                        "z": 0.0
                    },
                    "bboxScale": {
                        "x": 1.0,
                        "y": 1.0,
                        "z": 1.0
                    }
                },
                "estimateSpaceFromSfM": true,
                "estimateSpaceMinObservations": 3,
                "estimateSpaceMinObservationAngle": 10,
                "maxInputPoints": 50000000,
                "maxPoints": 5000000,
                "maxPointsPerVoxel": 1000000,
                "minStep": 2,
                "partitioning": "singleBlock",
                "repartition": "multiResolution",
                "angleFactor": 15.0,
                "simFactor": 15.0,
                "pixSizeMarginInitCoef": 2.0,
                "pixSizeMarginFinalCoef": 4.0,
                "voteMarginFactor": 4.0,
                "contributeMarginFactor": 2.0,
                "simGaussianSizeInit": 10.0,
                "simGaussianSize": 10.0,
                "minAngleThreshold": 1.0,
                "refineFuse": true,
                "helperPointsGridSize": 10,
                "densify": false,
                "densifyNbFront": 1,
                "densifyNbBack": 1,
                "densifyScale": 20.0,
                "nPixelSizeBehind": 4.0,
                "fullWeight": 1.0,
                "voteFilteringForWeaklySupportedSurfaces": true,
                "addLandmarksToTheDensePointCloud": false,
                "invertTetrahedronBasedOnNeighborsNbIterations": 10,
                "minSolidAngleRatio": 0.2,
                "nbSolidAngleFilteringIterations": 2,
                "colorizeOutput": true,
                "addMaskHelperPoints": false,
                "maskHelperPointsWeight": 1.0,
                "maskBorderSize": 4,
                "maxNbConnectedHelperPoints": 50,
                "saveRawDensePointCloud": true,
                "exportDebugTetrahedralization": false,
                "seed": 0,
                "verboseLevel": "info"
            },
            "outputs": {
                "outputMesh": "{cache}/{nodeType}/{uid0}/mesh.{outputMeshFileTypeValue}",
                "output": "{cache}/{nodeType}/{uid0}/densePointCloud.abc",
                "outputRAW": "{cache}/{nodeType}/{uid0}/densePointCloud_raw.abc"
            }
        },
        "HoloLensIO_1": {
            "nodeType": "HoloLensIO",
            "position": [
                242,
                32
            ],
            "parallelization": {
                "blockSize": 0,
                "size": 5,
                "split": 1
            },
            "uids": {
                "0": "156aff2fc2a1397397076e7f84cd0328c4bb8537"
            },
            "internalFolder": "{cache}/{nodeType}/{uid0}/",
            "inputs": {
                "inputFolder": "{KeyframeSelector_1.output}",
                "pointcloudFile": "{DensePointcloudFilter_1.output}",
                "hashScale": 10,
                "allPoints": false,
                "intrinsics": [
                    {
                        "intrinsicId": 0,
                        "csvPrefixes": [
                            "pv"
                        ],
                        "width": 1344,
                        "height": 756,
                        "pxFocalLength": {
                            "x": 1083.8628,
                            "y": 1082.8471
                        },
                        "principalPoint": {
                            "x": 665.5559,
                            "y": 400.5432
                        },
                        "distortionParams": [
                            -0.0168,
                            0.0044
                        ]
                    },
                    {
                        "intrinsicId": 1,
                        "csvPrefixes": [
                            "vlc_ll"
                        ],
                        "width": 480,
                        "height": 640,
                        "pxFocalLength": {
                            "x": 449.2613,
                            "y": 449.2928
                        },
                        "principalPoint": {
                            "x": 249.9525,
                            "y": 304.7976
                        },
                        "distortionParams": [
                            -0.03371,
                            0.0236
                        ]
                    },
                    {
                        "intrinsicId": 2,
                        "csvPrefixes": [
                            "vlc_lf"
                        ],
                        "width": 480,
                        "height": 640,
                        "pxFocalLength": {
                            "x": 458.5854,
                            "y": 454.1538
                        },
                        "principalPoint": {
                            "x": 233.5316,
                            "y": 324.1116
                        },
                        "distortionParams": [
                            -0.00717,
                            0.00725
                        ]
                    },
                    {
                        "intrinsicId": 3,
                        "csvPrefixes": [
                            "vlc_rf"
                        ],
                        "width": 480,
                        "height": 640,
                        "pxFocalLength": {
                            "x": 460.7706,
                            "y": 456.1151
                        },
                        "principalPoint": {
                            "x": 257.1324,
                            "y": 320.1994
                        },
                        "distortionParams": [
                            -0.0102,
                            0.0194
                        ]
                    },
                    {
                        "intrinsicId": 4,
                        "csvPrefixes": [
                            "vlc_rr"
                        ],
                        "width": 480,
                        "height": 640,
                        "pxFocalLength": {
                            "x": 445.7555,
                            "y": 445.6442
                        },
                        "principalPoint": {
                            "x": 240.7121,
                            "y": 313.0296
                        },
                        "distortionParams": [
                            -0.02997,
                            0.01758
                        ]
                    }
                ],
                "inputSfMFormat": "HoloLens",
                "outputSfMFormat": "COLMAP",
                "cpoyImagesToOutput": false,
                "imagesPath": "original",
                "verboseLevel": "info"
            },
            "outputs": {
                "output": "{cache}/{nodeType}/{uid0}/",
                "outputMeshroomSfM": "{cache}/{nodeType}/{uid0}/meshroom_sfm.json"
            }
        },
        "DensePonitcloudsAligner_1": {
            "nodeType": "DensePonitcloudsAligner",
            "position": [
                2453,
                90
            ],
            "parallelization": {
                "blockSize": 0,
                "size": 1,
                "split": 1
            },
            "uids": {
                "0": "11d146f184bba618f41fbb0a970a03010c9b420a"
            },
            "internalFolder": "{cache}/{nodeType}/{uid0}/",
            "inputs": {
                "inputPointcloud1": "{ConvertSfMFormat_2.output}",
                "inputPointcloud2": "{DensePointcloudFilter_1.output}",
                "alignmentMehod": "concatenation",
                "verboseLevel": "info"
            },
            "outputs": {
                "output": "{cache}/{nodeType}/{uid0}//model.obj"
            }
        },
        "Texturing_1": {
            "nodeType": "Texturing",
            "position": [
                3658,
                12
            ],
            "parallelization": {
                "blockSize": 0,
                "size": 1,
                "split": 1
            },
            "uids": {
                "0": "f63b531aed564db95d92daee6b24b6c8a707c6fa"
            },
            "internalFolder": "{cache}/{nodeType}/{uid0}/",
            "inputs": {
                "containerName": "{MeshFiltering_1.containerName}",
                "containerPrefix": "{MeshFiltering_1.containerPrefix}",
                "input": "{HoloLensIO_4.outputMeshroomSfM}",
                "imagesFolder": "",
                "inputMesh": "{MeshFiltering_1.outputMesh}",
                "inputRefMesh": "",
                "textureSide": 8192,
                "downscale": 2,
                "outputMeshFileType": "obj",
                "colorMapping": {
                    "enable": true,
                    "colorMappingFileType": "exr"
                },
                "bumpMapping": {
                    "enable": true,
                    "bumpType": "Normal",
                    "normalFileType": "exr",
                    "heightFileType": "exr"
                },
                "displacementMapping": {
                    "enable": true,
                    "displacementMappingFileType": "exr"
                },
                "unwrapMethod": "Basic",
                "useUDIM": true,
                "fillHoles": true,
                "padding": 5,
                "multiBandDownscale": 4,
                "multiBandNbContrib": {
                    "high": 1,
                    "midHigh": 5,
                    "midLow": 10,
                    "low": 0
                },
                "useScore": true,
                "bestScoreThreshold": 0.1,
                "angleHardThreshold": 90.0,
                "processColorspace": "sRGB",
                "correctEV": false,
                "forceVisibleByAllVertices": false,
                "flipNormals": false,
                "visibilityRemappingMethod": "PullPush",
                "subdivisionTargetRatio": 0.8,
                "verboseLevel": "info"
            },
            "outputs": {
                "output": "{cache}/{nodeType}/{uid0}/",
                "outputMesh": "{cache}/{nodeType}/{uid0}/texturedMesh.{outputMeshFileTypeValue}",
                "outputMaterial": "{cache}/{nodeType}/{uid0}/texturedMesh.mtl",
                "outputTextures": "{cache}/{nodeType}/{uid0}/texture_*.exr"
            }
        },
        "MeshFiltering_1": {
            "nodeType": "MeshFiltering",
            "position": [
                3447,
                -47
            ],
            "parallelization": {
                "blockSize": 0,
                "size": 1,
                "split": 1
            },
            "uids": {
                "0": "40ca51bb6dbfeb90b66fc0d7dc08f3dca96edf42"
            },
            "internalFolder": "{cache}/{nodeType}/{uid0}/",
            "inputs": {
                "containerName": "{Meshing_2.containerName}",
                "containerPrefix": "{Meshing_2.containerPrefix}",
                "inputMesh": "{Meshing_2.outputMesh}",
                "outputMeshFileType": "obj",
                "keepLargestMeshOnly": false,
                "smoothingSubset": "all",
                "smoothingBoundariesNeighbours": 0,
                "smoothingIterations": 5,
                "smoothingLambda": 1.0,
                "filteringSubset": "all",
                "filteringIterations": 1,
                "filterLargeTrianglesFactor": 60.0,
                "filterTrianglesRatio": 0.0,
                "verboseLevel": "info"
            },
            "outputs": {
                "outputMesh": "{cache}/{nodeType}/{uid0}/mesh.{outputMeshFileTypeValue}"
            }
        },
        "FilterColmapSfM_1": {
            "nodeType": "FilterColmapSfM",
            "position": [
                3002,
                192
            ],
            "parallelization": {
                "blockSize": 0,
                "size": 1,
                "split": 1
            },
            "uids": {
                "0": "7c4f7576ff30fa481f5587f7d99d47a6e9eef427"
            },
            "internalFolder": "{cache}/{nodeType}/{uid0}/",
            "inputs": {
                "inputFolder": "{HoloLensIO_3.inputFolder}",
                "subsamplePoints3D": false,
                "numberOfPoints3D": 1000,
                "minNumberOfObservations": 50,
                "filterPV": false,
                "filterVLC": true,
                "cpoyImagesToOutput": true,
                "verboseLevel": "info"
            },
            "outputs": {
                "output": "{cache}/{nodeType}/{uid0}/"
            }
        },
        "ConvertSfMFormat_2": {
            "nodeType": "ConvertSfMFormat",
            "position": [
                2281,
                -102
            ],
            "parallelization": {
                "blockSize": 0,
                "size": 1,
                "split": 1
            },
            "uids": {
                "0": "79e8032337126c7066f25fd34dc50d8fe7ca1f52"
            },
            "internalFolder": "{cache}/{nodeType}/{uid0}/",
            "inputs": {
                "containerName": "{Meshing_1.containerName}",
                "containerPrefix": "{Meshing_1.containerPrefix}",
                "input": "{Meshing_1.output}",
                "fileExt": "ply",
                "describerTypes": [
                    "dspsift",
                    "unknown",
                    "sift"
                ],
                "imageWhiteList": [],
                "views": true,
                "intrinsics": true,
                "extrinsics": true,
                "structure": true,
                "observations": true,
                "verboseLevel": "info"
            },
            "outputs": {
                "output": "{cache}/{nodeType}/{uid0}/sfm.{fileExtValue}"
            }
        },
        "HoloLensIO_2": {
            "nodeType": "HoloLensIO",
            "position": [
                1139,
                -80
            ],
            "parallelization": {
                "blockSize": 0,
                "size": 0,
                "split": 1
            },
            "uids": {
                "0": "baaefb11964921b3505d22672f360aec0cb19d67"
            },
            "internalFolder": "{cache}/{nodeType}/{uid0}/",
            "inputs": {
                "inputFolder": "{ModelsAligner_1.output}",
                "pointcloudFile": "",
                "hashScale": 1,
                "allPoints": false,
                "intrinsics": [],
                "inputSfMFormat": "COLMAP",
                "outputSfMFormat": "Meshroom",
                "cpoyImagesToOutput": true,
                "imagesPath": "container",
                "verboseLevel": "info"
            },
            "outputs": {
                "output": "{cache}/{nodeType}/{uid0}/",
                "outputMeshroomSfM": "{cache}/{nodeType}/{uid0}/meshroom_sfm.json"
            }
        },
        "DensePointcloudFilter_2": {
            "nodeType": "DensePointcloudFilter",
            "position": [
                2641,
                91
            ],
            "parallelization": {
                "blockSize": 0,
                "size": 1,
                "split": 1
            },
            "uids": {
                "0": "d4bb678e59b9ff6a34d41205d8709b9d3512cebe"
            },
            "internalFolder": "{cache}/{nodeType}/{uid0}/",
            "inputs": {
                "densePointcloud": "{DensePonitcloudsAligner_1.output}",
                "neighbourDistance": 0.05,
                "minNeighbours": 30,
                "verboseLevel": "info"
            },
            "outputs": {
                "output": "{cache}/{nodeType}/{uid0}//model.obj"
            }
        },
        "Meshing_2": {
            "nodeType": "Meshing",
            "position": [
                3088,
                -101
            ],
            "parallelization": {
                "blockSize": 0,
                "size": 1,
                "split": 1
            },
            "uids": {
                "0": "8d38eb0a7ee969912a6f96ce12b0d0a0e05a75d2"
            },
            "internalFolder": "{cache}/{nodeType}/{uid0}/",
            "inputs": {
                "containerName": "{ConvertSfMFormat_2.containerName}",
                "containerPrefix": "{ConvertSfMFormat_2.containerPrefix}",
                "input": "{HoloLensIO_3.outputMeshroomSfM}",
                "depthMapsFolder": "",
                "outputMeshFileType": "obj",
                "useBoundingBox": false,
                "boundingBox": {
                    "bboxTranslation": {
                        "x": 0.0,
                        "y": 0.0,
                        "z": 0.0
                    },
                    "bboxRotation": {
                        "x": 0.0,
                        "y": 0.0,
                        "z": 0.0
                    },
                    "bboxScale": {
                        "x": 1.0,
                        "y": 1.0,
                        "z": 1.0
                    }
                },
                "estimateSpaceFromSfM": true,
                "estimateSpaceMinObservations": 3,
                "estimateSpaceMinObservationAngle": 10,
                "maxInputPoints": 50000000,
                "maxPoints": 5000000,
                "maxPointsPerVoxel": 1000000,
                "minStep": 2,
                "partitioning": "singleBlock",
                "repartition": "multiResolution",
                "angleFactor": 15.0,
                "simFactor": 15.0,
                "pixSizeMarginInitCoef": 2.0,
                "pixSizeMarginFinalCoef": 4.0,
                "voteMarginFactor": 4.0,
                "contributeMarginFactor": 2.0,
                "simGaussianSizeInit": 10.0,
                "simGaussianSize": 10.0,
                "minAngleThreshold": 1.0,
                "refineFuse": true,
                "helperPointsGridSize": 10,
                "densify": false,
                "densifyNbFront": 1,
                "densifyNbBack": 1,
                "densifyScale": 20.0,
                "nPixelSizeBehind": 4.0,
                "fullWeight": 1.0,
                "voteFilteringForWeaklySupportedSurfaces": true,
                "addLandmarksToTheDensePointCloud": true,
                "invertTetrahedronBasedOnNeighborsNbIterations": 10,
                "minSolidAngleRatio": 0.2,
                "nbSolidAngleFilteringIterations": 2,
                "colorizeOutput": true,
                "addMaskHelperPoints": false,
                "maskHelperPointsWeight": 1.0,
                "maskBorderSize": 4,
                "maxNbConnectedHelperPoints": 50,
                "saveRawDensePointCloud": true,
                "exportDebugTetrahedralization": false,
                "seed": 0,
                "verboseLevel": "info"
            },
            "outputs": {
                "outputMesh": "{cache}/{nodeType}/{uid0}/mesh.{outputMeshFileTypeValue}",
                "output": "{cache}/{nodeType}/{uid0}/densePointCloud.abc",
                "outputRAW": "{cache}/{nodeType}/{uid0}/densePointCloud_raw.abc"
            }
        },
        "HoloLensIO_3": {
            "nodeType": "HoloLensIO",
            "position": [
                2824,
                18
            ],
            "parallelization": {
                "blockSize": 0,
                "size": 0,
                "split": 1
            },
            "uids": {
                "0": "271cfcd5de0674f0ffd29291aa347b19abc5f9f0"
            },
            "internalFolder": "{cache}/{nodeType}/{uid0}/",
            "inputs": {
                "inputFolder": "{ModelsAligner_1.output}",
                "pointcloudFile": "{DensePointcloudFilter_2.output}",
                "hashScale": 100,
                "allPoints": false,
                "intrinsics": [],
                "inputSfMFormat": "COLMAP",
                "outputSfMFormat": "Meshroom",
                "cpoyImagesToOutput": true,
                "imagesPath": "container",
                "verboseLevel": "info"
            },
            "outputs": {
                "output": "{cache}/{nodeType}/{uid0}/",
                "outputMeshroomSfM": "{cache}/{nodeType}/{uid0}/meshroom_sfm.json"
            }
        },
        "HoloLensIO_4": {
            "nodeType": "HoloLensIO",
            "position": [
                3450,
                160
            ],
            "parallelization": {
                "blockSize": 0,
                "size": 0,
                "split": 1
            },
            "uids": {
                "0": "512a192d10248ed3e1ac1b8057d13636401bc325"
            },
            "internalFolder": "{cache}/{nodeType}/{uid0}/",
            "inputs": {
                "inputFolder": "{FilterColmapSfM_1.output}",
                "pointcloudFile": "{ConvertSfMFormat_3.output}",
                "hashScale": 100,
                "allPoints": true,
                "intrinsics": [],
                "inputSfMFormat": "COLMAP",
                "outputSfMFormat": "Meshroom",
                "cpoyImagesToOutput": true,
                "imagesPath": "container",
                "verboseLevel": "info"
            },
            "outputs": {
                "output": "{cache}/{nodeType}/{uid0}/",
                "outputMeshroomSfM": "{cache}/{nodeType}/{uid0}/meshroom_sfm.json"
            }
        },
        "ConvertSfMFormat_3": {
            "nodeType": "ConvertSfMFormat",
            "position": [
                3266,
                64
            ],
            "parallelization": {
                "blockSize": 0,
                "size": 1,
                "split": 1
            },
            "uids": {
                "0": "d891663bbbcd7c1a43840261fabdfa7297d8bc37"
            },
            "internalFolder": "{cache}/{nodeType}/{uid0}/",
            "inputs": {
                "containerName": "",
                "containerPrefix": "",
                "input": "{Meshing_2.output}",
                "fileExt": "ply",
                "describerTypes": [
                    "sift",
                    "unknown"
                ],
                "imageWhiteList": [],
                "views": false,
                "intrinsics": false,
                "extrinsics": false,
                "structure": true,
                "observations": false,
                "verboseLevel": "info"
            },
            "outputs": {
                "output": "{cache}/{nodeType}/{uid0}/sfm.{fileExtValue}"
            }
        }
    }
}