upload:
	rm -rf dist
	python setup.py sdist
	twine upload dist/*

test:
	find . -name '*.pyc' -delete
	docker build -f test.dockerfile -t quay.io/synthai/institute:test .
	docker run -v /usr/bin/docker:/usr/bin/docker -v /root/.docker:/root/.docker -v /var/run/docker.sock:/var/run/docker.sock --net=host quay.io/synthai/institute:test

build:
	find . -name '*.pyc' -delete
	docker build -t quay.io/synthai/institute .
	docker build -f test.dockerfile -t quay.io/synthai/institute:test .

push:
	find . -name '*.pyc' -delete
	docker build -t quay.io/synthai/institute .
	docker build -f test.dockerfile -t quay.io/synthai/institute:test .

	docker push quay.io/synthai/institute
	docker push quay.io/synthai/institute:test

test-push:
	docker build -f test.dockerfile -t quay.io/synthai/institute:test .
	docker push quay.io/synthai/institute:test
