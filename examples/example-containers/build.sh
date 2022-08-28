#!/bin/bash

docker build -t containernet_example:sawtoothAll -f Dockerfile.sawtoothAll --build-arg IMAGE_VER=$(date +%Y%m%d-%H%M%S) .