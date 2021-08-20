import os
from pathlib import Path
from src.utils.UtilsSingularity import UtilsSingularity

class Meshroom():

    def __init__(self, colmap_sif):
        """Init meshroom/alicevision object to run predefined commands"""
        self._meshroom_sif = colmap_sif

    def create_cache_folders(self, relative_path):
        absolute_dir_path = self._meshroom_sif._working_dir + relative_path
        if os.path.isfile(absolute_dir_path) or absolute_dir_path[-4:] == ".abc" or absolute_dir_path[-4:] == ".ply":
            absolute_dir_path = os.path.dirname(absolute_dir_path)
        Path(absolute_dir_path).mkdir(parents=True, exist_ok=True)

    def convert_sfm(self, input_path, output_path):
        self.create_cache_folders(output_path)
        self._meshroom_sif.command_dict("aliceVision_convertSfMFormat", 
            {"input": input_path, 
            "output": output_path,
            "describerTypes": "unknown,sift",
            "views": True,
            "intrinsics": True,
            "extrinsics": True,
            "structure": True,
            "observations": True,
            "verboseLevel": "info"
            })

    def undistort_imgs(self, input_path, output_path):
        self.create_cache_folders(output_path)
        self._meshroom_sif.command_dict("aliceVision_prepareDenseScene", 
            {"input": input_path, 
            "output": output_path,
            "outputFileType": "exr",
            "saveMetadata": True,
            "saveMatricesTxtFiles": False,
            "evCorrection": False,
            "verboseLevel": "info"
            })

    def estimate_depthmaps(self, input_path, output_path, images_folder):
        self.create_cache_folders(output_path)       # 7min - 134imgs  (3s / img in full resolution)
        self._meshroom_sif.command_dict("aliceVision_depthMapEstimation", 
            {"input": input_path, 
            "output": output_path,
            "imagesFolder": images_folder,
            "downscale": 1,
            "minViewAngle": 2.0,
            "maxViewAngle": 70.0,
            "sgmMaxTCams": 10,
            "sgmWSH": 4,
            "sgmGammaC": 5.5,
            "sgmGammaP": 8.0,
            "refineMaxTCams": 6,
            "refineNSamplesHalf": 150,
            "refineNDepthsToRefine": 31,
            "refineNiters": 100,
            "refineWSH": 3,
            "refineSigma": 15,
            "refineGammaC": 15.5,
            "refineGammaP": 8.0,
            "refineUseTcOrRcPixSize": False,
            "exportIntermediateResults": False,
            "nbGPUs": 0,
            "verboseLevel": "info"})

    def filter_depthmaps(self, input_path, output_path, deptmaps_path):
        self.create_cache_folders(output_path)
        self._meshroom_sif.command_dict("aliceVision_depthMapFiltering", 
            {"input": input_path, 
            "output": output_path,
            "depthMapsFolder": deptmaps_path,
            "minViewAngle": 2.0,
            "maxViewAngle": 70.0,
            "nNearestCams": 10,
            "minNumOfConsistentCams": 3,
            "minNumOfConsistentCamsWithLowSimilarity": 4,
            "pixSizeBall": 0,
            "pixSizeBallWithLowSimilarity": 0,
            "computeNormalMaps": False,
            "verboseLevel": "info"
            })

    def meshing(self, input_path, output_path, mesh_path, deptmaps_path = ""):
        self.create_cache_folders(output_path)
        params = {"input": input_path, 
            "output": output_path,
            "outputMesh": mesh_path,
            "estimateSpaceFromSfM": True,
            "estimateSpaceMinObservations": 3,
            "estimateSpaceMinObservationAngle": 10,
            "maxInputPoints": 50000000,
            "maxPoints": 5000000,
            "maxPointsPerVoxel": 1000000,
            "minStep": 2,
            "partitioning": "singleBlock",
            "repartition": "multiResolution",
            "angleFactor": 15.0,
            "simFactor": 15.0,
            "pixSizeMarginInitCoef": 2.0,
            "pixSizeMarginFinalCoef": 4.0,
            "voteMarginFactor": 4.0,
            "contributeMarginFactor": 2.0,
            "simGaussianSizeInit": 10.0,
            "simGaussianSize": 10.0,
            "minAngleThreshold": 1.0,
            "refineFuse": True,
            "helperPointsGridSize": 10,
            "nPixelSizeBehind": 4.0,
            "fullWeight": 1.0,
            "voteFilteringForWeaklySupportedSurfaces": True,
            "addLandmarksToTheDensePointCloud": True,
            "invertTetrahedronBasedOnNeighborsNbIterations": 0,
            "minSolidAngleRatio": 0.2,
            "nbSolidAngleFilteringIterations": 0,
            "colorizeOutput": True,
            "maxNbConnectedHelperPoints": 50,   # this is important try -1
            "saveRawDensePointCloud": True,
            "exportDebugTetrahedralization": False,
            "seed": 0,
            "verboseLevel": "info"}
        if deptmaps_path:
            params["depthMapsFolder"] = deptmaps_path

        self._meshroom_sif.command_dict("aliceVision_meshing", params)

    def meshing2(self, input_path, output_path, mesh_path):
        self.create_cache_folders(output_path)
        params = {"input": "/host_pwd/" + input_path, 
            "output": "/host_pwd/" + output_path,
            "outputMesh": "/host_pwd/" + mesh_path,
            "estimateSpaceFromSfM": True,
            "addLandmarksToTheDensePointCloud": True,
            "colorizeOutput": False,
            "saveRawDensePointCloud": True,
            "maxNbConnectedHelperPoints": -1,  
            "verboseLevel": "info"}
        self._meshroom_sif.command_dict("aliceVision_meshing", params)

    def texturing(self, input_path, images_folder, mesh_path, output_path):
        self.create_cache_folders(output_path)
        self._meshroom_sif.command_dict("aliceVision_texturing", 
            {"input": input_path, 
            "imagesFolder": images_folder,
            "inputMesh": mesh_path,
            "output": output_path,
            "textureSide": 8192,
            "downscale": 2,
            "outputTextureFileType": "png",
            "unwrapMethod": "Basic",
            "useUDIM": True,
            "fillHoles": False,
            "padding": 5,
            "multiBandDownscale": 4,
            "multiBandNbContrib": "1 5 10 0",
            "useScore": True,
            "bestScoreThreshold": 0.1,
            "angleHardThreshold": 140.0,
            "processColorspace": "sRGB",
            "correctEV": False,
            "forceVisibleByAllVertices": False,
            "flipNormals": False,
            "visibilityRemappingMethod": "PullPush",
            "subdivisionTargetRatio": 0.8,
            "verboseLevel": "trace"})