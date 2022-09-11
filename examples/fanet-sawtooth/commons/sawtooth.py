import os
import sys
import time

from mininet.log import info

from containernet.term import makeTerm
from .utils import time_stamp, kill_process, coord_time_stamp

cmd_keep_alive = '; bash'

consensus_algorithms = ["pbft", "poet"]


def create_ip_list_sawtooth_drones(number_of_drones):
    with open('examples/example-containers/sawtooth_scripts/drones.txt', 'w') as file:
        for i in range(number_of_drones):
            my_ip = '10.0.0.1' + str(i)
            file.write(my_ip + '\n')

    os.system('cd examples/example-containers && ./build.sh')


def verify_consensus_algorithm(consensus: str):
    if consensus not in consensus_algorithms:
        print("Invalid consensus algorithm. choose between:")
        print(*consensus_algorithms)
        quit()


def initialize_sawtooth(should_open_terminal=False,
                        wait_time_in_seconds: int = 0,
                        keep_terminal_alive=False,
                        consensus_algorithm="poet",
                        *args):
    verify_consensus_algorithm(consensus_algorithm)
    for node in args:
        start_validator(node, should_open_terminal,
                        wait_time_in_seconds,
                        keep_terminal_alive,
                        consensus_algorithm=consensus_algorithm,
                        is_parameterized=False)
        start_rest_api(node, should_open_terminal=False)
        start_transaction_processors(node, consensus_algorithm, should_open_terminal=False)
        start_consensus_mechanism(node, consensus_algorithm, should_open_terminal=False)


def initialize_parameterized_sawtooth(should_open_terminal=True,
                                      wait_time_in_seconds: int = 0,
                                      keep_terminal_alive=False,
                                      consensus_algorithm="poet",
                                      *args):
    for node in args:
        start_validator(node,
                        should_open_terminal,
                        wait_time_in_seconds,
                        keep_terminal_alive,
                        consensus_algorithm,
                        is_parameterized=True)
        start_rest_api(node, should_open_terminal=False)
        start_transaction_processors(node, consensus_algorithm, should_open_terminal=False)
        start_consensus_mechanism(node, consensus_algorithm, should_open_terminal=False)


def start_validator(node: any,
                    should_open_terminal: bool = False,
                    wait_time_in_seconds: int = 2,
                    keep_terminal_alive=False,
                    consensus_algorithm="poet",
                    is_parameterized=False):
    """Start the Validator

    Args:
        node (any): Mininet node
        should_open_terminal (bool, optional): If True, opens a new terminal. Defaults to False.
        wait_time_in_seconds (int, optional): Wait time in seconds before leaving the command
        keep_terminal_alive (bool, optional): Leave the terminal open if it fails
        consensus_algorithm (string, optional): Consensus algorithm
        is_parameterized (bool, optional): If true, runs customized topology
    """
    verify_consensus_algorithm(consensus_algorithm)
    station_name = str(node.name)
    if is_parameterized and str(station_name) == "base1":
        command = 'bash /sawtooth_scripts/validator_{}_parametrized.sh base1'.format(consensus_algorithm)
    elif is_parameterized and station_name.startswith('drone'):
        command = 'bash /sawtooth_scripts/validator_{}_parametrized.sh drone'.format(consensus_algorithm)
    else:
        command = 'bash /sawtooth_scripts/validator_{}.sh {}'.format(consensus_algorithm, station_name)

    info(time_stamp() + '*** Generating sawtooth keypair for ' + station_name + ' ***\n')

    if str(station_name) == "base1":
        info(time_stamp() + '*** Create the Genesis Block on Base Station\n')
        info(time_stamp() + '*** Create a batch to initialize the consensus settings on the Base Station\n')
        info(time_stamp() + '*** Combining batches in one genesis batch on Base Station ***\n')

    if should_open_terminal:
        if keep_terminal_alive:
            command += cmd_keep_alive
        makeTerm(node=node, title=station_name + ' Validator', cmd=command)
        time.sleep(wait_time_in_seconds)
    else:
        node.cmd(command + ' &')
        time.sleep(wait_time_in_seconds)


def start_rest_api(node: any,
                   should_open_terminal: bool = False,
                   keep_terminal_alive=False):
    """Start the REST API

    Args:
        node (any): Mininet node
        should_open_terminal (bool, optional): If True, opens a new terminal. Defaults to False.
        keep_terminal_alive (bool, optional): Leave the terminal open if it fails
    """
    station_name = str(node.name)
    station_ip = str(node.params.get('ip'))
    command = 'sudo -u sawtooth sawtooth-rest-api -v --connect tcp://' + station_ip + ':4004'

    info(time_stamp() + '*** Start REST API for ' + station_name + ' ***\n')

    if should_open_terminal:
        if keep_terminal_alive:
            command += cmd_keep_alive
        makeTerm(node=node, title=station_name + ' REST API', cmd=command)
    else:
        node.cmd(command + ' &')


def start_transaction_processors(node: any,
                                 consensus_algorithm: str = "poet",
                                 should_open_terminal: bool = False,
                                 wait_time_in_seconds: int = 0,
                                 keep_terminal_alive=False):
    """Start the transaction processors

    Args:
        node (any): Mininet node
        consensus_algorithm (str, optional): Consensus algorithm
        should_open_terminal (bool, optional):
            If True, opens a new terminal for each processor. Defaults to False.
        wait_time_in_seconds (int, optional): Wait time in seconds before leaving the command
        keep_terminal_alive (bool, optional): Leave the terminal open if it fails
    """

    station_name = str(node.name)
    station_ip = str(node.params.get('ip'))
    command_settings_tp = 'sudo -u sawtooth settings-tp -v --connect tcp://' + \
                          station_ip + ':4004'
    command_intkey_tp = 'sudo -u sawtooth intkey-tp-python -v --connect tcp://' + \
                        station_ip + ':4004'
    command_poet_validator_registry_tp = ""
    if consensus_algorithm == "poet":
        command_poet_validator_registry_tp = 'sudo -u sawtooth poet-validator-registry-tp -v --connect tcp://' + \
                                             station_ip + ':4004'

    info(time_stamp() + '*** Start Transaction Processors for ' + station_name + ' ***\n')

    if should_open_terminal:
        if keep_terminal_alive:
            command_settings_tp += cmd_keep_alive
            command_intkey_tp += cmd_keep_alive
            if consensus_algorithm == "poet":
                command_poet_validator_registry_tp += cmd_keep_alive

        makeTerm(node=node,
                 title=station_name + ' Settings Transaction Processor', cmd=command_settings_tp)
        time.sleep(wait_time_in_seconds)
        makeTerm(node=node,
                 title=station_name + ' Intkey Transaction Processor', cmd=command_intkey_tp)
        time.sleep(wait_time_in_seconds)
        if consensus_algorithm == "poet":
            makeTerm(node=node,
                     title=station_name + ' PoET Validator Registry Transaction Processor',
                     cmd=command_poet_validator_registry_tp)
    else:
        node.cmd(command_settings_tp + ' &')
        time.sleep(wait_time_in_seconds)
        node.cmd(command_intkey_tp + ' &')
        time.sleep(wait_time_in_seconds)
        if consensus_algorithm == "poet":
            node.cmd(command_poet_validator_registry_tp + ' &')


def start_consensus_mechanism(node: any,
                              consensus_algorithm: str = "poet",
                              should_open_terminal: bool = False,
                              keep_terminal_alive=False):
    """Start the consensus engine

    Args:
        node (any): Mininet node
        consensus_algorithm (str, optional): Consensus algorithm
        should_open_terminal (bool, optional): If True, opens a new terminal. Defaults to False.
        keep_terminal_alive (bool, optional): Leave the terminal open if it fails
    """

    station_name = str(node.name)
    station_ip = str(node.params.get('ip'))
    command = '{}-engine -vv --connect tcp://localhost:5050 --component tcp://'.format(consensus_algorithm) + \
              station_ip + ':4004'

    info(time_stamp() + '*** Start Consensus Engine for ' + station_name + ' ***\n')

    if should_open_terminal:
        if keep_terminal_alive:
            command += cmd_keep_alive
        makeTerm(node=node, title=station_name + ' Consensus Mechanism', cmd=command + cmd_keep_alive)
    else:
        node.cmd(command + ' &')


def set_sawtooth_location(station: any,
                          coordinate: dict,
                          iterations: int = 10,
                          interval: int = 10):
    """Sets the coordinates to the destination of the FANET

    Args:
        station (any): Mininet node
        coordinate (dict): Coordinates (Lat, Long)
        iterations (int): Number of iterations
        interval (int): Interval between iterations
    """
    for number in range(iterations):
        station.cmd(
            "intkey set " + str(coord_time_stamp()) + " " + str(coordinate['lat']) + str(coordinate['long']))
        time.sleep(interval)
        info(time_stamp() + " Iteration number " + str(number + 1) + " of " + str(iterations) + "\n")


def get_sawtooth_destination(node: any) -> str:
    """Get the coordinates stored in the node transactions

    Args:
        node (any): Mininet node

    Returns:
        str: The coordinate registries
    """
    node.cmd("sh /sawtooth_scripts/get_destination.sh")

    return node.cmd("cat /data/sawtooth/locations.log")


def is_simulation_successful(expected_coord, coordinates) -> bool:
    for result in coordinates:
        if expected_coord not in result:
            return False
    return True


def validate_scenario(net, expected_coord, coordinates):
    for coord in coordinates:
        info('Node coordinates: \n' + str(coord) + '\n')
    if is_simulation_successful(expected_coord, coordinates):
        info(time_stamp() + " ******************** SIMULATION SUCCESSFUL! ********************\n")
    else:
        info(time_stamp() + " ******************** SIMULATION FAILED! ********************\n")
        kill_process()
        net.stop()
        sys.exit(1)


def save_sawtooth_logs(*args):
    for node in args:
        node.cmd('mkdir /data/sawtooth/ && cp /var/log/sawtooth/* /data/sawtooth/')


def get_destinations(*args):
    destinations = []
    for drone in args:
        destinations.append(get_sawtooth_destination(drone))
    return destinations
