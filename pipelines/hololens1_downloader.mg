{
    "header": {
        "pipelineVersion": "2.2",
        "releaseVersion": "2021.1.0",
        "fileVersion": "1.1",
        "nodesVersions": {
            "HoloLens1Downloader": "0.1"
        }
    },
    "graph": {
        "HoloLens1Downloader_1": {
            "nodeType": "HoloLens1Downloader",
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
                "0": "20d3e1ee213079602877c9fb554734e91647b33a"
            },
            "internalFolder": "{cache}/{nodeType}/{uid0}/",
            "inputs": {
                "username": "IMPACT",
                "password": "Praha123",
                "ip": "10.37.1.101",
                "recordingsFolder": "d:/tmp/HoloLensRecording",
                "download": true,
                "delete": false,
                "verboseLevel": "info"
            },
            "outputs": {}
        }
    }
}