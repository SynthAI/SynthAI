# A Dockerfile that sets up a full Lab install
FROM quay.io/synthai/lab:base

RUN apt-get update \
    && apt-get install -y libav-tools \
    python-numpy \
    python-scipy \
    python-pyglet \
    python-setuptools \
    libpq-dev \
    libjpeg-dev \
    curl \
    cmake \
    swig \
    python-opengl \
    libboost-all-dev \
    libsdl2-dev \
    wget \
    unzip \
    git \
    xpra \
    libav-tools  \
    python3-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && easy_install pip

WORKDIR /usr/local/lab/
RUN mkdir -p lab && touch lab/__init__.py
COPY ./lab/version.py ./lab/
COPY ./requirements.txt ./
COPY ./setup.py ./
COPY ./tox.ini ./

RUN pip install tox
# Install the relevant dependencies. Keep printing so Travis knows we're alive.
RUN ["bash", "-c", "( while true; do echo '.'; sleep 60; done ) & tox --notest"]

# Finally, clean cached code (including dot files) and upload our actual code!
RUN mv .tox /tmp/.tox && rm -rf .??* * && mv /tmp/.tox .tox
COPY . /usr/local/lab/

ENTRYPOINT ["/usr/local/lab/bin/docker_entrypoint"]
CMD ["tox"]
