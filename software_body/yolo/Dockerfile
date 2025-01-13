FROM python:3.10

WORKDIR /app

COPY requirements.txt /app

RUN pip install -r requirements.txt

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        cmake \
        git \
        libgtk2.0-dev \
        pkg-config \
        libavcodec-dev \
        libavformat-dev \
        libswscale-dev \
        libv4l-dev \
        libxvidcore-dev \
        libx264-dev \
        libjpeg-dev \
        libpng-dev \
        libtiff-dev \
        gfortran \
        libblas-dev \
        liblapack-dev \
        libatlas-base-dev \
        libgl1-mesa-glx

RUN pip3 uninstall socketio -y
RUN pip3 install --upgrade python-socketio==5.6.0 websocket-client

COPY . /app


CMD ["python","-u", "main.py"]
