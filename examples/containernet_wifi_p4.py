#!/usr/bin/python
"""
This is the simplest example to showcase Containernet with enabled and containerized P4 AP.
"""
import os

from containernet.net import Containernet
from containernet.node import DockerP4AP
from containernet.cli import CLI
from mininet.log import info, setLogLevel


def topology():
    net = Containernet()

    info('*** Adding docker containers\n')
    sta1 = net.addStation('sta1', ip='10.0.0.1', mac="00:00:00:00:00:01")
    sta2 = net.addStation('sta2', ip='10.0.0.2', mac="00:00:00:00:00:02")

    path = os.path.dirname(os.path.abspath(__file__))
    json_file = '/root/s1-runtime.json' # container directory
    config = path + '/p4_files/commands_ap1.txt'
    args = {'json': json_file, 'switch_config': config}

    info('*** Adding P4 AP\n')
    # IPBASE: subnet from eth0 interface,
    ap1 = net.addAccessPoint('ap1', cls=DockerP4AP, mac="00:00:00:00:00:03",
                             volumes=[path + "/p4_files:/root"],
                             dimage="ramonfontes/bmv2", cpu_shares=20,
                             client_isolation=True, netcfg=True,
                             thriftport=50001,  IPBASE="172.17.0.0/16", **args)
    net.configureWifiNodes()

    info('*** Creating links\n')
    net.addLink(sta1, ap1)
    net.addLink(sta2, ap1)

    info('*** Starting network\n')
    net.build()
    ap1.start([])
    net.staticArp()

    info('*** Running CLI\n')
    CLI(net)

    info('*** Stopping network\n')
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    topology()
