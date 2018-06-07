# A Dockerfile that sets up a full Lab install
FROM ubuntu:16.04

RUN apt-get update \
    && apt-get install -y libav-tools \
    python-setuptools \
    libpq-dev \
    libjpeg-dev \
    curl \
    cmake \
    swig \
    freeglut3 \
    python-opengl \
    libboost-all-dev \
    libglu1-mesa \
    libglu1-mesa-dev \
    libsdl2-2.0-0\
    libgles2-mesa-dev \
    libsdl2-dev \
    wget \
    unzip \
    git \
    xserver-xorg-input-void \
    xserver-xorg-video-dummy \
    python-gtkglext1 \
    xpra \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && easy_install pip

WORKDIR /usr/local/lab
RUN mkdir -p lab && touch lab/__init__.py
COPY ./lab/version.py ./lab
COPY ./requirements.txt .
COPY ./setup.py .
RUN pip install -e .[all]

# Finally, upload our actual code!
COPY . /usr/local/lab

WORKDIR /root
ENTRYPOINT ["/usr/local/lab/bin/docker_entrypoint"]
