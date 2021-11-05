{
    "header": {
        "pipelineVersion": "2.2",
        "releaseVersion": "2021.1.0",
        "fileVersion": "1.1",
        "nodesVersions": {
            "HololensPointcloudComposer": "0.1",
            "KeyframeSelector": "0.1"
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
                "output": "{cache}/{nodeType}/{uid0}/"
            }
        },
        "KeyframeSelector_1": {
            "nodeType": "KeyframeSelector",
            "position": [
                65,
                34
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
        }
    }
}