{
    "header": {
        "pipelineVersion": "2.2",
        "releaseVersion": "2021.1.0",
        "fileVersion": "1.1",
        "nodesVersions": {
            "PointcloudComposer": "0.1",
            "TentativeMatcher": "0.1",
            "HoloLens2Downloader": "0.1",
            "KeyframeSelector": "0.1",
            "DensePonitcloudsConcatenator": "0.1",
            "DensePointcloudFilter": "0.1",
            "HoloLens1Downloader": "0.1",
            "Patchmatchnet": "0.1",
            "HlocLocalizer": "0.1",
            "ModelsAligner": "0.1",
            "KeypointsDetector": "0.1",
            "MatchingPairsSelector": "0.1",
            "IOConvertor": "0.1",
            "Matcher": "0.1",
            "Mapper": "0.1"
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
                "0": "b27ead06883d9c21327beb0a7755d63afa8b381c"
            },
            "internalFolder": "{cache}/{nodeType}/{uid0}/",
            "inputs": {
                "sfmfolder": "{IOConvertor_1.output}",
                "databaseFile": "{KeypointsDetector_1.output}",
                "imagesFolder": "{IOConvertor_1.output}",
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
        "HoloLens1Downloader_1": {
            "nodeType": "HoloLens1Downloader",
            "position": [
                -369,
                34
            ],
            "parallelization": {
                "blockSize": 0,
                "size": 1,
                "split": 1
            },
            "uids": {
                "0": "2ddb0fb61d0606a976d335dba39ec0c903da500f"
            },
            "internalFolder": "{cache}/{nodeType}/{uid0}/",
            "inputs": {
                "username": "",
                "password": "",
                "ip": "",
                "recordingsFolder": "",
                "download": true,
                "delete": false,
                "verboseLevel": "info"
            },
            "outputs": {}
        },
        "HoloLens2Downloader_1": {
            "nodeType": "HoloLens2Downloader",
            "position": [
                -373,
                102
            ],
            "parallelization": {
                "blockSize": 0,
                "size": 1,
                "split": 1
            },
            "uids": {
                "0": "2ddb0fb61d0606a976d335dba39ec0c903da500f"
            },
            "internalFolder": "{cache}/{nodeType}/{uid0}/",
            "inputs": {
                "username": "",
                "password": "",
                "ip": "",
                "recordingsFolder": "",
                "download": true,
                "delete": false,
                "verboseLevel": "info"
            },
            "outputs": {}
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
                "0": "09fbfc0321fdd0afc67398004c272a19714df722"
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
                3011,
                213
            ],
            "parallelization": {
                "blockSize": 0,
                "size": 1,
                "split": 1
            },
            "uids": {
                "0": "bd25b5a7c4e8806ca326c0910ad27e54bffbf926"
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
                "0": "d281d40e85fc5f3a85ab335423de3c4ffcb39388"
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
                3207,
                -13
            ],
            "parallelization": {
                "blockSize": 0,
                "size": 1,
                "split": 1
            },
            "uids": {
                "0": "1bb144d1b9d5cd638a87ba7f0f60b0c4075c1d88"
            },
            "internalFolder": "{cache}/{nodeType}/{uid0}/",
            "inputs": {
                "colmapFolder": "{ModelsAligner_3.output}",
                "verboseLevel": "info"
            },
            "outputs": {
                "output": "{cache}/{nodeType}/{uid0}/",
                "outputPLY": "{cache}/{nodeType}/{uid0}//fused.ply"
            }
        },
        "ModelsAligner_1": {
            "nodeType": "ModelsAligner",
            "position": [
                3200,
                134
            ],
            "parallelization": {
                "blockSize": 0,
                "size": 1,
                "split": 1
            },
            "uids": {
                "0": "fca25f0eb357ea94c2f49036e6cfcc6594f62439"
            },
            "internalFolder": "{cache}/{nodeType}/{uid0}/",
            "inputs": {
                "sfmTransform": "{ModelsAligner_2.sfmReference}",
                "ptsTransform": "{DensePointcloudFilter_1.output}",
                "sfmReference": "{ModelsAligner_3.output}",
                "alignerType": [
                    "pointcloud"
                ],
                "verboseLevel": "info"
            },
            "outputs": {
                "output": "{cache}/{nodeType}/{uid0}/",
                "transforedPts": "{cache}/{nodeType}/{uid0}/model.obj"
            }
        },
        "DensePonitcloudsConcatenator_1": {
            "nodeType": "DensePonitcloudsConcatenator",
            "position": [
                3418,
                68
            ],
            "parallelization": {
                "blockSize": 0,
                "size": 1,
                "split": 1
            },
            "uids": {
                "0": "3c29853357c46baee2611da1a8e74d24a6915531"
            },
            "internalFolder": "{cache}/{nodeType}/{uid0}/",
            "inputs": {
                "pointcloud1": "{Patchmatchnet_1.outputPLY}",
                "pointcloud2": "{ModelsAligner_1.transforedPts}",
                "verboseLevel": "info"
            },
            "outputs": {
                "output": "{cache}/{nodeType}/{uid0}//model.obj"
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
                "0": "ab4fa1196468690095e841222450e7e6d5955232"
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
                "0": "916b0d5377e72467cb8915a0200c483f9b0ebc6e"
            },
            "internalFolder": "{cache}/{nodeType}/{uid0}/",
            "inputs": {
                "recordingDir": "/local1/projects/artwin/datasets/LibrarySmall_Holo2",
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
                "0": "626e5c71edf6e8211887247ffe17a26076621f66"
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
                "0": "9d627dd0f0e7a040771ced8f605c9dfb28aa8bbc"
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
        },
        "Matcher_2": {
            "nodeType": "Matcher",
            "position": [
                2500,
                -138
            ],
            "parallelization": {
                "blockSize": 0,
                "size": 1,
                "split": 1
            },
            "uids": {
                "0": "38cb4a70c2dea55e9245b1d6a7411c178f116284"
            },
            "internalFolder": "{cache}/{nodeType}/{uid0}/",
            "inputs": {
                "databaseFile": "{TentativeMatcher_2.databaseOutputFile}",
                "inputMatchesFormat": "image pairs + tentative matches",
                "inputMatches": "{TentativeMatcher_2.tentativeMatches}",
                "algorithm": "COLMAP",
                "matchingTreshold": 2,
                "verboseLevel": "info"
            },
            "outputs": {
                "output": "{cache}/{nodeType}/{uid0}/",
                "databaseOutputFile": "{cache}/{nodeType}/{uid0}/database.db"
            }
        },
        "TentativeMatcher_2": {
            "nodeType": "TentativeMatcher",
            "position": [
                2300,
                -226
            ],
            "parallelization": {
                "blockSize": 0,
                "size": 1,
                "split": 1
            },
            "uids": {
                "0": "aff2ed33f7fe33caae3b2d329711d08a3569e3a6"
            },
            "internalFolder": "{cache}/{nodeType}/{uid0}/",
            "inputs": {
                "sfmfolder": "{HlocLocalizer_1.output}",
                "databaseFile": "{KeypointsDetector_2.output}",
                "imagesFolder": "{HlocLocalizer_1.output}",
                "imagePairs": "{HlocLocalizer_1.image_pairs}",
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
                "0": "47fc0040307b94498de2c33cac5ef8a8a9089d56"
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
        "DensePonitcloudsConcatenator_2": {
            "nodeType": "DensePonitcloudsConcatenator",
            "position": [
                3809,
                -138
            ],
            "parallelization": {
                "blockSize": 0,
                "size": 1,
                "split": 1
            },
            "uids": {
                "0": "6ac76e98cabb9234565abee0813e1112a27741bd"
            },
            "internalFolder": "{cache}/{nodeType}/{uid0}/",
            "inputs": {
                "pointcloud1": "{HlocLocalizer_1.densePts}",
                "pointcloud2": "{IOConvertor_4.densePts}",
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
                "0": "62cc2ebd6a7dbb0449ca29386f4050a014d50a82"
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
        "IOConvertor_2": {
            "nodeType": "IOConvertor",
            "position": [
                1621,
                67
            ],
            "parallelization": {
                "blockSize": 0,
                "size": 0,
                "split": 1
            },
            "uids": {
                "0": "c454ed8ab206f01d53925ff4417cdca48115dd29"
            },
            "internalFolder": "{cache}/{nodeType}/{uid0}/",
            "inputs": {
                "inputFolder": "{ModelsAligner_2.output}",
                "pointcloudFile": "",
                "hashScale": 1,
                "renderScale": 1,
                "allPoints": false,
                "intrinsics": [],
                "inputSfMFormat": "COLMAP",
                "outputSfMFormat": [
                    "LQuery"
                ],
                "copyImagesToOutput": false,
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
        "KeypointsDetector_2": {
            "nodeType": "KeypointsDetector",
            "position": [
                2059,
                -102
            ],
            "parallelization": {
                "blockSize": 0,
                "size": 1,
                "split": 1
            },
            "uids": {
                "0": "32da9c3ed2423033bdd20b08d13478b2d73cd5a9"
            },
            "internalFolder": "{cache}/{nodeType}/{uid0}/",
            "inputs": {
                "imagesFolder": "{HlocLocalizer_1.output}",
                "database": "",
                "algorithm": "{KeypointsDetector_1.algorithm}",
                "removeImages": true,
                "verboseLevel": "info"
            },
            "outputs": {
                "output": "{cache}/{nodeType}/{uid0}/database.db"
            }
        },
        "Mapper_2": {
            "nodeType": "Mapper",
            "position": [
                2685,
                -81
            ],
            "parallelization": {
                "blockSize": 0,
                "size": 1,
                "split": 1
            },
            "uids": {
                "0": "4ee608ce7646caaa314f6981d68b4f71ab3cdf46"
            },
            "internalFolder": "{cache}/{nodeType}/{uid0}/",
            "inputs": {
                "databaseFile": "{Matcher_2.databaseOutputFile}",
                "imagesDirectory": "{TentativeMatcher_2.imagesFolder}",
                "algorithm": "COLMAP",
                "verboseLevel": "info"
            },
            "outputs": {
                "output": "{cache}/{nodeType}/{uid0}/"
            }
        },
        "ModelsAligner_3": {
            "nodeType": "ModelsAligner",
            "position": [
                2875,
                30
            ],
            "parallelization": {
                "blockSize": 0,
                "size": 1,
                "split": 1
            },
            "uids": {
                "0": "15a751640a0a1d5a3a02b74e6f5a38ace2685fee"
            },
            "internalFolder": "{cache}/{nodeType}/{uid0}/",
            "inputs": {
                "sfmTransform": "{Mapper_2.output}",
                "ptsTransform": "",
                "sfmReference": "{HlocLocalizer_1.output}",
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
        "IOConvertor_4": {
            "nodeType": "IOConvertor",
            "position": [
                3616,
                -42
            ],
            "parallelization": {
                "blockSize": 0,
                "size": 0,
                "split": 1
            },
            "uids": {
                "0": "f696d2c705e95e926e1cf29c1ea52ca92a46f22f"
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
                    "OBJ"
                ],
                "copyImagesToOutput": false,
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
        "HlocLocalizer_1": {
            "nodeType": "HlocLocalizer",
            "position": [
                1819,
                -164
            ],
            "parallelization": {
                "blockSize": 0,
                "size": 1,
                "split": 1
            },
            "uids": {
                "0": "315ad758ef473aff187e62b8fb4e5535e170b371"
            },
            "internalFolder": "{cache}/{nodeType}/{uid0}/",
            "inputs": {
                "hlocMapDir": "/local/mapping/policmic/hololens_mapper/pipelines/MeshroomCache/HlocMapCreator/a91a81ec2a478e8769e86e5eb2c20bc1b60cf675",
                "queryFile": "{IOConvertor_2.lQueryFile}",
                "localSfM": "{ModelsAligner_2.output}",
                "imagesRig": "True",
                "copyDensePts": true,
                "verboseLevel": "info"
            },
            "outputs": {
                "output": "{cache}/{nodeType}/{uid0}/",
                "image_pairs": "{cache}/{nodeType}/{uid0}/image_pairs.txt",
                "localization": "{cache}/{nodeType}/{uid0}/query_localization_results.txt",
                "densePts": "{cache}/{nodeType}/{uid0}/model.obj"
            }
        }
    }
}