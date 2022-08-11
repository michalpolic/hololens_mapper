#!/usr/bin/env bash

# create common conda enviroment
conda env create -f environment.yml
conda activate meshroom

# download large files 
mkdir ./third_party/Hierarchical-Localization/third_party/netvlad
wget --no-check-certificate https://cvg-data.inf.ethz.ch/hloc/netvlad/Pitts30K_struct.mat -O ./third_party/Hierarchical-Localization/third_party/netvlad/VGG16-NetVLAD-Pitts30K.mat
echo "Wget done"
# create containers
if [ "$(uname) == Darwin" ] || [ "$(expr substr $(uname -s) 1 5)" == "Linux" ]; then
    # Singularity containers
    echo "Init singularity containers"
    singularity build ./alicevision.sif docker://alicevision/meshroom:2021.1.0-av2.4.0-centos7-cuda10.2
    echo "Alicevision done"
    singularity build ./colmap.sif docker://uodcvip/colmap:latest
    echo "Colmap done"
    singularity build --fakeroot ./hloc.sif ./third_party/Hierarchical-Localization/Singularity.def
    echo "Hloc done"
    singularity build --fakeroot ./patchmatchnet.sif ./third_party/PatchmatchNet/Singularity.def
    echo "PatchMatch done"
    singularity build --fakeroot ./ricp.sif ./third_party/Fast-Robust-ICP/Singularity.def
    echo "RICP done"
    singularity build --fakeroot ./poselib.sif ./third_party/poselib/Singularity.def
    echo "Poselib done"
    singularity build --fakeroot ./pixel-perfect-sfm.sif ./third_party/pixel-perfect-sfm/Singularity.def 
    echo "pixel-perfect-sfm done"
    #singularity build --fakeroot ./predator.sif ./third_party/OverlapPredator/Singularity.def
    #echo "Overlap Predator done"
elif [ "$(expr substr $(uname -s) 1 10)" == "MINGW32_NT" ] || [ "$(expr substr $(uname -s) 1 10)" == "MINGW64_NT" ]; then
    # Docker images
    docker pull alicevision/meshroom:2021.1.0-av2.4.0-centos7-cuda10.2
    docker pull uodcvip/colmap:latest
    docker build -t hloc:latest ./third_party/Hierarchical-Localization
    docker build -t patchmatchnet ./third_party/PatchmatchNet
    docker build -t ricp ./third_party/Fast-Robust-ICP
    echo "TODO: containarize Poselib into Docker"
    echo "TODO: containarize pixel-perfect-sfm into Docker"
fi

# create common conda enviroment
conda env create -f environment.yml
conda activate meshroom

# compile the C++ codes
mkdir ./src/utils/srcRenderDepth/build
cd ./src/utils/srcRenderDepth/build
cmake ..
cmake -D Python_EXECUTABLE=$(which python) -D pybind11_DIR="$(conda info --json | jq -r '.active_prefix')/share/cmake/pybind11" ..
cmake --build . --config Release --target install
echo "RenderDepth done"

cd ../../../..
mkdir ./src/meshroom/MeshroomCpp/build
cd ./src/meshroom/MeshroomCpp/build
cmake ..
cmake --build . --config Release --target install
mkdir ./src/meshroom/MeshroomCpp/build
cd ./src/meshroom/MeshroomCpp/build
cmake -D Python_EXECUTABLE=$(which python) -D pybind11_DIR="$(conda info --json | jq -r '.active_prefix')/share/cmake/pybind11" ..
cmake --build . --config Release --target install
echo "Meshroom done"

