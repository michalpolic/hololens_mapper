{
    "header": {
        "pipelineVersion": "2.2",
        "releaseVersion": "2021.1.0",
        "fileVersion": "1.1",
        "nodesVersions": {
            "HoloLens2Downloader": "0.1"
        }
    },
    "graph": {
        "HoloLens2Downloader_1": {
            "nodeType": "HoloLens2Downloader",
            "position": [
                978,
                -17
            ],
            "parallelization": {
                "blockSize": 0,
                "size": 1,
                "split": 1
            },
            "uids": {
                "0": "daf7f6cb89ff136eb999c20ce7c81bd1d1a76ac5"
            },
            "internalFolder": "{cache}/{nodeType}/{uid0}/",
            "inputs": {
                "username": "IMPACT",
                "password": "Praha123",
                "ip": "127.0.0.1:10080",
                "recordingsFolder": "d:/tmp/HoloLens2Recording",
                "download": true,
                "delete": true,
                "verboseLevel": "info"
            },
            "outputs": {}
        }
    }
}