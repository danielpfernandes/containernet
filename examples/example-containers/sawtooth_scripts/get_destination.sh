#!/bin/bash
if [ ! -d "/data/" ]; then
    mkdir /data
    mkdir /data/sawtooth
fi
intkey list > /data/sawtooth/locations.log
