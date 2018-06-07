.PHONY: install test

install:
	pip install -r requirements.txt

base:
	docker pull ubuntu:14.04
	docker tag ubuntu:14.04 quay.io/synthai/lab:base
	docker push quay.io/synthai/lab:base

test:
	docker build -f test.dockerfile -t quay.io/synthai/lab:test .
	docker push quay.io/synthai/lab:test

upload:
	rm -rf dist
	python setup.py sdist
	twine upload dist/*

docker-build:
	docker build -t quay.io/synthai/lab .

docker-run:
	docker run -ti quay.io/synthai/lab bash
