{
    "header": {
        "pipelineVersion": "2.2",
        "releaseVersion": "2021.1.0",
        "fileVersion": "1.1",
        "nodesVersions": {
            "HlocQueryComposer": "0.1",
            "HlocLocalizer": "0.1",
            "HlocMapCreator": "0.1",
            "IOConvertor": "0.1"
        }
    },
    "graph": {
        "HlocMapCreator_1": {
            "nodeType": "HlocMapCreator",
            "position": [
                1220,
                -54
            ],
            "parallelization": {
                "blockSize": 0,
                "size": 1,
                "split": 1
            },
            "uids": {
                "0": "7b80aaac0afd00fdf625904a8bdf2aa1747074fa"
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
                1023,
                -53
            ],
            "parallelization": {
                "blockSize": 0,
                "size": 0,
                "split": 1
            },
            "uids": {
                "0": "260aa7c81f78fa1b06cf9a443969093db9d61a53"
            },
            "internalFolder": "{cache}/{nodeType}/{uid0}/",
            "inputs": {
                "inputFolder": "/local/datasets/Matterport2COLMAP/SPRING_Demo/DB_Broca_dynamic_1/cutouts_dynamic/hospital_COLMAP",
                "pointcloudFile": "/local/datasets/Matterport2COLMAP/SPRING_Demo/DB_Broca_dynamic_1/models/hospital/cloud.obj",
                "hashScale": 10,
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
        "HlocLocalizer_1": {
            "nodeType": "HlocLocalizer",
            "position": [
                1630,
                -118
            ],
            "parallelization": {
                "blockSize": 0,
                "size": 1,
                "split": 1
            },
            "uids": {
                "0": "52b7066f1bfd73edc98848d172af373c34fc8ade"
            },
            "internalFolder": "{cache}/{nodeType}/{uid0}/",
            "inputs": {
                "hlocMapDir": "{HlocQueryComposer_1.hlocMapDir}",
                "queryFile": "{HlocQueryComposer_1.output}",
                "localSfM": "",
                "imageDescriptor": "netvlad",
                "keypointDetector": "superpoint-n4096-r1024",
                "matcher": "superglue",
                "imagesRig": false,
                "copyDensePts": false,
                "verboseLevel": "info"
            },
            "outputs": {
                "output": "{cache}/{nodeType}/{uid0}/",
                "image_pairs": "{cache}/{nodeType}/{uid0}/image_pairs.txt",
                "localization": "{cache}/{nodeType}/{uid0}/query_localization_results.txt",
                "densePts": "{cache}/{nodeType}/{uid0}/model.obj"
            }
        },
        "HlocQueryComposer_1": {
            "nodeType": "HlocQueryComposer",
            "position": [
                1418,
                -72
            ],
            "parallelization": {
                "blockSize": 0,
                "size": 1,
                "split": 1
            },
            "uids": {
                "0": "570a5deb61b055149634cbbc63b2eeab9a2e6ce7"
            },
            "internalFolder": "{cache}/{nodeType}/{uid0}/",
            "inputs": {
                "imageDir": "True",
                "images": [],
                "hlocMapDir": "{HlocMapCreator_1.output}",
                "queryImageDir": "/local/datasets/Matterport2COLMAP/SPRING_Demo/BrocaQueryRealistic/images",
                "sameCamera": "True",
                "intrinsics": [
                    {
                        "cameraModel": "SIMPLE_PINHOLE",
                        "width": 1344,
                        "height": 756,
                        "params": "1034.7892 672 378"
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