.PHONY: docker-build

docker-build:
	@echo "Building and running with Docker Compose..."
	$(DOCKER_COMPOSE) up --build

help:
	@echo "Makefile commands:"
	@echo "docker-build - Build and run the containers using Docker Compose."