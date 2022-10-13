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
                "0": "a556b3062821f93c6db901baabde15a7f6107c96"
            },
            "internalFolder": "{cache}/{nodeType}/{uid0}/",
            "inputs": {
                "username": "IMPACT",
                "password": "Praha123",
                "ip": "127.0.0.1:10080",
                "recordingsFolder": "D:/tmp/HoloLens2Recording__OK2",
                "download": true,
                "delete": true,
                "verboseLevel": "info"
            },
            "outputs": {}
        }
    }
}