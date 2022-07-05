FROM colmap/colmap:latest
RUN apt-get update -y
RUN apt-get install python3 python3-pip unzip wget -y

COPY . /app
WORKDIR /app/
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

WORKDIR /colmap/
RUN git pull
WORKDIR /colmap/build
RUN cmake ..
RUN make -j install

RUN pip3 install git+https://github.com/mihaidusmanu/pycolmap
WORKDIR /app/
ENV PYTHONPATH /app/