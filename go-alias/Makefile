build:
	docker build -t quay.io/synthai/gonode .

push: build
	docker push quay.io/synthai/gonode

run: build
	docker run -it -p 3000:5000 -e AWS_DEFAULT_REGION=us-west-2 quay.io/synthai/gonode
