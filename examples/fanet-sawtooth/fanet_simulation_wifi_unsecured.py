#!/usr/bin/python
"""
This is the simplest example to showcase Containernet.
"""
import os
import subprocess
import sys
import time

from mininet.cli import CLI
from mininet.log import info, setLogLevel
from mn_wifi.link import adhoc

from commons.network import setup_network
from commons.rest import set_rest_location
from commons.utils import time_stamp, kill_process, kill_containers, save_logs_to_results
from containernet.net import Containernet
from containernet.node import DockerSta
from containernet.term import makeTerm


def simulate(iterations_count: int = 5,
             wait_time_in_seconds: int = 5):
    start_location_server = 'touch /data/locations.csv && python /rest/locationRestServer.py &'
    tail_locations_log = "tail -f /data/locations.csv"

    setLogLevel('info')

    iterations_count = int(iterations_count)
    wait_time_in_seconds = int(wait_time_in_seconds)

    net = Containernet()

    info(time_stamp() + '*** Starting monitors\n')
    grafana = subprocess.Popen(
        ["sh", "start_monitor.sh"], stdout=subprocess.PIPE)

    info(time_stamp() + '*** Adding base station\n')
    bs1 = net.addStation('base1',
                         ip='10.0.0.1',
                         mac='00:00:00:00:00:00',
                         cls=DockerSta,
                         dimage="containernet_sawtooth:latest",
                         ports=[4004, 8008, 8800, 5050, 3030, 5000],
                         volumes=["/tmp/base1/data:/data"])

    info(time_stamp() + '*** Adding docker drones\n')

    # Intel Aero Ready to Fly Drone processor
    d1 = net.addStation('drone1',
                        ip='10.0.0.249',
                        mac='00:00:00:00:00:01',
                        cls=DockerSta,
                        dimage="containernet_sawtooth:latest",
                        ports=[4004, 8008, 8800, 5050, 3030, 5000],
                        volumes=["/tmp/drone1/root:/root",
                                 "/tmp/drone1/data:/data"],
                        mem_limit=3900182016,
                        cpu_shares=5,
                        cpu_period=50000,
                        cpu_quota=10000,
                        position='30,60,10')

    # OSD33x Family Processor
    d2 = net.addStation('drone2',
                        ip='10.0.0.250',
                        mac='00:00:00:00:00:02',
                        cls=DockerSta,
                        dimage="containernet_sawtooth:latest",
                        ports=[4004, 8008, 8800, 5050, 3030, 5000],
                        volumes=["/tmp/drone2/root:/root",
                                 "/tmp/drone2/data:/data"],
                        mem_limit=958182016,
                        cpu_shares=2,
                        cpu_period=50000,
                        cpu_quota=10000,
                        position='31,61,10')

    # Holy-bro PX4 Vision
    d3 = net.addStation('drone3',
                        ip='10.0.0.251',
                        mac='00:00:00:00:00:03',
                        cls=DockerSta,
                        dimage="containernet_sawtooth:latest",
                        ports=[4004, 8008, 8800, 5050, 3030, 5000],
                        volumes=["/tmp/drone3/root:/root",
                                 "/tmp/drone3/data:/data"],
                        mem_limit=3900182016,
                        cpu_shares=5,
                        cpu_period=50000,
                        cpu_quota=10000,
                        position='50,50,10')

    # Raspberry Pi4 with 2GB RAM
    d4 = net.addStation('drone4',
                        ip='10.0.0.252',
                        mac='00:00:00:00:00:04',
                        cls=DockerSta,
                        dimage="containernet_sawtooth:latest",
                        ports=[4004, 8008, 8800, 5050, 3030, 5000],
                        volumes=["/tmp/drone4/root:/root",
                                 "/tmp/drone4/data:/data"],
                        mem_limit=1900182016,
                        cpu_shares=5,
                        cpu_period=50000,
                        cpu_quota=10000,
                        position='60,20,10')

    # Jetson Nano ARM Cortex-A57 3 GB PDDL4
    d5 = net.addStation('drone5',
                        ip='10.0.0.253',
                        mac='00:00:00:00:00:05',
                        cls=DockerSta,
                        dimage="containernet_sawtooth:latest",
                        ports=[4004, 8008, 8800, 5050, 3030, 5000],
                        volumes=["/tmp/drone5/root:/root",
                                 "/tmp/drone5/data:/data"],
                        mem_limit=3900182016,
                        cpu_shares=10,
                        cpu_period=50000,
                        cpu_quota=10000,
                        position='20,60,10')

    setup_network(net, bs1, d1, d2, d3, d4, d5)

    info(time_stamp() + '*** Starting REST server on drones\n')
    d1.cmd(start_location_server)
    d2.cmd(start_location_server)
    d3.cmd(start_location_server)
    d4.cmd(start_location_server)
    d5.cmd(start_location_server)

    info(time_stamp() + '*** Starting Validation REST server on base station\n')
    bs1.cmd('python /rest/locationRestServer.py &')

    info(time_stamp() + '*** Start drone terminals\n')
    makeTerm(bs1, cmd="bash")
    makeTerm(d1, cmd=tail_locations_log)
    makeTerm(d2, cmd=tail_locations_log)
    makeTerm(d3, cmd=tail_locations_log)
    makeTerm(d4, cmd=tail_locations_log)
    makeTerm(d5, cmd=tail_locations_log)

    time.sleep(5)

    info(time_stamp() + "*** Configure the node position\n")
    # setNodePosition = 'python {}/setNodePosition.py '.format(path) + sta_drone_send + ' &'
    # os.system(setNodePosition)

    # -------------------------------------- STAGE 1A -------------------------------------- #
    info(time_stamp() + "*** Stage 1A: BS1 sends initial coordinates to Drone 3\n")
    info(time_stamp() + "*** Stage 1A Expected: Coordinates set to 50.01 10.01\n")
    set_rest_location(bs1, iterations=iterations_count, interval=wait_time_in_seconds,
                      target='10.0.0.251', coordinates=' 50.01 10.01')
    # -------------------------------------- STAGE 2A -------------------------------------- #
    info(time_stamp() + "*** Stage 2A: BS1 changes the destination coordinates through Drone 2\n")
    info(time_stamp() + "*** Stage 2A Expected: Coordinates set to 50.02 10.02\n")
    set_rest_location(bs1, iterations=iterations_count, interval=wait_time_in_seconds,
                      target='10.0.0.250', coordinates='50.02 10.02')
    # -------------------------------------- STAGE 3A -------------------------------------- #
    info(time_stamp() + "*** Stage 3A: Drone 5 is compromised and tries to change the destination coordinates\n")
    info(time_stamp() + "*** Stage 3A Expected: Coordinates keep to 50.02 10.02 (Exploited if set to 50.02 10.03)\n")
    set_rest_location(d5, iterations=iterations_count, interval=wait_time_in_seconds,
                      target='10.0.0.249', coordinates='50.02 10.03')
    # -------------------------------------- STAGE 4A -------------------------------------- #
    info(time_stamp() + "*** Stage 4A: Connection with the base station is lost and \
the compromised drone tries to change the destination coordinates\n")
    info(time_stamp() + "*** Stage 4A Expected: Coordinates keep to 50.02 10.02 (Exploited if set to 50.02 10.04)\n")
    os.system('docker container rm mn.base1 --force')
    set_rest_location(d5, iterations=iterations_count, interval=wait_time_in_seconds,
                      target='10.0.0.249', coordinates='50.02 10.04')
    # -------------------------------------- STAGE 5A -------------------------------------- #
    info(
        time_stamp() + "*** Stage 5A: A compromised base station joins the network tries to change the destination coordinates\n")
    info(time_stamp() + "*** Stage 5A Expected: Coordinates keep to 50.02 10.02 (Exploited if set to 50.02 10.05)\n")
    bs2 = net.addStation('base2',
                         ip='10.0.0.101',
                         mac='00:00:00:00:00:00',
                         cls=DockerSta,
                         dimage="containernet_sawtooth:latest",
                         ports=[4004, 8008, 8800, 5050, 3030, 5000],
                         volumes=["/tmp/base2:/root"])
    net.addLink(bs2, cls=adhoc, intf='base2-wlan0',
                ssid='adhocNet', proto='batman_adv',
                mode='g', channel=5, ht_cap='HT40+')
    makeTerm(bs2, cmd="bash")
    set_rest_location(bs2, iterations=iterations_count, interval=wait_time_in_seconds,
                      target='10.0.0.251', coordinates='50.02 10.05')

    save_logs_to_results()

    info(time_stamp() + '*** Running CLI\n')
    CLI(net)

    info(time_stamp() + '*** Stopping network')
    kill_process()
    net.stop()
    save_logs_to_results()
    grafana.kill()


if __name__ == '__main__':
    setLogLevel('info')
    # Killing old processes
    kill_process()
    kill_containers()

    if len(sys.argv) == 3:
        print('iterations: ' + sys.argv[1])
        print('wait time: ' + sys.argv[2])
        simulate(iterations_count=int(sys.argv[1]),
                 wait_time_in_seconds=int(sys.argv[2]))
    else:
        simulate()
