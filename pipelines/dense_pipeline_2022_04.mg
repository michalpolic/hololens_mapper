{
    "header": {
        "pipelineVersion": "2.2",
        "releaseVersion": "2021.1.0",
        "fileVersion": "1.1",
        "nodesVersions": {
            "MatchingPairsSelector": "0.1",
            "PointcloudComposer": "0.1",
            "DensePointcloudFilter": "0.1",
            "KeyframeSelector": "0.1",
            "IOConvertor": "0.1"
        }
    },
    "graph": {
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
                "0": "87f8b9c8baeb06074d5ffe20f7c6b2ef9913894a"
            },
            "internalFolder": "{cache}/{nodeType}/{uid0}/",
            "inputs": {
                "densePointcloud": "{PointcloudComposer_1.output}",
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
                481,
                140
            ],
            "parallelization": {
                "blockSize": 0,
                "size": 1,
                "split": 1
            },
            "uids": {
                "0": "78121d10c375dd260c9b994e3b57d2297c8d7d30"
            },
            "internalFolder": "{cache}/{nodeType}/{uid0}/",
            "inputs": {
                "sfmFile": "{IOConvertor_1.output}",
                "inputSfMFormat": "COLMAP",
                "outputSfMFormat": "COLMAP",
                "minCommonPts": 200,
                "verboseLevel": "info"
            },
            "outputs": {
                "output": "{cache}/{nodeType}/{uid0}//image_pairs.txt"
            }
        },
        "PointcloudComposer_1": {
            "nodeType": "PointcloudComposer",
            "position": [
                -144,
                63
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
        "KeyframeSelector_2": {
            "nodeType": "KeyframeSelector",
            "position": [
                62,
                -10
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
        "IOConvertor_1": {
            "nodeType": "IOConvertor",
            "position": [
                267,
                47
            ],
            "parallelization": {
                "blockSize": 0,
                "size": 0,
                "split": 1
            },
            "uids": {
                "0": "93bd52d4ccfbfad19ce1e818ae5dbbbb335d8c56"
            },
            "internalFolder": "{cache}/{nodeType}/{uid0}/",
            "inputs": {
                "inputFolder": "{KeyframeSelector_2.output}",
                "pointcloudFile": "{DensePointcloudFilter_1.densePointcloud}",
                "hashScale": 10,
                "allPoints": false,
                "intrinsics": [
                    {
                        "intrinsicId": 0,
                        "trackingFile": "pv",
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
                        "trackingFile": "vlc_ll",
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
                        "trackingFile": "vlc_lf",
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
                        "trackingFile": "vlc_rf",
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
                        "trackingFile": "vlc_rr",
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
                "inputSfMFormat": "HoloLens2",
                "outputSfMFormat": [
                    "COLMAP"
                ],
                "cpoyImagesToOutput": false,
                "imagesPath": "original",
                "verboseLevel": "info"
            },
            "outputs": {
                "output": "{cache}/{nodeType}/{uid0}/",
                "outputMeshroomSfM": "{cache}/{nodeType}/{uid0}/meshroom_sfm.json"
            }
        }
    }
}