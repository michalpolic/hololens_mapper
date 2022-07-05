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
                781,
                -33
            ],
            "parallelization": {
                "blockSize": 0,
                "size": 1,
                "split": 1
            },
            "uids": {
                "0": "b2d0fc9708ae42e21faec37d994a68d3311df672"
            },
            "internalFolder": "{cache}/{nodeType}/{uid0}/",
            "inputs": {
                "username": "IMPACT",
                "password": "Praha123",
                "ip": "192.168.68.110",
                "recordingsFolder": "d:/tmp/HoloLensRecording",
                "download": true,
                "delete": false,
                "verboseLevel": "info"
            },
            "outputs": {}
        }
    }
}