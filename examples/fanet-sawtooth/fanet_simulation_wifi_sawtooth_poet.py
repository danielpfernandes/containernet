#!/usr/bin/python
"""
This is an example of use case for FANET simulation using Containernet with Hyperledger Sawtooth and PoET Consensus.
"""
import os
import subprocess
import sys
import time

from mininet.cli import CLI
from mininet.log import info, setLogLevel

from commons.network import setup_network, get_default_fanet, start_bs2_station, get_default_base_station
from commons.rest import set_rest_location
from commons.sawtooth import initialize_sawtooth, set_sawtooth_location, validate_scenario, save_sawtooth_logs, \
    get_destinations
from commons.utils import time_stamp, kill_process, kill_containers, save_logs_to_results
from containernet.net import Containernet
from containernet.term import makeTerm

CONSENSUS_ALGORITHM = "poet"


def simulate(iterations_count: int = 5,
             wait_time_in_seconds: float = 5,
             skip_cli_simulation=False):
    iterations_count = int(iterations_count)
    wait_time_in_seconds = float(wait_time_in_seconds)
    should_open_xterm = not skip_cli_simulation
    setLogLevel('info')

    os.system('cd examples/example-containers && ./build.sh')

    info(time_stamp() + '*** Starting monitors\n')
    grafana = subprocess.Popen(
        ["sh", "start_monitor.sh"], stdout=subprocess.PIPE)

    time.sleep(2.5)

    net = Containernet()

    bs1 = get_default_base_station(net)

    drones = get_default_fanet(net)

    setup_network(net, bs1, *drones)

    info(time_stamp() + '*** Starting Sawtooth on the Base Station ***\n')
    initialize_sawtooth(should_open_xterm, 0, should_open_xterm, CONSENSUS_ALGORITHM, bs1)

    info(time_stamp() + '*** Starting Sawtooth on the Drones (drone5 expected to fail) ***\n')
    initialize_sawtooth(should_open_xterm, 0, should_open_xterm, CONSENSUS_ALGORITHM, *drones[0:4])

    if not skip_cli_simulation:
        info(time_stamp() + '*** Start drone terminals\n')
        makeTerm(bs1, cmd="bash")
        for drone in drones:
            makeTerm(drone, cmd="bash")

    info(time_stamp() + '*** Waiting until the the Sawtooth peer connection\n')
    time.sleep(60)
    # info(time_stamp() + "*** Configure the node position\n")
    # setNodePosition = 'python {}/setNodePosition.py '.format(path) + sta_drone_send + ' &'
    # os.system(setNodePosition)

    # Common variables
    sc06_coordinates = {'lat': '5001', 'long': '1001'}
    sc07_coordinates = {'lat': '5002', 'long': '1002'}
    sc08_coordinates = '5002 1003'
    sc09_coordinates = {'lat': '5002', 'long': '1004'}
    sc10_coordinates = '5002 1005'
    expected_sc06 = '50011001'
    expected_sc07 = '50021002'
    expected_sc09 = '50021004'

    # -------------------------------------- STAGE 1B -------------------------------------- #
    info(time_stamp() + "*** Stage 1B: BS1 sends the new coordinates and the Sawtooth"
                        " network validates the update of the information\n")
    info(time_stamp() + "*** Stage 1B Expected: Coordinates set to 50011001101\n")
    set_sawtooth_location(bs1, sc06_coordinates, iterations=iterations_count, interval=wait_time_in_seconds)
    validate_scenario(net, expected_sc06, get_destinations(*drones[0:4]))

    # -------------------------------------- STAGE 2B -------------------------------------- #
    info(time_stamp() + "*** Stage 2B: BS1 sends changes the coordinates and the Sawtooth"
                        " network validates the update of the information\n")
    info(time_stamp() + "*** Stage 2B Expected: Coordinates set to 50021002102\n")
    set_sawtooth_location(bs1, sc07_coordinates, iterations=iterations_count, interval=wait_time_in_seconds)
    validate_scenario(net, expected_sc07, get_destinations(*drones[0:4]))

    # -------------------------------------- STAGE 3B -------------------------------------- #
    info(time_stamp() + "*** Stage 3B: A  Drone 5 is compromised and tries to change the destination coordinates"
                        "using the unprotected REST Interface\n")
    info(time_stamp() + "*** Stage 3B Expected: Coordinates keep to 50021002102 (Exploited if set to 50301030303)\n")
    set_rest_location(drones[-1], iterations_count, wait_time_in_seconds, target='10.0.0.249',
                      coordinates=sc08_coordinates)
    validate_scenario(net, expected_sc07, get_destinations(*drones[0:4]))

    # -------------------------------------- STAGE 4B -------------------------------------- #
    info(time_stamp() + "*** Stage 4B: Connection with the base station is lost and"
                        " drone2 needs to rearrange the destination coordinates for emergency purposes\n")
    info(time_stamp() + "*** Stage 4B Expected: Coordinates keep to 50041004104\n")
    os.system('docker container rm mn.base1 --force')
    set_sawtooth_location(drones[1], sc09_coordinates, iterations=iterations_count, interval=wait_time_in_seconds)
    validate_scenario(net, expected_sc09, get_destinations(*drones[0:4]))

    # -------------------------------------- STAGE 5B -------------------------------------- #
    info(time_stamp() + "*** Stage 5B:  compromised base station joins the network tries to change the destination"
                        " coordinates through the unsecure REST interface\n")
    info(time_stamp() + "*** Stage 5B Expected: Coordinates keep to 50041004104 (Exploited if set to 50501050505)\n")
    bs2 = start_bs2_station(net)
    if not skip_cli_simulation:
        makeTerm(bs2, cmd="bash")
    set_rest_location(bs2, iterations_count, wait_time_in_seconds, '10.0.0.250', coordinates=sc10_coordinates)
    validate_scenario(net, expected_sc07, get_destinations(*drones[0:4]))

    info(time_stamp() + "*** Saving Drones logs at /tmp/drone/data/sawtooth/\n")
    save_sawtooth_logs(*drones[0:4])
    save_logs_to_results()

    if not skip_cli_simulation:
        info(time_stamp() + '*** Running CLI\n')
        CLI(net)

    info(time_stamp() + '*** Stopping network\n')
    kill_process()
    net.stop()
    grafana.kill()


if __name__ == '__main__':
    setLogLevel('info')
    # Killing old processes
    kill_process()
    kill_containers()

    if len(sys.argv) == 3 and str(sys.argv[0]) != "sudo":
        should_skip_cli = True
        print('iterations: ' + sys.argv[1])
        print('wait time: ' + sys.argv[2])
        simulate(iterations_count=int(sys.argv[1]),
                 wait_time_in_seconds=float(sys.argv[2]),
                 skip_cli_simulation=should_skip_cli)
    else:
        simulate()
