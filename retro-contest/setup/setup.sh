#!/bin/sh

cd `dirname $0`

try_build () {
	docker build -t $@ || exit $?
}

echo - Pulling base images
docker pull -a synthai/retro-agent
docker pull -a synthai/retro-env
if [ "$1" = "rebuild" ]; then
	echo - Building base CPU image
	try_build synthai/retro-agent:bare           --build-arg BASE=ubuntu --build-arg TAG= --pull -f agent.docker ..
	echo - Building base CUDA images
	try_build synthai/retro-agent:bare-cuda8     --build-arg CUDA=8.0 --build-arg CUDNN=6 --pull -f agent.docker ..
	try_build synthai/retro-agent:bare-cuda9     --build-arg CUDA=9.0 --build-arg CUDNN=7 --pull -f agent.docker ..
	echo - Building base TensorFlow images
	try_build synthai/retro-agent:tensorflow-1.4 --build-arg CUDA=8 --build-arg TF=1.4.1        - < agent-tf.docker
	try_build synthai/retro-agent:tensorflow-1.5 --build-arg CUDA=9 --build-arg TF=1.5.1        - < agent-tf.docker
	try_build synthai/retro-agent:tensorflow-1.7 --build-arg CUDA=9 --build-arg TF=1.7.1        - < agent-tf.docker
	try_build synthai/retro-agent:tensorflow-1.8 --build-arg CUDA=9 --build-arg TF=1.8.0        - < agent-tf.docker
	echo - Building base PyTorch images
	try_build synthai/retro-agent:pytorch-0.3    --build-arg PYTORCH=0.3.1                      - < agent-pytorch.docker
	try_build synthai/retro-agent:pytorch-0.4    --build-arg PYTORCH=0.4.0                      - < agent-pytorch.docker
	echo - Building remote image
	try_build synthai/retro-env -f remote-env.docker ..
fi
if [ -n "$(ls ../roms)" ]; then
	echo - Building remote image with ROMs
	docker tag synthai/retro-env synthai/retro-env:bare
	try_build synthai/retro-env -f remote-env-roms.docker ..
fi
echo - Tagging images
docker tag synthai/retro-agent:tensorflow-1.8     synthai/retro-agent:tensorflow-latest
docker tag synthai/retro-agent:tensorflow-latest  synthai/retro-agent:tensorflow
docker tag synthai/retro-agent:pytorch-0.4        synthai/retro-agent:pytorch
docker tag synthai/retro-agent:tensorflow         synthai/retro-agent:latest
docker tag synthai/retro-agent agent

echo - Installing Python library
pip3 install -e '../support[docker,rest]'
