#!/usr/bin/python
"""
This is an example of use case for FANET simulation using Containernet with Hyperledger Sawtooth and PoET Consensus.
"""
import os
import subprocess
import sys
import time

from mininet.log import info, setLogLevel

from commons.network import setup_network, start_bs2_station, get_default_base_station, create_ip_list_sawtooth_drones, \
    get_custom_fanet
from commons.rest import set_rest_location
from commons.sawtooth import set_sawtooth_location, validate_scenario, initialize_parameterized_sawtooth, \
    save_sawtooth_logs, get_destinations
from commons.utils import time_stamp, kill_process, kill_containers, save_logs_to_results
from containernet.net import Containernet
from containernet.term import makeTerm

CONSENSUS_ALGORITHM = "poet"


def simulate(number_of_drones=5,
             iterations_count: int = 5,
             wait_time_in_seconds: float = 5,
             skip_cli_simulation=False):
    iterations_count = int(iterations_count)
    wait_time_in_seconds = float(wait_time_in_seconds)
    should_open_xterm = not skip_cli_simulation
    setLogLevel('info')

    create_ip_list_sawtooth_drones(number_of_drones)

    info(time_stamp() + '*** Starting monitors\n')
    grafana = subprocess.Popen(
        ["sh", "start_monitor.sh"], stdout=subprocess.PIPE)

    time.sleep(2.5)

    net = Containernet()

    bs1 = get_default_base_station(net)

    drones = get_custom_fanet(net, number_of_drones=number_of_drones)

    setup_network(net, bs1, *drones)

    info(time_stamp() + '*** Starting Sawtooth on the Base Station ***\n')
    initialize_parameterized_sawtooth(should_open_xterm, 0, should_open_xterm, CONSENSUS_ALGORITHM, bs1)

    info(time_stamp() + '*** Starting Sawtooth on the Drones ***\n')
    initialize_parameterized_sawtooth(should_open_xterm, 0, should_open_xterm, CONSENSUS_ALGORITHM, *drones)

    info(time_stamp() + '*** Start base terminal\n')
    makeTerm(bs1, cmd="bash")

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

    # -------------------------------------- SCENARIO 06 -------------------------------------- #
    info(time_stamp() + "*** Scenario 6: BS1 sends the new coordinates and the Sawtooth"
                        " network validates the update of the information\n")
    info(time_stamp() + "*** Scenario 6 Expected: Coordinates set to 50011001101\n")
    set_sawtooth_location(bs1, sc06_coordinates, iterations=iterations_count, interval=wait_time_in_seconds)
    validate_scenario(net, expected_sc06, get_destinations(*drones))

    # -------------------------------------- SCENARIO 07 -------------------------------------- #
    info(time_stamp() + "*** Scenario 7: BS1 sends changes the coordinates and the Sawtooth"
                        " network validates the update of the information\n")
    info(time_stamp() + "*** Scenario 7 Expected: Coordinates set to 50021002102\n")
    set_sawtooth_location(bs1, sc07_coordinates, iterations=iterations_count, interval=wait_time_in_seconds)
    validate_scenario(net, expected_sc07, get_destinations(*drones))

    # -------------------------------------- SCENARIO 08 -------------------------------------- #
    info(time_stamp() + "*** Scenario 8: A  Drone 5 is compromised and tries to change the destination coordinates"
                        "using the unprotected REST Interface\n")
    info(time_stamp() + "*** Scenario 8 Expected: Coordinates keep to 50021002102 (Exploited if set to 50301030303)\n")
    set_rest_location(drones[0], iterations_count, wait_time_in_seconds, target='10.0.0.249',
                      coordinates=sc08_coordinates)
    validate_scenario(net, expected_sc07, get_destinations(*drones))

    # -------------------------------------- SCENARIO 09 -------------------------------------- #
    info(time_stamp() + "*** Scenario 9: Connection with the base station is lost and"
                        "drone2 needs to rearrange the destination coordinates for emergency purposes\n")
    info(time_stamp() + "*** Scenario 9 Expected: Coordinates keep to 50041004104\n")
    os.system('docker container rm mn.base1 --force')
    set_sawtooth_location(drones[-1], sc09_coordinates, iterations=iterations_count, interval=wait_time_in_seconds)
    validate_scenario(net, expected_sc09, get_destinations(*drones))

    # -------------------------------------- SCENARIO 10 -------------------------------------- #
    info(time_stamp() + "*** Scenario 10:  compromised base station joins the network tries to change the destination"
                        " coordinates through the unsecure REST interface\n")
    info(time_stamp() + "*** Scenario 10 Expected: Coordinates keep to 50041004104 (Exploited if set to 50501050505)\n")
    bs2 = start_bs2_station(net)
    if not skip_cli_simulation:
        makeTerm(bs2, cmd="bash")
    set_rest_location(bs2, iterations_count, wait_time_in_seconds, '10.0.0.250', coordinates=sc10_coordinates)
    validate_scenario(net, expected_sc07, get_destinations(*drones))

    info(time_stamp() + "*** Saving Drones logs at /tmp/drone/data/sawtooth/\n")
    save_sawtooth_logs(*drones)
    save_logs_to_results()

    if not skip_cli_simulation:
        info(time_stamp() + '*** Running CLI\n')
        # CLI(net)

    info(time_stamp() + '*** Stopping network\n')
    kill_process()
    net.stop()
    grafana.kill()


if __name__ == '__main__':
    setLogLevel('info')
    # Killing old processes
    kill_process()
    kill_containers()

    if len(sys.argv) == 4:
        skip_cli = False
        print('number of drones: ' + sys.argv[1])
        print('iterations: ' + sys.argv[2])
        print('wait time: ' + sys.argv[3])
        simulate(number_of_drones=int(sys.argv[1]),
                 iterations_count=int(sys.argv[2]),
                 wait_time_in_seconds=float(sys.argv[3]),
                 skip_cli_simulation=skip_cli)
    else:
        simulate()
