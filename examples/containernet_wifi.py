#!/usr/bin/python
"""
This is the simplest example to showcase Containernet with Mininet-WiFi.
"""
from containernet.net import Containernet
from containernet.node import DockerSta
from containernet.cli import CLI
from mininet.log import info, setLogLevel


def topology():
    net = Containernet()

    info('*** Adding docker containers\n')
    sta1 = net.addStation('sta1', ip='10.0.0.1', mac='00:02:00:00:00:01',
                          cls=DockerSta, dimage="ramonfontes/bmv2", cpu_shares=20)
    sta2 = net.addStation('sta2', ip='10.0.0.2', mac='00:02:00:00:00:02',
                          cls=DockerSta, dimage="ramonfontes/bmv2", cpu_shares=20)
    ap1 = net.addAccessPoint('ap1')

    info('*** Configuring WiFi nodes\n')
    net.configureWifiNodes()

    info('*** Creating links\n')
    net.addLink(sta1, ap1)
    net.addLink(sta2, ap1)

    info('*** Starting network\n')
    net.start()

    info('*** Running CLI\n')
    CLI(net)

    info('*** Stopping network\n')
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    topology()

