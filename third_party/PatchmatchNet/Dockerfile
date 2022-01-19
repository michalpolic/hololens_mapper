FROM nvidia/cuda:10.2-cudnn7-devel
RUN apt-get update -y
RUN apt-get install ffmpeg libsm6 libxext6 -y

RUN : \
    && apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        software-properties-common \
    && add-apt-repository -y ppa:deadsnakes \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        python3.8-venv \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && :

RUN python3.8 -m venv /venv
ENV PATH=/venv/bin:$PYTH

COPY . /app
WORKDIR /app/
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

WORKDIR /app/
ENV PYTHONPATH /app/