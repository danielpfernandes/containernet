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
from fanet_utils import create_json_drones, kill_containers, save_logs_to_results, set_rest_location, setup_network, time_stamp


def simulate(number_of_drones:int = 5,
            iterations_count: int = 5,
            wait_time_in_seconds: int = 5,
            skip_cli = False):

    START_LOCATION_SERVER = 'touch /data/locations.csv && python /rest/locationRestServer.py &'
    TAIL_LOCATIONS_LOG = "tail -f /data/locations.csv"
    
    iterations_count = int(iterations_count)
    wait_time_in_seconds = int(wait_time_in_seconds)
    ports = [4004, 8008, 8800, 5050, 3030, 5000]
    docker_image = "containernet_example:sawtoothAll"
    drones = []

    create_json_drones(number_of_drones)
    
    info( time_stamp() + '*** Starting monitors\n')
    grafana = subprocess.Popen(
        ["sh", "start_monitor.sh"], stdout=subprocess.PIPE)
    
    time.sleep(wait_time_in_seconds/2)

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
                        volumes=["/tmp/" + name + "/root:/root",
                                 "/tmp/" + name + "/data:/data"],
                        mem_limit=900182016,
                        cpu_shares=2,
                        cpu_period=50000,
                        cpu_quota=10000,
                        position='30,60,10')
        drones.append(drone)

    setup_network(net, bs1, *drones)

    info(time_stamp() + '*** Starting REST server on drones\n')
    for drone in drones:
        drone.cmd(START_LOCATION_SERVER)

    info(time_stamp() + '*** Starting Validation REST server on base station\n')
    bs1.cmd('python /rest/locationRestServer.py &')

    info(time_stamp() + '*** Start drone terminals\n')
    if not skip_cli:
        makeTerm(bs1, cmd="bash")
        for drone in drones:
            makeTerm(drone, cmd=TAIL_LOCATIONS_LOG)

    makeTerm(drones[0], cmd="bash")
    time.sleep(5)

    info(time_stamp() + "*** Configure the node position\n")
    # setNodePosition = 'python {}/setNodePosition.py '.format(path) + sta_drone_send + ' &'
    # os.system(setNodePosition)

    ################################### SCENARIO 01 ###################################
    info(time_stamp() + "*** Scenario 1: BS1 sends initial coordinates to Drone 3\n")
    info(time_stamp() + "*** Scenario 1 Expected: Coordinates set to 50.01 10.01\n")
    set_rest_location(bs1, iterations=iterations_count, interval=wait_time_in_seconds,
                 target=drones[-1].params['ip'], coordinates=' 50.01 10.01')
    ################################### SCENARIO 02 ###################################
    info(time_stamp() + "*** Scenario 2: BS1 changes the destination coordinates through Drone 2\n")
    info(time_stamp() + "*** Scenario 2 Expected: Coordinates set to 50.02 10.02\n")
    set_rest_location(bs1, iterations=iterations_count, interval=wait_time_in_seconds,
                 target=drones[1].params['ip'], coordinates='50.02 10.02')
    ################################### SCENARIO 03 ###################################
    info(time_stamp() + "*** Scenario 3: Drone 5 is compromised and tries to change the destination coordinates\n")
    info(time_stamp() + "*** Scenario 3 Expected: Coordinates keep to 50.02 10.02 (Exploited if set to 50.02 10.03)\n")
    set_rest_location(drones[-2], iterations=iterations_count, interval=wait_time_in_seconds,
                 target=drones[1].params['ip'], coordinates='50.02 10.03')
    ################################### SCENARIO 04 ###################################
    info(time_stamp() + "*** Scenario 4: Connection with the base station is lost and \
the compromised drone tries to change the destination coordinates\n")
    info(time_stamp() + "*** Scenario 4 Expected: Coordinates keep to 50.02 10.02 (Exploited if set to 50.02 10.04)\n")
    bs1.cmd("pkill -9 -f /rest/locationRestServer.py &")
    set_rest_location(drones[-2], iterations=iterations_count, interval=wait_time_in_seconds,
                 target=drones[1].params['ip'], coordinates='50.02 10.04')
    ################################### SCENARIO 05 ###################################
    info(time_stamp() + "*** Scenario 5: A compromised base station joins the network tries to change the destination coordinates\n")
    info(time_stamp() + "*** Scenario 5 Expected: Coordinates keep to 50.02 10.02 (Exploited if set to 50.02 10.05)\n")
    bs2 = net.addStation('base2',
                         ip='10.0.0.101',
                         mac='00:00:10:01:00:00',
                         cls=DockerSta,
                         dimage="containernet_example:sawtoothAll",
                         ports=[4004, 8008, 8800, 5050, 3030, 5000],
                         volumes=["/tmp/base2:/root"])
    net.addLink(bs2, cls=adhoc, intf='base2-wlan0',
                ssid='adhocNet', proto='batman_adv',
                mode='g', channel=5, ht_cap='HT40+')
    makeTerm(bs2, cmd="bash")
    set_rest_location(bs2, iterations=iterations_count, interval=wait_time_in_seconds,
                 target=drones[2].params['ip'], coordinates='50.02 10.05')

    save_logs_to_results()

    info(time_stamp() + '*** Running CLI\n')
    CLI(net)

    info(time_stamp() + '*** Stopping network')
    kill_process()
    net.stop()
    save_logs_to_results()


def kill_process():
    # os.system('pkill -9 -f coppeliaSim')
    os.system('pkill -9 -f simpleTest.py')
    os.system('pkill -9 -f setNodePosition.py')
    os.system('rm examples/uav/data/*')


if __name__ == '__main__':
    setLogLevel('info')
    # Killing old processes
    kill_process()
    kill_containers()

    if len(sys.argv) >= 1:
        print('number of drones: ' + str(sys.argv[1]))
        simulate(number_of_drones=int(sys.argv[1]),
                iterations_count=5,
                wait_time_in_seconds=5,
                skip_cli=False)
    else:
        simulate()