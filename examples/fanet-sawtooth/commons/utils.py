import os
from datetime import datetime

from mininet.log import info
from mn_wifi.link import adhoc

from containernet.net import Containernet


def time_stamp() -> str:
    return str(datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%s'))


def coord_time_stamp() -> str:
    return str(datetime.now().strftime('%Y-%m-%dT%H-%M-%S'))


def save_logs_to_results(prefix_name: str = 'sim'):
    os.system('chown -R $USER:$USER /tmp/drone* /tmp/base*')
    os.system('zip -r results/' + prefix_name + str(coord_time_stamp) + '.zip /tmp/drone* tmp/base*')


def kill_process():
    # os.system('pkill -9 -f coppeliaSim')
    os.system('pkill -9 -f simpleTest.py')
    os.system('pkill -9 -f setNodePosition.py')
    os.system('rm -f examples/uav/data/*')


def kill_containers():
    os.system('rm -f examples/example-containers/rest_scripts/parametrized_drones.json')
    os.system('rm -f examples/example-containers/sawtooth_scripts/drones.txt')
    os.system('kill -TERM $(pgrep -f prometheus)')
    os.system('rm -f examples/uav/data/*')
    os.system('rm -rf /tmp/poet-shared')
    os.system('docker container rm $(docker ps -a -q) --force')
    os.system('service docker restart')
    os.system('cd examples/example-containers && ./build.sh')
