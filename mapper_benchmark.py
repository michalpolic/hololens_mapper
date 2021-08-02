# 1) read dense pointcloud in world coordinates from HoloLens depthmaps 
# 2) run COLMAP to find "correct" camera poses
# 3) load COLMAP & load HoloLens camera poses
# 4) transform colmap cameras to HoloLens coordinate system
# 5) save SfM results to Meshroom SfM JSON file
# 6) run Meshroom: undistortion, depthmap estimation, depth filtering, meshing with output dense pointcloud
# 7) load MVS dense pointcloud
# 8) compose common dense pointcloud
# 9) filter out noise
# 10) calculate the visibility of dense points and save Meshroom SfM JSON file
# 11) run Meshroom: meshing and texturing

import sys
import os
from pathlib import Path
import numpy as np
import json
from src.holo.HoloIO import HoloIO
from src.colmap.ColmapIO import ColmapIO
from src.meshroom.MeshroomIO import MeshroomIO
from src.utils.UtilsMath import UtilsMath

# example dataset
holo_dir = "/local/artwin/mapping/data/benchmark/desk"
uvdata_path = "/local/artwin/mapping/data/uvdata.txt"
out_dir = "/local/artwin/mapping/data/benchmark_results/desk"

# COLMAP - add colmap into the path (may be changed to use docker as for AliceVision)
# AliceVision and Meshroom (create Singularity image from docker to run it widthout sudo)
# 1) execute: singularity build <path_to>/alicevision.sif docker://alicevision/meshroom:2021.1.0-av2.4.0-centos7-cuda10.2
# 2) run simgularity package (does this script)
alice_vision_bin = "/local/artwin/mapping/codes/Meshroom-2021.1.0-av2.4.0-centos7-cuda10.2/aliceVision/bin"


# # 1) read dense pointcloud in world coordinates from HoloLens depthmaps 
holo_io = HoloIO()
# holo_xyz = holo_io.read_dense_pointcloud(holo_dir + "/long_throw_depth", uvdata_path, holo_dir + "/long_throw_depth.csv") 
# holo_io.write_pointcloud_to_file(holo_xyz, out_dir + "/desk.obj")


# # 2) run COLMAP to find "correct" camera poses (TODO: https://github.com/GrumpyZhou/patch2pix)
# Path(out_dir + "/colmap/sparse").mkdir(parents=True, exist_ok=True)
# # os.system(f"colmap automatic_reconstructor --workspace_path {out_dir}/colmap --image_path {holo_dir}/pv")  # 34min - 134 images
# os.system(f"colmap feature_extractor --database_path {out_dir}/colmap/database.db --image_path {holo_dir}/pv --ImageReader.camera_model \"RADIAL\" --ImageReader.single_camera 1")
# os.system(f"colmap exhaustive_matcher --database_path {out_dir}/colmap/database.db")
# os.system(f"colmap mapper --database_path {out_dir}/colmap/database.db --image_path {holo_dir}/pv --output_path {out_dir}/colmap/sparse") # 2min - 134 images


# # 3) load COLMAP & load HoloLens camera poses
colmap_io = ColmapIO()
colmap_cameras, colmap_images, colmap_points = colmap_io.load_model(out_dir + "/colmap/sparse/0")
holo_cameras = holo_io.read_cameras(holo_dir + "/pv.csv")


# # 4) estimate transformation of colmap cameras to HoloLens coordinate system
utils_math = UtilsMath()
colmap_to_holo_transform = utils_math.estimate_colmap_to_holo_transformation(colmap_images, holo_cameras)
colmap_images = utils_math.transform_colmap_images(colmap_images, colmap_to_holo_transform)
colmap_points = utils_math.transform_colmap_points(colmap_points, colmap_to_holo_transform)


# # # 5) save SfM results to Meshroom SfM JSON file
meshroom_io = MeshroomIO()
# meshroom_io.save_colmap_to_json(out_dir + "/sfm.json", holo_dir + "/pv/", colmap_cameras, colmap_images, colmap_points)


# 6) run Meshroom: undistortion, depthmap estimation, depth filtering, meshing with output dense pointcloud, convert resluts to obj
out_cache = out_dir + "/MeshroomCache"
# Path(out_cache + "/ConvertSfMFormat/test").mkdir(parents=True, exist_ok=True)
# os.system(f"{alice_vision_bin}/aliceVision_convertSfMFormat --input {out_dir}/sfm.json --output {out_cache}/ConvertSfMFormat/test/sfm.abc --describerTypes sift --views True --intrinsics True --extrinsics True --structure True --observations True --verboseLevel info")

# Path(out_cache + "/PrepareDenseScene/test").mkdir(parents=True, exist_ok=True)
# os.system(f"{alice_vision_bin}/aliceVision_prepareDenseScene --input {out_cache}/ConvertSfMFormat/test/sfm.abc --output {out_cache}/PrepareDenseScene/test --outputFileType exr --saveMetadata True --saveMatricesTxtFiles False --evCorrection False --verboseLevel info")

# Path(out_cache + "/DepthMap/test").mkdir(parents=True, exist_ok=True)  # 7min - 134imgs  (3s / img in full resolution)
# os.system(f"{alice_vision_bin}/aliceVision_depthMapEstimation --input {out_cache}/ConvertSfMFormat/test/sfm.abc --output {out_dir}/MeshroomCache/DepthMap/test --imagesFolder {out_cache}/PrepareDenseScene/test --downscale 1 --minViewAngle 2.0 --maxViewAngle 70.0 --sgmMaxTCams 10 --sgmWSH 4 --sgmGammaC 5.5 --sgmGammaP 8.0 --refineMaxTCams 6 --refineNSamplesHalf 150 --refineNDepthsToRefine 31 --refineNiters 100 --refineWSH 3 --refineSigma 15 --refineGammaC 15.5 --refineGammaP 8.0 --refineUseTcOrRcPixSize False --exportIntermediateResults False --nbGPUs 0 --verboseLevel info")

# Path(out_cache + "/DepthMapFilter/test").mkdir(parents=True, exist_ok=True)
# os.system(f"{alice_vision_bin}/aliceVision_depthMapFiltering --input {out_cache}/ConvertSfMFormat/test/sfm.abc --output {out_dir}/MeshroomCache/DepthMapFilter/test --depthMapsFolder {out_cache}/DepthMap/test --minViewAngle 2.0 --maxViewAngle 70.0  --nNearestCams 10 --minNumOfConsistentCams 3 --minNumOfConsistentCamsWithLowSimilarity 4 --pixSizeBall 0 --pixSizeBallWithLowSimilarity 0 --computeNormalMaps False --verboseLevel info")

# Path(out_cache + "/Meshing/test").mkdir(parents=True, exist_ok=True)
# os.system(f"{alice_vision_bin}/aliceVision_meshing --input {out_cache}/ConvertSfMFormat/test/sfm.abc --output {out_dir}/MeshroomCache/Meshing/test/densePointCloud.abc --outputMesh {out_dir}/MeshroomCache/Meshing/test/mesh.obj --depthMapsFolder {out_cache}/DepthMap/test  --estimateSpaceFromSfM True --estimateSpaceMinObservations 3 --estimateSpaceMinObservationAngle 10 --maxInputPoints 50000000 --maxPoints 5000000 --maxPointsPerVoxel 1000000 --minStep 2 --partitioning singleBlock --repartition multiResolution --angleFactor 15.0 --simFactor 15.0 --pixSizeMarginInitCoef 2.0 --pixSizeMarginFinalCoef 4.0 --voteMarginFactor 4.0 --contributeMarginFactor 2.0 --simGaussianSizeInit 10.0 --simGaussianSize 10.0 --minAngleThreshold 1.0 --refineFuse True --helperPointsGridSize 10 --nPixelSizeBehind 4.0 --fullWeight 1.0 --voteFilteringForWeaklySupportedSurfaces True --addLandmarksToTheDensePointCloud True --invertTetrahedronBasedOnNeighborsNbIterations 0 --minSolidAngleRatio 0.2 --nbSolidAngleFilteringIterations 0 --colorizeOutput False --maxNbConnectedHelperPoints 50 --saveRawDensePointCloud True --exportDebugTetrahedralization False --seed 0 --verboseLevel info")

# Path(out_cache + "/ConvertSfMFormat/test").mkdir(parents=True, exist_ok=True)
# os.system(f"{alice_vision_bin}/aliceVision_convertSfMFormat --input {out_cache}/Meshing/test/densePointCloud_raw.abc  --output {out_cache}/ConvertSfMFormat/test/mvs_raw.ply --describerTypes sift,unknown --views False --intrinsics False --extrinsics False --structure True --observations False --verboseLevel info")


# # 7) load MVS dense pointcloud
# mvs_xyz = meshroom_io.load_ply_vertices(out_cache + "/ConvertSfMFormat/test/mvs_raw.ply")


# # 8) compose common dense pointcloud
# common_xyz = np.concatenate((holo_xyz, mvs_xyz), axis=1)
# holo_io.write_pointcloud_to_file(common_xyz, out_dir + "/common_pointcloud.obj")


# 9) filter out noise
# # common_xyz = meshroom_io.load_obj_vertices(out_dir + "/common_pointcloud.obj")  # just for testing
# common_xyz_fitered = utils_math.filter_dense_pointcloud_noise_KDtree(common_xyz, 0.05, 50)
# holo_io.write_pointcloud_to_file(common_xyz_fitered, out_dir + "/common_pointcloud_filtered.obj")


# 10) calculate the visibility of dense points and save Meshroom SfM JSON file
# common_xyz_fitered = meshroom_io.load_obj_vertices(out_dir + "/common_pointcloud_filtered.obj")  # just for testing
# visibility_map = utils_math.estimate_visibility(colmap_cameras, colmap_images, common_xyz_fitered)
# meshroom_io.save_merged_mvs_to_json(out_dir + "/holo_and_mvs.json", holo_dir + "/pv/", colmap_cameras, colmap_images, common_xyz_fitered, visibility_map)

# 11) run Meshroom: meshing and texturing
# Path(out_cache + "/ConvertSfMFormat/test_merged").mkdir(parents=True, exist_ok=True)
# os.system(f"{alice_vision_bin}/aliceVision_convertSfMFormat --input {out_dir}/holo_and_mvs.json --output {out_cache}/ConvertSfMFormat/test_merged/sfm.abc --describerTypes sift --views True --intrinsics True --extrinsics True --structure True --observations True --verboseLevel info")

# Path(out_cache + "/PrepareDenseScene/test_merged").mkdir(parents=True, exist_ok=True)
# os.system(f"{alice_vision_bin}/aliceVision_prepareDenseScene --input {out_cache}/ConvertSfMFormat/test_merged/sfm.abc --output {out_cache}/PrepareDenseScene/test_merged --outputFileType exr --saveMetadata True --saveMatricesTxtFiles False --evCorrection False --verboseLevel info")

Path(out_cache + "/Meshing/test_merged").mkdir(parents=True, exist_ok=True)
os.system(f"{alice_vision_bin}/aliceVision_meshing --input {out_cache}/ConvertSfMFormat/test_merged/sfm.abc --output {out_dir}/MeshroomCache/Meshing/test_merged/densePointCloud.abc --outputMesh {out_dir}/MeshroomCache/Meshing/test_merged/mesh.obj --estimateSpaceFromSfM True --saveRawDensePointCloud True --verboseLevel info")

# Path(out_cache + "/Texturing/test_merged").mkdir(parents=True, exist_ok=True)
# os.system(f"{alice_vision_bin}/aliceVision_texturing --input {out_cache}/Meshing/test_merged/densePointCloud.abc --imagesFolder {out_cache}/PrepareDenseScene/test_merged --inputMesh {out_cache}/Meshing/test_merged/mesh.obj --output {out_cache}/Texturing/test_merged --textureSide 8192 --downscale 2 --outputTextureFileType png --unwrapMethod Basic --useUDIM True --fillHoles False --padding 5 --multiBandDownscale 4 --multiBandNbContrib 1 5 10 0 --useScore True --bestScoreThreshold 0.1 --angleHardThreshold 140.0 --processColorspace sRGB --correctEV False --forceVisibleByAllVertices False --flipNormals False --visibilityRemappingMethod PullPush --subdivisionTargetRatio 0.8 --verboseLevel trace ")
