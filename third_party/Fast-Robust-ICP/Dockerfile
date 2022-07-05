FROM nvidia/cuda:10.2-devel-ubuntu18.04

RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN apt-get update && apt-get -y install cmake libeigen3-dev
RUN apt-get install -y git build-essential
RUN cd /usr/include && ln -sf eigen3 eigen && mkdir build && cd build && cmake -DCMAKE_BUILD_TYPE=Release .. && make