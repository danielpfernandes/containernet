import os

from mininet.log import info
from mn_wifi.link import adhoc

from containernet.net import Containernet
from containernet.node import DockerSta
from .utils import time_stamp

ports = [4004, 8008, 8800, 5050, 3030, 5000]
docker_image = "containernet_sawtooth:latest"


def add_link(net: Containernet, node: any):
    net.addLink(node, cls=adhoc, intf=str(node.name) + '-wlan0',
                ssid='adhocNet', proto='batman_adv',
                mode='g', channel=5, ht_cap='HT40+')


def setup_network(net: Containernet, *argv):
    net.setPropagationModel(model="logDistance", exp=4.5)

    info("\n*** Configuring wifi nodes\n")

    net.configureWifiNodes()

    for node in argv:
        add_link(net, node)

    info(time_stamp() + '*** Starting network\n')
    net.build()
    net.start()

    # nodes = net.stations
    # telemetry(nodes=nodes, single=True, data_type='position')

    sta_drone = []
    for n in net.stations:
        sta_drone.append(n.name)
    sta_drone_send = ' '.join(map(str, sta_drone))

    # # set_socket_ip: localhost must be replaced by ip address
    # # of the network interface of your system
    # # The same must be done with socket_client.py
    info(time_stamp() + '*** Starting Socket Server\n')
    net.socketServer(ip='127.0.0.1', port=12345)

    # info("*** Starting CoppeliaSim\n")
    path = os.path.dirname(os.path.abspath(__file__))
    # os.system('{}/CoppeliaSim_Edu_V4_1_0_Ubuntu/coppeliaSim.sh -s {}'
    #             '/simulation.ttt -gGUIITEMS_2 &'.format(path, path))
    # time.sleep(10)

    info("\n*** Perform a simple test\n")
    simple_test = 'python {}/simpleTest.py '.format(
        path) + sta_drone_send + ' &'
    os.system(simple_test)


def create_ip_list_sawtooth_drones(number_of_drones):
    with open('/tmp/drones.txt', 'w') as file:
        for i in range(number_of_drones):
            if i < 10:
                my_ip = '10.0.0.1' + str(i)
                file.write(my_ip + '\n')
            else:
                my_ip = '10.0.0.' + str(i)
                file.write(my_ip + '\n')

    # os.system('cd examples/example-containers && ./build.sh')


def copy_ip_list_to_node(node_name: str):
    os.system("docker cp /tmp/drones.txt mn.{}:/data/drones.txt".format(node_name))


def get_custom_fanet(net: Containernet, number_of_drones: int) -> list:
    info(time_stamp() + '*** Adding docker drones\n')
    drones = []
    for i in range(number_of_drones):

        name = 'drone' + str(i)
        if i < 10:
            my_ip = '10.0.0.1' + str(i)
            my_mac = '00:00:00:00:00:0' + str(i)
        else:
            my_ip = '10.0.0.' + str(i)
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
    return drones


def get_default_base_station(net: Containernet) -> any:
    info(time_stamp() + '*** Adding base station\n')
    return net.addStation('base1',
                          ip='10.0.0.1',
                          mac='00:00:00:00:00:00',
                          cls=DockerSta,
                          dimage=docker_image,
                          ports=ports,
                          port_bindings={88: 8008, 8008: 88},
                          volumes=["/tmp/base1/data:/data"])


def get_default_fanet(net: Containernet) -> list:
    info(time_stamp() + '*** Adding docker drones\n')
    d1 = net.addStation('drone1',
                        ip='10.0.0.249',
                        mac='00:00:00:00:00:01',
                        cls=DockerSta,
                        dimage=docker_image,
                        ports=ports,
                        volumes=["/tmp/drone1/data:/data"],
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
                        dimage=docker_image,
                        ports=ports,
                        volumes=["/tmp/drone2/data:/data"],
                        mem_limit=958182016,
                        cpu_shares=2,
                        cpu_period=50000,
                        cpu_quota=10000,
                        position='31,61,10')

    # Holybro PX4 Vision
    d3 = net.addStation('drone3',
                        ip='10.0.0.251',
                        mac='00:00:00:00:00:03',
                        cls=DockerSta,
                        dimage=docker_image,
                        ports=ports,
                        volumes=["/tmp/drone3/data:/data"],
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
                        dimage=docker_image,
                        ports=ports,
                        volumes=["/tmp/drone4/data:/data"],
                        mem_limit=1900182016,
                        cpu_shares=5,
                        cpu_period=50000,
                        cpu_quota=10000,
                        position='60,20,10')

    # Jetson Nano ARM Cortex-A57 3 GB LPDDR4
    d5 = net.addStation('drone5',
                        ip='10.0.0.253',
                        mac='00:00:00:00:00:05',
                        cls=DockerSta,
                        dimage=docker_image,
                        ports=ports,
                        volumes=["/tmp/drone5/data:/data"],
                        mem_limit=3900182016,
                        cpu_shares=10,
                        cpu_period=50000,
                        cpu_quota=10000,
                        position='20,60,10')

    return [d1, d2, d3, d4, d5]


def start_bs2_station(net):
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

    return bs2
