#!/usr/bin/python
"""
This is the most simple example to showcase Containernet.
"""
import os
import subprocess
import sys
import time

from mininet.cli import CLI
from mininet.log import info, setLogLevel
from mn_wifi.link import adhoc

from containernet.net import Containernet
from containernet.node import DockerSta
from containernet.term import makeTerm
from fanet_utils import create_txt_drones, get_sawtooth_destination, initialize_parameterized_sawtooth, \
    save_logs_to_results, validate_scenario, kill_containers, \
    kill_process, set_sawtooth_location, set_rest_location, setup_network, time_stamp


def simulate(number_of_drones=5,
             iterations_count: int = 5,
             wait_time_in_seconds: int = 5,
             skip_cli=False):
    iterations_count = int(iterations_count)
    wait_time_in_seconds = int(wait_time_in_seconds)
    should_open_xterm = not skip_cli
    ports = [4004, 8008, 8800, 5050, 3030, 5000]
    docker_image = "containernet_example:sawtoothAll"
    drones = []

    create_txt_drones(number_of_drones)

    info(time_stamp() + '*** Starting monitors\n')
    grafana = subprocess.Popen(
        ["sh", "start_monitor.sh"], stdout=subprocess.PIPE)

    time.sleep(wait_time_in_seconds / 2)

    net = Containernet()

    info(time_stamp() + '*** Adding base station\n')

    bs1 = net.addStation('base1',
                         ip='10.0.0.1',
                         mac='00:00:00:00:00:00',
                         cls=DockerSta,
                         dimage=docker_image,
                         ports=ports,
                         port_bindings={88: 8008, 8008: 88},
                         volumes=["/tmp/base1/data:/data"])

    info(time_stamp() + '*** Adding docker drones\n')

    for i in range(number_of_drones):
        name = 'drone' + str(i)
        my_ip = '10.0.0.1' + str(i)
        if i < 10:
            my_mac = '00:00:00:00:00:0' + str(i)
        else:
            my_mac = '00:00:00:00:00:' + str(i)
        drone = net.addStation(name,
                               ip=my_ip,
                               mac=my_mac,
                               cls=DockerSta,
                               dimage=docker_image,
                               ports=ports,
                               volumes=["/tmp/" + name + "/data:/data"],
                               mem_limit=900182016,
                               cpu_shares=2,
                               cpu_period=50000,
                               cpu_quota=10000,
                               position='30,60,10')
        drones.append(drone)

    setup_network(net, bs1, *drones)

    info(time_stamp() + '*** Starting Sawtooth on the Base Station ***\n')
    initialize_parameterized_sawtooth(should_open_xterm, 0, should_open_xterm, bs1)

    info(time_stamp() + '*** Starting Sawtooth on the Drones ***\n')
    initialize_parameterized_sawtooth(should_open_xterm, 0, should_open_xterm, *drones)

    info(time_stamp() + '*** Start base terminal\n')
    makeTerm(bs1, cmd="bash")

    info(time_stamp() + '*** Waiting until the the Sawtooth peer connection\n')
    time.sleep(60)
    # info(time_stamp() + "*** Configure the node position\n")
    # setNodePosition = 'python {}/setNodePosition.py '.format(path) + sta_drone_send + ' &'
    # os.system(setNodePosition)

    # Common variables
    sc06_coords = {'lat': '5001', 'long': '1001'}
    sc07_coords = {'lat': '5002', 'long': '1002'}
    sc08_coords = '5002 1003'
    sc09_coords = {'lat': '5002', 'long': '1004'}
    sc10_coords = '5002 1005'
    expected_sc06 = '50011001'
    expected_sc07 = '50021002'
    expected_sc09 = '50041004'

    ################################### SCENARIO 06 ###################################
    info(time_stamp() + "*** Scenario 6: BS1 sends the new coordinates and the Sawtooth" \
                        " network validates the update of the information\n")
    info(time_stamp() + "*** Scenario 6 Expected: Coordinates set to 50011001101\n")
    set_sawtooth_location(bs1, sc06_coords, iterations=iterations_count, interval=wait_time_in_seconds)
    validate_scenario(net, expected_sc06, get_destinations(*drones))

    ################################### SCENARIO 07 ###################################
    info(time_stamp() + "*** Scenario 7: BS1 sends changes the coordinates and the Sawtooth" \
                        " network validates the update of the information\n")
    info(time_stamp() + "*** Scenario 7 Expected: Coordinates set to 50021002102\n")
    set_sawtooth_location(bs1, sc07_coords, iterations=iterations_count, interval=wait_time_in_seconds)
    validate_scenario(net, expected_sc07, get_destinations(*drones))

    ################################### SCENARIO 08 ###################################
    info(time_stamp() + "*** Scenario 8: A  Drone 5 is compromised and tries to change the destination coordinates" \
                        "using the unprotected REST Interface\n")
    info(time_stamp() + "*** Scenario 3 Expected: Coordinates keep to 50021002102 (Exploited if set to 50301030303)\n")
    set_rest_location(drones[0], iterations_count, wait_time_in_seconds, target='10.0.0.249', coordinates=sc08_coords)
    validate_scenario(net, expected_sc07, get_destinations(*drones))

    ################################### SCENARIO 09 ###################################
    info(time_stamp() + "*** Scenario 9: Connection with the base station is lost and" \
                        "drone2 needs to rearrange the destination coordinates for emergency purposes\n")
    info(time_stamp() + "*** Scenario 9 Expected: Coordinates keep to 50041004104\n")
    os.system('docker container rm mn.base1 --force')
    set_sawtooth_location(drones[-1], sc09_coords, iterations=iterations_count, interval=wait_time_in_seconds)
    validate_scenario(net, expected_sc09, get_destinations(*drones))

    ################################### SCENARIO 10 ###################################
    info(time_stamp() + "*** Scenario 10:  compromised base station joins the network tries to change the destination" \
                        " coordinates through the unsecure REST interface\n")
    info(time_stamp() + "*** Scenario 3 Expected: Coordinates keep to 50041004104 (Exploited if set to 50501050505)\n")
    bs2 = start_bs2_station(net)
    if not skip_cli:
        makeTerm(bs2, cmd="bash")
    set_rest_location(bs2, iterations_count, wait_time_in_seconds, '10.0.0.250', coordinates=sc10_coords)
    validate_scenario(net, expected_sc07, get_destinations(*drones))

    info(time_stamp() + "*** Saving Drones logs at /tmp/drone/data/sawtooth/\n")
    save_sawtooth_logs(*drones)
    save_logs_to_results()

    if not skip_cli:
        info(time_stamp() + '*** Running CLI\n')
        CLI(net)

    info(time_stamp() + '*** Stopping network\n')
    kill_process()
    net.stop()


def start_bs2_station(net):
    bs2 = net.addStation('base2',
                         ip='10.0.0.101',
                         mac='00:00:00:00:00:00',
                         cls=DockerSta,
                         dimage="containernet_example:sawtoothAll",
                         ports=[4004, 8008, 8800, 5050, 3030, 5000],
                         volumes=["/tmp/base2:/root"])
    net.addLink(bs2, cls=adhoc, intf='base2-wlan0',
                ssid='adhocNet', proto='batman_adv',
                mode='g', channel=5, ht_cap='HT40+')

    return bs2


def save_sawtooth_logs(*args):
    for node in args:
        node.cmd('mkdir /data/sawtooth/ && cp /var/log/sawtooth/* /data/sawtooth/')


def get_destinations(*args):
    destinations = []
    for drone in args:
        destinations.append(get_sawtooth_destination(drone))
    return destinations


if __name__ == '__main__':
    setLogLevel('info')
    # Killing old processes
    kill_process()
    kill_containers()

    if len(sys.argv) == 4:
        skip_cli = True
        print('number of drones: ' + sys.argv[1])
        print('iterations: ' + sys.argv[2])
        print('wait time: ' + sys.argv[3])
        simulate(number_of_drones=int(sys.argv[1]),
                 iterations_count=int(sys.argv[2]),
                 wait_time_in_seconds=int(sys.argv[3]),
                 skip_cli=skip_cli)
    else:
        simulate()
