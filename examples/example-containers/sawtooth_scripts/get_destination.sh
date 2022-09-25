#!/bin/bash
if [ ! -d "/data" ]; then
    mkdir /data
fi
if [ ! -d "/data/sawtooth" ]; then
    mkdir /data/sawtooth
fi
intkey list > /data/sawtooth/locations.log
