#!/bin/sh

# Utility script for building and running the docker image

docker rm -f movies
docker image rm -f movies:latest
docker build -t movies:latest .
docker run --name movies -d -p 8000:8000 movies:latest
docker ps