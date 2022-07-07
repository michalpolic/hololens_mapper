{
    "header": {
        "pipelineVersion": "2.2",
        "releaseVersion": "2021.1.0",
        "fileVersion": "1.1",
        "nodesVersions": {
            "KeypointsDetector": "0.1",
            "DensePointcloudFilter": "0.1",
            "DensePonitcloudsConcatenator": "0.1",
            "MatchingPairsSelector": "0.1",
            "Patchmatchnet": "0.1",
            "PointcloudComposer": "0.1",
            "ModelsAligner": "0.1",
            "Mapper": "0.1",
            "Matcher": "0.1",
            "KeyframeSelector": "0.1",
            "IOConvertor": "0.1",
            "HlocMapCreator": "0.1",
            "TentativeMatcher": "0.1"
        }
    },
    "graph": {
        "TentativeMatcher_1": {
            "nodeType": "TentativeMatcher",
            "position": [
                781,
                14
            ],
            "parallelization": {
                "blockSize": 0,
                "size": 1,
                "split": 1
            },
            "uids": {
                "0": "3eaadb3e9ca47b8d96f656d13a64af706f860d4c"
            },
            "internalFolder": "{cache}/{nodeType}/{uid0}/",
            "inputs": {
                "sfmfolder": "{IOConvertor_1.output}",
                "databaseFile": "{KeypointsDetector_1.output}",
                "imagesFolder": "{KeypointsDetector_1.imagesFolder}",
                "imagePairs": "{MatchingPairsSelector_1.output}",
                "algorithm": "COLMAP",
                "matchingTreshold": 10,
                "removeImages": true,
                "verboseLevel": "info"
            },
            "outputs": {
                "output": "{cache}/{nodeType}/{uid0}/",
                "databaseOutputFile": "{cache}/{nodeType}/{uid0}/database.db",
                "tentativeMatches": "{cache}/{nodeType}/{uid0}/tentative_matches.txt"
            }
        },
        "MatchingPairsSelector_1": {
            "nodeType": "MatchingPairsSelector",
            "position": [
                593,
                134
            ],
            "parallelization": {
                "blockSize": 0,
                "size": 1,
                "split": 1
            },
            "uids": {
                "0": "615f01436948e91371eec13459231a0b2675a37d"
            },
            "internalFolder": "{cache}/{nodeType}/{uid0}/",
            "inputs": {
                "sfm": "{IOConvertor_1.output}",
                "inputSfMFormat": "COLMAP",
                "outputSfMFormat": "image pairs",
                "minCommonPts": 200,
                "verboseLevel": "info"
            },
            "outputs": {
                "output": "{cache}/{nodeType}/{uid0}//image_pairs.txt"
            }
        },
        "DensePointcloudFilter_1": {
            "nodeType": "DensePointcloudFilter",
            "position": [
                1346,
                245
            ],
            "parallelization": {
                "blockSize": 0,
                "size": 1,
                "split": 1
            },
            "uids": {
                "0": "d8a5798a1d1ac66cdda0f875531527c8310e1ecb"
            },
            "internalFolder": "{cache}/{nodeType}/{uid0}/",
            "inputs": {
                "densePointcloud": "{IOConvertor_1.pointcloudFile}",
                "neighbourDistance": 0.05,
                "minNeighbours": 50,
                "verboseLevel": "info"
            },
            "outputs": {
                "output": "{cache}/{nodeType}/{uid0}//model.obj"
            }
        },
        "Matcher_1": {
            "nodeType": "Matcher",
            "position": [
                984,
                16
            ],
            "parallelization": {
                "blockSize": 0,
                "size": 1,
                "split": 1
            },
            "uids": {
                "0": "051191c45c5360b3958e832a5a757d5c038228f8"
            },
            "internalFolder": "{cache}/{nodeType}/{uid0}/",
            "inputs": {
                "databaseFile": "{TentativeMatcher_1.databaseOutputFile}",
                "inputMatchesFormat": "image pairs + tentative matches",
                "inputMatches": "{TentativeMatcher_1.tentativeMatches}",
                "algorithm": "COLMAP",
                "matchingTreshold": 2,
                "verboseLevel": "info"
            },
            "outputs": {
                "output": "{cache}/{nodeType}/{uid0}/",
                "databaseOutputFile": "{cache}/{nodeType}/{uid0}/database.db"
            }
        },
        "Patchmatchnet_1": {
            "nodeType": "Patchmatchnet",
            "position": [
                1548,
                115
            ],
            "parallelization": {
                "blockSize": 0,
                "size": 1,
                "split": 1
            },
            "uids": {
                "0": "7e435ec24b0a2250fe427b624b11c994c257993f"
            },
            "internalFolder": "{cache}/{nodeType}/{uid0}/",
            "inputs": {
                "colmapFolder": "{ModelsAligner_2.output}",
                "verboseLevel": "info"
            },
            "outputs": {
                "output": "{cache}/{nodeType}/{uid0}/",
                "outputPLY": "{cache}/{nodeType}/{uid0}//fused.ply"
            }
        },
        "KeypointsDetector_1": {
            "nodeType": "KeypointsDetector",
            "position": [
                592,
                -99
            ],
            "parallelization": {
                "blockSize": 0,
                "size": 1,
                "split": 1
            },
            "uids": {
                "0": "9153041efac2bd8764f0e1e5852819810e301924"
            },
            "internalFolder": "{cache}/{nodeType}/{uid0}/",
            "inputs": {
                "imagesFolder": "{IOConvertor_1.output}",
                "database": "",
                "algorithm": "SIFT",
                "removeImages": true,
                "verboseLevel": "info"
            },
            "outputs": {
                "output": "{cache}/{nodeType}/{uid0}/database.db"
            }
        },
        "DensePonitcloudsConcatenator_1": {
            "nodeType": "DensePonitcloudsConcatenator",
            "position": [
                1741,
                193
            ],
            "parallelization": {
                "blockSize": 0,
                "size": 1,
                "split": 1
            },
            "uids": {
                "0": "f82885275b635e22949847045f0858cb020cc3e3"
            },
            "internalFolder": "{cache}/{nodeType}/{uid0}/",
            "inputs": {
                "pointcloud1": "{Patchmatchnet_1.outputPLY}",
                "pointcloud2": "{DensePointcloudFilter_1.output}",
                "verboseLevel": "info"
            },
            "outputs": {
                "output": "{cache}/{nodeType}/{uid0}//model.obj"
            }
        },
        "ModelsAligner_2": {
            "nodeType": "ModelsAligner",
            "position": [
                1349,
                116
            ],
            "parallelization": {
                "blockSize": 0,
                "size": 1,
                "split": 1
            },
            "uids": {
                "0": "72b054287452a19d943cb2bc1ddc50e08b22a4b9"
            },
            "internalFolder": "{cache}/{nodeType}/{uid0}/",
            "inputs": {
                "sfmTransform": "{Mapper_1.output}",
                "ptsTransform": "",
                "sfmReference": "{IOConvertor_1.output}",
                "alignerType": [
                    "sfm"
                ],
                "verboseLevel": "info"
            },
            "outputs": {
                "output": "{cache}/{nodeType}/{uid0}/",
                "transforedPts": "{cache}/{nodeType}/{uid0}/model.obj"
            }
        },
        "HlocMapCreator_1": {
            "nodeType": "HlocMapCreator",
            "position": [
                2129,
                99
            ],
            "parallelization": {
                "blockSize": 0,
                "size": 1,
                "split": 1
            },
            "uids": {
                "0": "a91a81ec2a478e8769e86e5eb2c20bc1b60cf675"
            },
            "internalFolder": "{cache}/{nodeType}/{uid0}/",
            "inputs": {
                "inputSfM": "{IOConvertor_4.output}",
                "imageDirectory": "{IOConvertor_4.output}",
                "imageFolderNames": "",
                "copyDensePts": true,
                "verboseLevel": "info"
            },
            "outputs": {
                "output": "{cache}/{nodeType}/{uid0}/"
            }
        },
        "IOConvertor_4": {
            "nodeType": "IOConvertor",
            "position": [
                1932,
                100
            ],
            "parallelization": {
                "blockSize": 0,
                "size": 0,
                "split": 1
            },
            "uids": {
                "0": "8f0fdcd8d26d23c43f56a9d116c390558dcb6da6"
            },
            "internalFolder": "{cache}/{nodeType}/{uid0}/",
            "inputs": {
                "inputFolder": "{Patchmatchnet_1.colmapFolder}",
                "pointcloudFile": "{DensePonitcloudsConcatenator_1.output}",
                "hashScale": 100,
                "renderScale": 1,
                "allPoints": false,
                "intrinsics": [],
                "inputSfMFormat": "COLMAP",
                "outputSfMFormat": [
                    "COLMAP",
                    "OBJ"
                ],
                "copyImagesToOutput": true,
                "convertImgsToJpeg": false,
                "imagesPath": "original",
                "verboseLevel": "info"
            },
            "outputs": {
                "output": "{cache}/{nodeType}/{uid0}/",
                "outputMeshroomSfM": "{cache}/{nodeType}/{uid0}/meshroom_sfm.json",
                "lQueryFile": "{cache}/{nodeType}/{uid0}/hloc_queries.txt",
                "densePts": "{cache}/{nodeType}/{uid0}/model.obj"
            }
        },
        "IOConvertor_1": {
            "nodeType": "IOConvertor",
            "position": [
                248,
                184
            ],
            "parallelization": {
                "blockSize": 0,
                "size": 5,
                "split": 1
            },
            "uids": {
                "0": "d32c41153bb6b178c264fe23da8b07211c4e0e9a"
            },
            "internalFolder": "{cache}/{nodeType}/{uid0}/",
            "inputs": {
                "inputFolder": "{KeyframeSelector_2.output}",
                "pointcloudFile": "{PointcloudComposer_1.output}",
                "hashScale": 10,
                "renderScale": 1,
                "allPoints": false,
                "intrinsics": [
                    {
                        "intrinsicId": 0,
                        "trackingFile": "pv",
                        "width": 760,
                        "height": 428,
                        "pxFocalLength": {
                            "x": 585.7849,
                            "y": 583.6563
                        },
                        "principalPoint": {
                            "x": 376.3103,
                            "y": 196.7361
                        },
                        "distortionParams": [
                            0.0028,
                            -0.0125
                        ]
                    },
                    {
                        "intrinsicId": 1,
                        "trackingFile": "vlc_lf",
                        "width": 640,
                        "height": 480,
                        "pxFocalLength": {
                            "x": 363.2337,
                            "y": 365.0553
                        },
                        "principalPoint": {
                            "x": 319.4072,
                            "y": 241.7827
                        },
                        "distortionParams": [
                            -0.0136,
                            0.0082
                        ]
                    },
                    {
                        "intrinsicId": 2,
                        "trackingFile": "vlc_ll",
                        "width": 640,
                        "height": 480,
                        "pxFocalLength": {
                            "x": 365.7522,
                            "y": 366.1228
                        },
                        "principalPoint": {
                            "x": 317.4559,
                            "y": 235.186
                        },
                        "distortionParams": [
                            -0.0154,
                            0.0129
                        ]
                    },
                    {
                        "intrinsicId": 3,
                        "trackingFile": "vlc_rf",
                        "width": 640,
                        "height": 480,
                        "pxFocalLength": {
                            "x": 365.3355,
                            "y": 366.6003
                        },
                        "principalPoint": {
                            "x": 317.4216,
                            "y": 239.2051
                        },
                        "distortionParams": [
                            -0.016,
                            0.0146
                        ]
                    },
                    {
                        "intrinsicId": 4,
                        "trackingFile": "vlc_rr",
                        "width": 640,
                        "height": 480,
                        "pxFocalLength": {
                            "x": 365.3515,
                            "y": 365.8378
                        },
                        "principalPoint": {
                            "x": 316.0903,
                            "y": 235.9292
                        },
                        "distortionParams": [
                            -0.0152,
                            0.0129
                        ]
                    }
                ],
                "inputSfMFormat": "HoloLens2",
                "outputSfMFormat": [
                    "COLMAP"
                ],
                "copyImagesToOutput": true,
                "convertImgsToJpeg": true,
                "imagesPath": "original",
                "verboseLevel": "info"
            },
            "outputs": {
                "output": "{cache}/{nodeType}/{uid0}/",
                "outputMeshroomSfM": "{cache}/{nodeType}/{uid0}/meshroom_sfm.json",
                "lQueryFile": "{cache}/{nodeType}/{uid0}/hloc_queries.txt",
                "densePts": "{cache}/{nodeType}/{uid0}/model.obj"
            }
        },
        "PointcloudComposer_1": {
            "nodeType": "PointcloudComposer",
            "position": [
                -134,
                94
            ],
            "parallelization": {
                "blockSize": 0,
                "size": 0,
                "split": 1
            },
            "uids": {
                "0": "0331ac16ede08e9c47a6748d0e288d502a281615"
            },
            "internalFolder": "{cache}/{nodeType}/{uid0}/",
            "inputs": {
                "recordingDir": "/local1/projects/artwin/datasets/LocalizaitonSmall",
                "recordingSource": "HoloLens2",
                "mindepth": 0.0,
                "maxdepth": 25.0,
                "parameters": [],
                "verboseLevel": "info"
            },
            "outputs": {
                "output": "{cache}/{nodeType}/{uid0}//model.obj"
            }
        },
        "KeyframeSelector_2": {
            "nodeType": "KeyframeSelector",
            "position": [
                66,
                20
            ],
            "parallelization": {
                "blockSize": 0,
                "size": 1,
                "split": 1
            },
            "uids": {
                "0": "80c07c3dd369510d1759e7b04afb49c590198e6a"
            },
            "internalFolder": "{cache}/{nodeType}/{uid0}/",
            "inputs": {
                "recordingDir": "{PointcloudComposer_1.recordingDir}",
                "imageFolderNames": "",
                "recordingSource": "{PointcloudComposer_1.recordingSource}",
                "pvBlurThreshold": 15.0,
                "pvMinFrameOffset": 5,
                "vlcMinFrameOffset": 5,
                "verboseLevel": "info"
            },
            "outputs": {
                "output": "{cache}/{nodeType}/{uid0}/"
            }
        },
        "Mapper_1": {
            "nodeType": "Mapper",
            "position": [
                1174,
                62
            ],
            "parallelization": {
                "blockSize": 0,
                "size": 1,
                "split": 1
            },
            "uids": {
                "0": "71cd636f6ce480ad08cdec7769d3255bbd3fc14e"
            },
            "internalFolder": "{cache}/{nodeType}/{uid0}/",
            "inputs": {
                "databaseFile": "{Matcher_1.databaseOutputFile}",
                "imagesDirectory": "{IOConvertor_1.output}",
                "algorithm": "COLMAP",
                "verboseLevel": "info"
            },
            "outputs": {
                "output": "{cache}/{nodeType}/{uid0}/"
            }
        }
    }
}