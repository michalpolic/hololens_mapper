{
    "header": {
        "pipelineVersion": "2.2",
        "releaseVersion": "2021.1.0",
        "fileVersion": "1.1",
        "nodesVersions": {
            "HlocLocalizer": "0.1",
            "HlocQueryComposer": "0.1",
            "KeypointsDetector": "0.1",
            "Mapper": "0.1",
            "HlocMapCreator": "0.1",
            "Matcher": "0.1",
            "KeyframeSelector": "0.1"
        }
    },
    "graph": {
        "HlocLocalizer_1": {
            "nodeType": "HlocLocalizer",
            "position": [
                1127,
                163
            ],
            "parallelization": {
                "blockSize": 0,
                "size": 1,
                "split": 1
            },
            "uids": {
                "0": "824517301e11fe4f37c4d7586b537dd430a18f58"
            },
            "internalFolder": "{cache}/{nodeType}/{uid0}/",
            "inputs": {
                "queryFile": "{HlocQueryComposer_1.output}",
                "hlocMapDir": "{HlocQueryComposer_1.hlocMapDir}",
                "localSfM": "",
                "imagesRig": false,
                "verboseLevel": "info"
            },
            "outputs": {
                "output": "{cache}/{nodeType}/{uid0}/",
                "image_pairs": "{cache}/{nodeType}/{uid0}/image_pairs.txt",
                "localization": "{cache}/{nodeType}/{uid0}/query_localization_results.txt"
            }
        },
        "Matcher_1": {
            "nodeType": "Matcher",
            "position": [
                306,
                -303
            ],
            "parallelization": {
                "blockSize": 0,
                "size": 1,
                "split": 1
            },
            "uids": {
                "0": "e43e4c0bb6843b6221549c88c2067a06a9536b6a"
            },
            "internalFolder": "{cache}/{nodeType}/{uid0}/",
            "inputs": {
                "databaseFile": "{KeypointsDetector_1.output}",
                "inputMatchesFormat": "no data",
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
        "KeypointsDetector_1": {
            "nodeType": "KeypointsDetector",
            "position": [
                90,
                -231
            ],
            "parallelization": {
                "blockSize": 0,
                "size": 1,
                "split": 1
            },
            "uids": {
                "0": "c280e5608c8377b787037e89425755ad05cd3e40"
            },
            "internalFolder": "{cache}/{nodeType}/{uid0}/",
            "inputs": {
                "imageDirectory": "/local/datasets/BrocaFrontRearFisheyeSubset",
                "imageFolderNames": "/local/datasets/BrocaFrontRearFisheyeSubset/ImageFolders",
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
                538,
                -234
            ],
            "parallelization": {
                "blockSize": 0,
                "size": 1,
                "split": 1
            },
            "uids": {
                "0": "9b6503ee11af6c3aac5fe4da50173790e56a8ed8"
            },
            "internalFolder": "{cache}/{nodeType}/{uid0}/",
            "inputs": {
                "databaseFile": "{Matcher_1.databaseOutputFile}",
                "imageDirectory": "{KeypointsDetector_1.imageDirectory}",
                "imageFolderNames": "{KeypointsDetector_1.imageFolderNames}",
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
                731,
                196
            ],
            "parallelization": {
                "blockSize": 0,
                "size": 1,
                "split": 1
            },
            "uids": {
                "0": "9616615ce94e001c50019a08f6ca83b2aaac151d"
            },
            "internalFolder": "{cache}/{nodeType}/{uid0}/",
            "inputs": {
                "inputSfM": "/local1/projects/artwin/mapping/hololens_mapper/pipelines/MeshroomCache/IOConvertor/194fe1cddf09dcbf237ce61a6e9e247be8345bb8",
                "imageDirectory": "",
                "imageFolderNames": "",
                "verboseLevel": "info"
            },
            "outputs": {
                "output": "{cache}/{nodeType}/{uid0}/"
            }
        },
        "KeyframeSelector_1": {
            "nodeType": "KeyframeSelector",
            "position": [
                51,
                -30
            ],
            "parallelization": {
                "blockSize": 0,
                "size": 1,
                "split": 1
            },
            "uids": {
                "0": "b1a024845f87d2fc6c8f01483c3ace821fd22d96"
            },
            "internalFolder": "{cache}/{nodeType}/{uid0}/",
            "inputs": {
                "recordingDir": "/local/datasets/davidTestDataset",
                "imageFolderNames": "/local/datasets/davidTestDataset/BlurringFolders",
                "recordingSource": "BROCA",
                "pvBlurThreshold": 25.0,
                "pvMinFrameOffset": 0,
                "vlcMinFrameOffset": 0,
                "verboseLevel": "debug"
            },
            "outputs": {
                "output": "{cache}/{nodeType}/{uid0}/"
            }
        },
        "HlocLocalizer_2": {
            "nodeType": "HlocLocalizer",
            "position": [
                1257,
                -271
            ],
            "parallelization": {
                "blockSize": 0,
                "size": 1,
                "split": 1
            },
            "uids": {
                "0": "49b11265a13a44c9354de3255d260842c8c13a7a"
            },
            "internalFolder": "{cache}/{nodeType}/{uid0}/",
            "inputs": {
                "queryFile": "{HlocQueryComposer_2.output}",
                "hlocMapDir": "{HlocQueryComposer_2.hlocMapDir}",
                "localSfM": "",
                "imagesRig": false,
                "verboseLevel": "info"
            },
            "outputs": {
                "output": "{cache}/{nodeType}/{uid0}/",
                "image_pairs": "{cache}/{nodeType}/{uid0}/image_pairs.txt",
                "localization": "{cache}/{nodeType}/{uid0}/query_localization_results.txt"
            }
        },
        "HlocMapCreator_2": {
            "nodeType": "HlocMapCreator",
            "position": [
                787,
                -237
            ],
            "parallelization": {
                "blockSize": 0,
                "size": 1,
                "split": 1
            },
            "uids": {
                "0": "0cf078ae0261722b160e9fe7d67d9d4e6de34b6b"
            },
            "internalFolder": "{cache}/{nodeType}/{uid0}/",
            "inputs": {
                "inputSfM": "{Mapper_1.output}",
                "imageDirectory": "{Mapper_1.imageDirectory}",
                "imageFolderNames": "{Mapper_1.imageFolderNames}",
                "verboseLevel": "debug"
            },
            "outputs": {
                "output": "{cache}/{nodeType}/{uid0}/"
            }
        },
        "HlocQueryComposer_2": {
            "nodeType": "HlocQueryComposer",
            "position": [
                1008,
                -254
            ],
            "parallelization": {
                "blockSize": 0,
                "size": 1,
                "split": 1
            },
            "uids": {
                "0": "9b727e062f96f6896a134482f71b763dc811c985"
            },
            "internalFolder": "{cache}/{nodeType}/{uid0}/",
            "inputs": {
                "imageDir": true,
                "images": [],
                "hlocMapDir": "{HlocMapCreator_2.output}",
                "queryImageDir": "/local/datasets/davidTestDataset/query_images",
                "sameCamera": "True",
                "intrinsics": [
                    {
                        "cameraModel": "OPENCV_FISHEYE",
                        "width": 3264,
                        "height": 2448,
                        "params": "1.1886892840742685e+03 1.1893016496137716e+03 1.6319484444597201e+03 1.2428175443297432e+03 -6.5074864654844314e-02 2.2948182911307041e-02 -3.9319897787193784e-03 -3.7411424922587362e-03"
                    }
                ],
                "verboseLevel": "info"
            },
            "outputs": {
                "output": "{cache}/{nodeType}/{uid0}/hloc_queries.txt"
            }
        },
        "HlocQueryComposer_1": {
            "nodeType": "HlocQueryComposer",
            "position": [
                929,
                203
            ],
            "parallelization": {
                "blockSize": 0,
                "size": 1,
                "split": 1
            },
            "uids": {
                "0": "1b68af9dfb9bf9707b4f13167b78e301fe940407"
            },
            "internalFolder": "{cache}/{nodeType}/{uid0}/",
            "inputs": {
                "imageDir": "True",
                "images": [],
                "hlocMapDir": "{HlocMapCreator_1.output}",
                "queryImageDir": "/local/datasets/LocalizationQueryExample/images",
                "sameCamera": "True",
                "intrinsics": [
                    {
                        "cameraModel": "RADIAL",
                        "width": 760,
                        "height": 428,
                        "params": "585.7 376.3103 196.7361 0.0028 -0.0125"
                    }
                ],
                "verboseLevel": "info"
            },
            "outputs": {
                "output": "{cache}/{nodeType}/{uid0}/hloc_queries.txt"
            }
        }
    }
}