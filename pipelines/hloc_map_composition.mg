{
    "header": {
        "pipelineVersion": "2.2",
        "releaseVersion": "2021.1.0",
        "fileVersion": "1.1",
        "nodesVersions": {
            "KeyframeSelector": "0.1",
            "HololensPointcloudComposer": "0.1",
            "HoloLensIO": "0.1"
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
                "0": "9ec581b7dfdc6c6da24677dbc2057b6d71e687bd"
            },
            "internalFolder": "{cache}/{nodeType}/{uid0}/",
            "inputs": {
                "recordingDir": "d:/local1/projects/artwin/datasets/2021_08_02__11_23_59_MUCLab_1",
                "UVfile": "d:/local1/projects/artwin/datasets/uvdata.txt",
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
                "0": "2d3b4ef6ca10e78c6b74af6bfbeeb5863e7f1b37"
            },
            "internalFolder": "{cache}/{nodeType}/{uid0}/",
            "inputs": {
                "recordingDir": "{HololensPointcloudComposer_1.recordingDir}",
                "pvBlurThreshold": 25.0,
                "pvMinFrameOffset": 13,
                "vlcMinFrameOffset": 30,
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
                4
            ],
            "parallelization": {
                "blockSize": 0,
                "size": 5,
                "split": 1
            },
            "uids": {
                "0": "2ebf61aaed8b3576c89817f30a2f415198899b64"
            },
            "internalFolder": "{cache}/{nodeType}/{uid0}/",
            "inputs": {
                "recordingDir": "{KeyframeSelector_1.output}",
                "pointcloudFile": "{HololensPointcloudComposer_1.output}",
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
                            "x": 1038.14,
                            "y": 1036.47
                        },
                        "principalPoint": {
                            "x": 664.39,
                            "y": 396.14
                        },
                        "distortionParams": [
                            0.1825,
                            -0.1615,
                            -0.2845
                        ]
                    },
                    {
                        "intrinsicId": 1,
                        "csvPrefixes": [
                            "vlc_ll"
                        ],
                        "width": 640,
                        "height": 480,
                        "pxFocalLength": {
                            "x": 450.07207,
                            "y": 450.274345
                        },
                        "principalPoint": {
                            "x": 320.0,
                            "y": 240.0
                        },
                        "distortionParams": []
                    },
                    {
                        "intrinsicId": 2,
                        "csvPrefixes": [
                            "vlc_lf"
                        ],
                        "width": 640,
                        "height": 480,
                        "pxFocalLength": {
                            "x": 448.189452,
                            "y": 452.47809
                        },
                        "principalPoint": {
                            "x": 320.0,
                            "y": 240.0
                        },
                        "distortionParams": []
                    },
                    {
                        "intrinsicId": 3,
                        "csvPrefixes": [
                            "vlc_rf"
                        ],
                        "width": 640,
                        "height": 480,
                        "pxFocalLength": {
                            "x": 449.435779,
                            "y": 453.332057
                        },
                        "principalPoint": {
                            "x": 320.0,
                            "y": 240.0
                        },
                        "distortionParams": []
                    },
                    {
                        "intrinsicId": 4,
                        "csvPrefixes": [
                            "vlc_rr"
                        ],
                        "width": 640,
                        "height": 480,
                        "pxFocalLength": {
                            "x": 450.301002,
                            "y": 450.244147
                        },
                        "principalPoint": {
                            "x": 320.0,
                            "y": 240.0
                        },
                        "distortionParams": []
                    }
                ],
                "outputSfMFormat": "COLMAP",
                "verboseLevel": "info"
            },
            "outputs": {
                "output": "{cache}/{nodeType}/{uid0}/"
            }
        }
    }
}