#!/usr/bin/env bash

if [ "$(uname)" == "Darwin" || "$(expr substr $(uname -s) 1 5)" == "Linux"]; then
    # Singularity containers
    singularity build ./alicevision.sif docker://alicevision/meshroom:2021.1.0-av2.4.0-centos7-cuda10.2
    singularity build ./colmap.sif docker://uodcvip/colmap:latest
    singularity build --fakeroot ./hloc.sif ./third_party/Hierarchical-Localization/Singularity.def
elif [ "$(expr substr $(uname -s) 1 10)" == "MINGW32_NT" || "$(expr substr $(uname -s) 1 10)" == "MINGW64_NT"]; then
    # Docker images
    docker pull alicevision/meshroom:2021.1.0-av2.4.0-centos7-cuda10.2
    docker pull uodcvip/colmap:latest
    docker build -t hloc:latest ./third_party/Hierarchical-Localization
fi

# create common conda enviroment
conda env create -f environment.yml
conda activate meshroom

# compile the C++ codes
mkdir ./src/utils/srcRenderDepth/build
cd ./src/utils/srcRenderDepth/build
cmake ..
cmake --build . --config Release --target install

cd ../../../..
mkdir ./src/meshroom/MeshroomCpp/build
cd ./src/meshroom/MeshroomCpp/build
cmake ..
cmake --build . --config Release --target install
