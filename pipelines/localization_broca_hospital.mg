{
    "header": {
        "pipelineVersion": "2.2",
        "releaseVersion": "2021.1.0",
        "fileVersion": "1.1",
        "nodesVersions": {
            "HlocQueryComposer": "0.1",
            "HlocMapCreator": "0.1",
            "HlocLocalizer": "0.1"
        }
    },
    "graph": {
        "HlocMapCreator_1": {
            "nodeType": "HlocMapCreator",
            "position": [
                782,
                -229
            ],
            "parallelization": {
                "blockSize": 0,
                "size": 1,
                "split": 1
            },
            "uids": {
                "0": "0bb87d59e544413bb294a175ce205c5a090939aa"
            },
            "internalFolder": "{cache}/{nodeType}/{uid0}/",
            "inputs": {
                "inputSfM": "/local1/projects/artwin/mapping/hololens_mapper/pipelines/MeshroomCache/IOConvertor/194fe1cddf09dcbf237ce61a6e9e247be8345bb8",
                "imagesFolder": "/local1/projects/artwin/mapping/hololens_mapper/pipelines/MeshroomCache/IOConvertor/194fe1cddf09dcbf237ce61a6e9e247be8345bb8",
                "verboseLevel": "info"
            },
            "outputs": {
                "output": "{cache}/{nodeType}/{uid0}/"
            }
        },
        "HlocQueryComposer_1": {
            "nodeType": "HlocQueryComposer",
            "position": [
                976,
                -88
            ],
            "parallelization": {
                "blockSize": 0,
                "size": 1,
                "split": 1
            },
            "uids": {
                "0": "0b28c81a136f18ba96eb29989728658050b4874c"
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
        },
        "HlocLocalizer_1": {
            "nodeType": "HlocLocalizer",
            "position": [
                1203,
                -163
            ],
            "parallelization": {
                "blockSize": 0,
                "size": 1,
                "split": 1
            },
            "uids": {
                "0": "f459a99b11e0382d1636337e1f81d8b3b15863bf"
            },
            "internalFolder": "{cache}/{nodeType}/{uid0}/",
            "inputs": {
                "queryFile": "{HlocQueryComposer_1.output}",
                "hlocMapDir": "{HlocQueryComposer_1.hlocMapDir}",
                "localSfM": "{HlocMapCreator_1.output}",
                "imagesRig": false,
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