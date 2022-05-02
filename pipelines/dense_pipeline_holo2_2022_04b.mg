{
    "header": {
        "pipelineVersion": "2.2",
        "releaseVersion": "2021.1.0",
        "fileVersion": "1.1",
        "nodesVersions": {
            "Patchmatchnet": "0.1",
            "HlocLocalizer": "0.1",
            "ModelsAligner": "0.1",
            "DensePointcloudFilter": "0.1",
            "DensePonitcloudsAligner": "0.1",
            "HoloLens1Downloader": "0.1",
            "HlocMapCreator": "0.1",
            "TentativeMatcher": "0.1",
            "KeyframeSelector": "0.1",
            "IOConvertor": "0.1",
            "HoloLens2Downloader": "0.1",
            "MatchingPairsSelector": "0.1",
            "KeypointsDetector": "0.1",
            "Matcher": "0.1",
            "Mapper": "0.1",
            "PointcloudComposer": "0.1"
        }
    },
    "graph": {
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
                "0": "64946ea31d91712726fa1f50c91e350083a7f7ec"
            },
            "internalFolder": "{cache}/{nodeType}/{uid0}/",
            "inputs": {
                "recordingDir": "/local1/projects/artwin/datasets/LibrarySmall_Holo2",
                "recordingSource": "HoloLens2",
                "parameters": [],
                "verboseLevel": "info"
            },
            "outputs": {
                "output": "{cache}/{nodeType}/{uid0}//model.obj"
            }
        },
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
                "0": "863f1788e29c86d4c5a8c3c87046edb84636e147"
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
                "0": "7b3ca410a7a1ae6d672ad0f6b1172ccb228097b7"
            },
            "internalFolder": "{cache}/{nodeType}/{uid0}/",
            "inputs": {
                "databaseFile": "{Matcher_1.databaseOutputFile}",
                "imagesFolder": "{TentativeMatcher_1.imagesFolder}",
                "algorithm": "COLMAP",
                "verboseLevel": "info"
            },
            "outputs": {
                "output": "{cache}/{nodeType}/{uid0}/"
            }
        },
        "HlocMapCreator_1": {
            "nodeType": "HlocMapCreator",
            "position": [
                594,
                -279
            ],
            "parallelization": {
                "blockSize": 0,
                "size": 1,
                "split": 1
            },
            "uids": {
                "0": "5459eb4fe47110e6be3b00e4a4a187ffeed0cb8f"
            },
            "internalFolder": "{cache}/{nodeType}/{uid0}/",
            "inputs": {
                "inputSfM": "{IOConvertor_3.output}",
                "imagesFolder": "{IOConvertor_3.output}",
                "verboseLevel": "info"
            },
            "outputs": {
                "output": "{cache}/{nodeType}/{uid0}/"
            }
        },
        "KeyframeSelector_1": {
            "nodeType": "KeyframeSelector",
            "position": [
                81,
                -308
            ],
            "parallelization": {
                "blockSize": 0,
                "size": 1,
                "split": 1
            },
            "uids": {
                "0": "f28977ee1900b76bdf6b281cd97127584cf283ef"
            },
            "internalFolder": "{cache}/{nodeType}/{uid0}/",
            "inputs": {
                "recordingDir": "{PointcloudComposer_2.recordingDir}",
                "recordingSource": "{PointcloudComposer_2.recordingSource}",
                "pvBlurThreshold": 15.0,
                "pvMinFrameOffset": 5,
                "vlcMinFrameOffset": 5,
                "verboseLevel": "info"
            },
            "outputs": {
                "output": "{cache}/{nodeType}/{uid0}/"
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
                "0": "194fe1cddf09dcbf237ce61a6e9e247be8345bb8"
            },
            "internalFolder": "{cache}/{nodeType}/{uid0}/",
            "inputs": {
                "inputFolder": "{KeyframeSelector_2.output}",
                "pointcloudFile": "{PointcloudComposer_1.output}",
                "hashScale": 10,
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
                "lQueryFile": "{cache}/{nodeType}/{uid0}/hloc_queries.txt"
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
                "0": "ae5d59aa0fbb14b338ca3b8c5d32deab1f28caea"
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
                2021,
                223
            ],
            "parallelization": {
                "blockSize": 0,
                "size": 1,
                "split": 1
            },
            "uids": {
                "0": "87f8b9c8baeb06074d5ffe20f7c6b2ef9913894a"
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
                "0": "077ad895c44c91a9f9f3f988ac26e030b949a7e8"
            },
            "internalFolder": "{cache}/{nodeType}/{uid0}/",
            "inputs": {
                "inputSfM": "{IOConvertor_1.output}",
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
                "0": "2eddaddd59c7a1786b0fcdc966b5ab3793826f89"
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
        "ModelsAligner_1": {
            "nodeType": "ModelsAligner",
            "position": [
                2207,
                147
            ],
            "parallelization": {
                "blockSize": 0,
                "size": 1,
                "split": 1
            },
            "uids": {
                "0": "44ce0d25e4651bbffed68e853ed2c5adf3d49528"
            },
            "internalFolder": "{cache}/{nodeType}/{uid0}/",
            "inputs": {
                "sfmTransform": "{ModelsAligner_2.output}",
                "ptsTransform": "{DensePointcloudFilter_1.output}",
                "sfmReference": "{HlocLocalizer_1.output}",
                "verboseLevel": "info"
            },
            "outputs": {
                "output": "{cache}/{nodeType}/{uid0}/",
                "transforedPts": "{cache}/{nodeType}/{uid0}/model.obj"
            }
        },
        "Patchmatchnet_1": {
            "nodeType": "Patchmatchnet",
            "position": [
                2021,
                328
            ],
            "parallelization": {
                "blockSize": 0,
                "size": 1,
                "split": 1
            },
            "uids": {
                "0": "1c7610c8c17ba021d378910beae2bc4ef6fce523"
            },
            "internalFolder": "{cache}/{nodeType}/{uid0}/",
            "inputs": {
                "colmapFolder": "{HlocLocalizer_1.output}",
                "verboseLevel": "info"
            },
            "outputs": {
                "output": "{cache}/{nodeType}/{uid0}/",
                "outputPLY": "{cache}/{nodeType}/{uid0}//fused.ply"
            }
        },
        "HlocLocalizer_1": {
            "nodeType": "HlocLocalizer",
            "position": [
                1801,
                -146
            ],
            "parallelization": {
                "blockSize": 0,
                "size": 1,
                "split": 1
            },
            "uids": {
                "0": "cca29563304244a782063c4eb7fba74b3dfa1978"
            },
            "internalFolder": "{cache}/{nodeType}/{uid0}/",
            "inputs": {
                "queryFile": "{IOConvertor_2.lQueryFile}",
                "hlocMapDir": "{HlocMapCreator_1.output}",
                "localSfM": "{ModelsAligner_2.output}",
                "verboseLevel": "info"
            },
            "outputs": {
                "output": "{cache}/{nodeType}/{uid0}/",
                "image_pairs": "{cache}/{nodeType}/{uid0}/image_pairs.txt",
                "localization": "{cache}/{nodeType}/{uid0}/query_localization_results.txt"
            }
        },
        "KeyframeSelector_2": {
            "nodeType": "KeyframeSelector",
            "position": [
                62,
                20
            ],
            "parallelization": {
                "blockSize": 0,
                "size": 1,
                "split": 1
            },
            "uids": {
                "0": "d6369fdfa53c7a82e1b098e8a9f1b2155714154a"
            },
            "internalFolder": "{cache}/{nodeType}/{uid0}/",
            "inputs": {
                "recordingDir": "{PointcloudComposer_1.recordingDir}",
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
        "PointcloudComposer_2": {
            "nodeType": "PointcloudComposer",
            "position": [
                -118,
                -234
            ],
            "parallelization": {
                "blockSize": 0,
                "size": 0,
                "split": 1
            },
            "uids": {
                "0": "08b198f1ca76300b1132ccee9d12c85d0a164e5a"
            },
            "internalFolder": "{cache}/{nodeType}/{uid0}/",
            "inputs": {
                "recordingDir": "/local1/projects/artwin/datasets/LocalizaitonSmall",
                "recordingSource": "HoloLens2",
                "parameters": [],
                "verboseLevel": "info"
            },
            "outputs": {
                "output": "{cache}/{nodeType}/{uid0}//model.obj"
            }
        },
        "IOConvertor_2": {
            "nodeType": "IOConvertor",
            "position": [
                1623,
                99
            ],
            "parallelization": {
                "blockSize": 0,
                "size": 0,
                "split": 1
            },
            "uids": {
                "0": "38e41ed88de3ae1a5127b2e400c69119d5a783b9"
            },
            "internalFolder": "{cache}/{nodeType}/{uid0}/",
            "inputs": {
                "inputFolder": "{ModelsAligner_2.output}",
                "pointcloudFile": "",
                "hashScale": 1,
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
                "lQueryFile": "{cache}/{nodeType}/{uid0}/hloc_queries.txt"
            }
        },
        "Mapper_2": {
            "nodeType": "Mapper",
            "position": [
                2601,
                -29
            ],
            "parallelization": {
                "blockSize": 0,
                "size": 1,
                "split": 1
            },
            "uids": {
                "0": "b0424e36393b7e5887cf41a318ae11d5a2c83994"
            },
            "internalFolder": "{cache}/{nodeType}/{uid0}/",
            "inputs": {
                "databaseFile": "{Matcher_2.databaseOutputFile}",
                "imagesFolder": "{KeypointsDetector_2.imagesFolder}",
                "algorithm": "COLMAP",
                "verboseLevel": "info"
            },
            "outputs": {
                "output": "{cache}/{nodeType}/{uid0}/"
            }
        },
        "KeypointsDetector_2": {
            "nodeType": "KeypointsDetector",
            "position": [
                2099,
                -89
            ],
            "parallelization": {
                "blockSize": 0,
                "size": 1,
                "split": 1
            },
            "uids": {
                "0": "5ff79d09714442ed92c09edabc0fc8678cce9639"
            },
            "internalFolder": "{cache}/{nodeType}/{uid0}/",
            "inputs": {
                "inputSfM": "{HlocLocalizer_1.output}",
                "imagesFolder": "{HlocLocalizer_1.output}",
                "database": "{Matcher_1.databaseOutputFile}",
                "algorithm": "{KeypointsDetector_1.algorithm}",
                "removeImages": true,
                "verboseLevel": "info"
            },
            "outputs": {
                "output": "{cache}/{nodeType}/{uid0}/database.db"
            }
        },
        "Matcher_2": {
            "nodeType": "Matcher",
            "position": [
                2405,
                -35
            ],
            "parallelization": {
                "blockSize": 0,
                "size": 1,
                "split": 1
            },
            "uids": {
                "0": "17dc9bd5b44534f474d6a163025fe78ffb967036"
            },
            "internalFolder": "{cache}/{nodeType}/{uid0}/",
            "inputs": {
                "databaseFile": "",
                "inputMatchesFormat": "image pairs",
                "inputMatches": "",
                "algorithm": "COLMAP",
                "matchingTreshold": 2,
                "verboseLevel": "info"
            },
            "outputs": {
                "output": "{cache}/{nodeType}/{uid0}/",
                "databaseOutputFile": "{cache}/{nodeType}/{uid0}/database.db"
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
                "0": "a13f2860d2b73470397086799cbdbc0759cb70a7"
            },
            "internalFolder": "{cache}/{nodeType}/{uid0}/",
            "inputs": {
                "sfmTransform": "{Mapper_1.output}",
                "ptsTransform": "",
                "sfmReference": "{IOConvertor_1.output}",
                "verboseLevel": "info"
            },
            "outputs": {
                "output": "{cache}/{nodeType}/{uid0}/",
                "transforedPts": "{cache}/{nodeType}/{uid0}/model.obj"
            }
        },
        "TentativeMatcher_2": {
            "nodeType": "TentativeMatcher",
            "position": [
                2271,
                -231
            ],
            "parallelization": {
                "blockSize": 0,
                "size": 1,
                "split": 1
            },
            "uids": {
                "0": "065bb06a66a145b5e6983ab85d67b15554cb5e11"
            },
            "internalFolder": "{cache}/{nodeType}/{uid0}/",
            "inputs": {
                "sfmfolder": "{KeypointsDetector_2.inputSfM}",
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
        "IOConvertor_3": {
            "nodeType": "IOConvertor",
            "position": [
                267,
                -284
            ],
            "parallelization": {
                "blockSize": 0,
                "size": 5,
                "split": 1
            },
            "uids": {
                "0": "73f0f51f9421649f8a192761afd0bb323d62a4a8"
            },
            "internalFolder": "{cache}/{nodeType}/{uid0}/",
            "inputs": {
                "inputFolder": "{KeyframeSelector_1.output}",
                "pointcloudFile": "{PointcloudComposer_2.output}",
                "hashScale": 10,
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
                "lQueryFile": "{cache}/{nodeType}/{uid0}/hloc_queries.txt"
            }
        },
        "ModelsAligner_3": {
            "nodeType": "ModelsAligner",
            "position": [
                2207,
                276
            ],
            "parallelization": {
                "blockSize": 0,
                "size": 1,
                "split": 1
            },
            "uids": {
                "0": "14097dffda5a3e0dcc4f7597a2ee523904f78fcb"
            },
            "internalFolder": "{cache}/{nodeType}/{uid0}/",
            "inputs": {
                "sfmTransform": "{ModelsAligner_2.output}",
                "ptsTransform": "{Patchmatchnet_1.outputPLY}",
                "sfmReference": "{HlocLocalizer_1.output}",
                "verboseLevel": "info"
            },
            "outputs": {
                "output": "{cache}/{nodeType}/{uid0}/",
                "transforedPts": "{cache}/{nodeType}/{uid0}/model.obj"
            }
        },
        "DensePonitcloudsAligner_1": {
            "nodeType": "DensePonitcloudsAligner",
            "position": [
                2476,
                249
            ],
            "parallelization": {
                "blockSize": 0,
                "size": 1,
                "split": 1
            },
            "uids": {
                "0": "3bff24ab82c517cc6d98bb943ab930221a4e4d70"
            },
            "internalFolder": "{cache}/{nodeType}/{uid0}/",
            "inputs": {
                "pointclouds": [],
                "alignmentMehod": "RICP",
                "alignmentStrategy": "Sequential alignment",
                "verboseLevel": "info",
                "configFile": "",
                "sampling": 1000
            },
            "outputs": {
                "output": "{cache}/{nodeType}/{uid0}//model.obj"
            }
        }
    }
}