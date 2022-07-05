{
    "header": {
        "pipelineVersion": "2.2",
        "releaseVersion": "2021.1.0",
        "fileVersion": "1.1",
        "nodesVersions": {
            "Mapper": "0.1",
            "Matcher": "0.1",
            "ModelsAligner": "0.1",
            "HoloLens2Downloader": "0.1",
            "KeypointsDetector": "0.1",
            "Patchmatchnet": "0.1",
            "PointcloudComposer": "0.1",
            "DensePointcloudFilter": "0.1",
            "TentativeMatcher": "0.1",
            "DensePonitcloudsConcatenator": "0.1",
            "HlocLocalizer": "0.1",
            "HoloLens1Downloader": "0.1",
            "IOConvertor": "0.1",
            "HlocMapCreator": "0.1",
            "KeyframeSelector": "0.1",
            "MatchingPairsSelector": "0.1"
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
                "0": "0764fdd890ab2b4f51b86a9ac224769234790638"
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
                "0": "1b5c8ce5ffd9dfc4d5b73b0cb93986f509ff3d4b"
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
                75,
                -177
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
                "0": "08dcad499d69b5c730c0da9f8e34a39285a69ad6"
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
                2999,
                -14
            ],
            "parallelization": {
                "blockSize": 0,
                "size": 1,
                "split": 1
            },
            "uids": {
                "0": "758a475999fade0927a25569129ee676f939684c"
            },
            "internalFolder": "{cache}/{nodeType}/{uid0}/",
            "inputs": {
                "colmapFolder": "{Mapper_2.output}",
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
                "0": "eb76bd3353132b074ca39e98176962fcc76ee2c0"
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
        "ModelsAligner_1": {
            "nodeType": "ModelsAligner",
            "position": [
                2992,
                133
            ],
            "parallelization": {
                "blockSize": 0,
                "size": 1,
                "split": 1
            },
            "uids": {
                "0": "eae429531da8eac15de81db6d5eb00dd3e550df6"
            },
            "internalFolder": "{cache}/{nodeType}/{uid0}/",
            "inputs": {
                "sfmTransform": "{ModelsAligner_2.sfmReference}",
                "ptsTransform": "{DensePointcloudFilter_1.output}",
                "sfmReference": "{Mapper_2.output}",
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
                3210,
                67
            ],
            "parallelization": {
                "blockSize": 0,
                "size": 1,
                "split": 1
            },
            "uids": {
                "0": "2538b500b723b7d092dd80bd77b79122db10d179"
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
                1621,
                67
            ],
            "parallelization": {
                "blockSize": 0,
                "size": 0,
                "split": 1
            },
            "uids": {
                "0": "14abc5115f24c698564b8d3c81b53ec19c45813d"
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
                2685,
                -81
            ],
            "parallelization": {
                "blockSize": 0,
                "size": 1,
                "split": 1
            },
            "uids": {
                "0": "784c825a618cd7ab40dee109b29fe927f3e70ca1"
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
                "0": "fa9b4e93648ee2952a3a1caf71f4e123ddee09ca"
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
                "0": "6671bac94092642ebb06e28f3ca20859b920f532"
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
        "KeypointsDetector_2": {
            "nodeType": "KeypointsDetector",
            "position": [
                2052,
                -92
            ],
            "parallelization": {
                "blockSize": 0,
                "size": 1,
                "split": 1
            },
            "uids": {
                "0": "371ae6b08f2ef2ae0cc762a72d17a9bbbc8faad2"
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
                "0": "27c603a8efad59b075dfec1a98bce5877e5efcc2"
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
        "IOConvertor_3": {
            "nodeType": "IOConvertor",
            "position": [
                264,
                -287
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
        "IOConvertor_4": {
            "nodeType": "IOConvertor",
            "position": [
                3414,
                -31
            ],
            "parallelization": {
                "blockSize": 0,
                "size": 0,
                "split": 1
            },
            "uids": {
                "0": "7311f56048f07f2439e0cebd23d4bb94085a2184"
            },
            "internalFolder": "{cache}/{nodeType}/{uid0}/",
            "inputs": {
                "inputFolder": "{Patchmatchnet_1.colmapFolder}",
                "pointcloudFile": "{DensePonitcloudsConcatenator_1.output}",
                "hashScale": 100,
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
                "lQueryFile": "{cache}/{nodeType}/{uid0}/hloc_queries.txt"
            }
        },
        "IOConvertor_5": {
            "nodeType": "IOConvertor",
            "position": [
                444,
                -449
            ],
            "parallelization": {
                "blockSize": 0,
                "size": 0,
                "split": 1
            },
            "uids": {
                "0": "8f68ba9a3fac30bd5593712c0ad1a935742f68c1"
            },
            "internalFolder": "{cache}/{nodeType}/{uid0}/",
            "inputs": {
                "inputFolder": "{IOConvertor_3.output}",
                "pointcloudFile": "{PointcloudComposer_2.output}",
                "hashScale": 1,
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
                "lQueryFile": "{cache}/{nodeType}/{uid0}/hloc_queries.txt"
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
                "0": "9f0fb5b70ca55322d0ce78069dd52de564a17345"
            },
            "internalFolder": "{cache}/{nodeType}/{uid0}/",
            "inputs": {
                "queryFile": "{IOConvertor_2.lQueryFile}",
                "hlocMapDir": "{HlocMapCreator_1.output}",
                "localSfM": "{ModelsAligner_2.output}",
                "imagesRig": "True",
                "verboseLevel": "info"
            },
            "outputs": {
                "output": "{cache}/{nodeType}/{uid0}/",
                "image_pairs": "{cache}/{nodeType}/{uid0}/image_pairs.txt",
                "localization": "{cache}/{nodeType}/{uid0}/query_localization_results.txt"
            }
        }
    }
}