FROM nvidia/cuda
RUN apt-get update -y
RUN apt-get install python3.8 python3-pip unzip wget -y

COPY . /app
WORKDIR /app/
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

WORKDIR /app/
ENV PYTHONPATH /app/