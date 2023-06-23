#!/bin/bash

docker build --build-arg IMAGE_VER="$(date +%s)" -t containernet_sawtooth:latest -f Dockerfile.sawtoothAll .
