import json
import os
import time

from mininet.log import info
from .utils import time_stamp


def create_json_drones(number_of_drones):
    my_drones = []
    for i in range(number_of_drones):
        name = 'drone' + str(i)
        my_ip = '10.0.0.1' + str(i)
        my_drones.append({'id': name, 'address': my_ip})

    with open('examples/example-containers/rest_scripts/parametrized_drones.json', 'w') as file:
        json.dump(my_drones, file)

    os.system('cd examples/example-containers && ./build.sh')


def set_rest_location(
        station: any, iterations=10, interval=10, target='10.0.0.1', coordinates='0 0'):
    """Set the drone location

    Args:
        station (any): Mininet node (source station)
        iterations (int, optional): Numbers of iterations to run the command. Defaults to 10.
        interval (int, optional): Interval in seconds between each iteration. Defaults to 10.
        target (str, optional): Target node (drone). Defaults to '10.0.0.249'.
        coordinates (str, optional):
            Coordinates in format <latitude> <longitude>. Defaults to '0 0'.
    """
    for number in range(iterations):
        station.cmd('python /rest/setLocation.py '
                    + target + ' '
                    + coordinates + ' True &')
        time.sleep(interval)
        info(time_stamp() + " Iteration number " + str(number + 1) + " of " + str(iterations) + "\n")
