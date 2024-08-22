#!/usr/bin/python
"""
This is the simplest example to showcase Containernet with enabled and containerized P4 switch.
"""
import os

from containernet.net import Containernet
from containernet.node import DockerP4Switch
from containernet.cli import CLI
from mininet.log import info, setLogLevel


def topology():
    net = Containernet()

    info('*** Adding docker containers\n')
    h1 = net.addHost('h1', mac="00:00:00:00:00:01")
    h2 = net.addHost('h2', mac="00:00:00:00:00:02")

    path = os.path.dirname(os.path.abspath(__file__))
    json_file = '/root/s1-runtime.json'
    config = path + '/p4_files/commands_s1.txt'
    args = {'json': json_file, 'switch_config': config}

    info('*** Adding P4 Switch\n')
    # IPBASE: subnet from eth0 interface,
    s1 = net.addSwitch('s1', cls=DockerP4Switch,
                        volumes=[path + "/p4_files:/root"],
                        dimage="ramonfontes/bmv2", cpu_shares=20,
                       netcfg=True, thriftport=50001,
                        IPBASE="172.17.0.0/16", **args)

    info('*** Configuring WiFi nodes\n')
    net.configureWifiNodes()

    net.addLink(h1, s1)
    net.addLink(h2, s1)

    info('*** Starting network\n')
    net.build()
    s1.start([])
    net.staticArp()

    info('*** Running CLI\n')
    CLI(net)

    info('*** Stopping network\n')
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    topology()