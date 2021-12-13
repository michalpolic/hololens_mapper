{
    "header": {
        "pipelineVersion": "2.2",
        "releaseVersion": "2021.1.0",
        "fileVersion": "1.1",
        "nodesVersions": {
            "HololensPointcloudComposer": "0.1",
            "KeyframeSelector": "0.1",
            "DensePointcloudFilter": "0.1",
            "ModelsAligner": "0.1",
            "HoloLensMatcher": "0.1",
            "MatchingPairsSelector": "0.1",
            "HoloLensIO": "0.1",
            "ColmapMapper": "0.1"
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
                "0": "310b96a95d4761b9dff24b8ffe77756259eb1e0b"
            },
            "internalFolder": "{cache}/{nodeType}/{uid0}/",
            "inputs": {
                "recordingDir": "/local1/projects/artwin/datasets/Kitchen__2021_11_25",
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
                "0": "be61e554269bbdd24d1d86248f6736f20a8316f2"
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
                66,
                82
            ],
            "parallelization": {
                "blockSize": 0,
                "size": 1,
                "split": 1
            },
            "uids": {
                "0": "3f28555bfd54ab5d83a007f5f3b4f74f58b4cbfc"
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
                "0": "b60ea0a05562abe22aa73c4b90b6249a72b5230c"
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
                "0": "df2147f32364ad4e14de7472e75b5ee185b1c4c8"
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
                "0": "17e7ee1984b88d58f23b51cddd5e5af7048feba5"
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
                947,
                0
            ],
            "parallelization": {
                "blockSize": 0,
                "size": 1,
                "split": 1
            },
            "uids": {
                "0": "b2e79a9c58629719346d2dab1c0199084058ecc5"
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
                "0": "b4b1649ec83bac88da10f4b319a990da2deaeb95"
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
                "verboseLevel": "info"
            },
            "outputs": {
                "output": "{cache}/{nodeType}/{uid0}/"
            }
        },
        "HoloLensIO_2": {
            "nodeType": "HoloLensIO",
            "position": [
                1131,
                45
            ],
            "parallelization": {
                "blockSize": 0,
                "size": 0,
                "split": 1
            },
            "uids": {
                "0": "bd8efe3c789c143fef1a696bcb8d833752024307"
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
                "verboseLevel": "info"
            },
            "outputs": {
                "output": "{cache}/{nodeType}/{uid0}/"
            }
        }
    }
}