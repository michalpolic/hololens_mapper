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
                0,
                0
            ],
            "parallelization": {
                "blockSize": 0,
                "size": 1,
                "split": 1
            },
            "uids": {
                "0": "67ee3189f347e96389879870792feefb50aa03eb"
            },
            "internalFolder": "{cache}/{nodeType}/{uid0}/",
            "inputs": {
                "username": "IMPACT",
                "password": "Praha123",
                "ip": "127.0.0.1:10080",
                "recordingsFolder": "D:/tmp/HoloLens2Recording__BD",
                "download": true,
                "delete": true,
                "verboseLevel": "info"
            },
            "outputs": {}
        }
    }
}