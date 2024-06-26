#!/usr/bin/env python3
import codecs
import logging
import socket
import subprocess
import shlex
from datetime import datetime

import pandas as pd
import requests
from flask import Flask, json, request

LOCATION_REST_SERVER_LOG_PATH = "/data/locationRestServer.log"
LOCATION_DATA_CSV_PATH = '/data/locations.csv'
LOCATION_DATA_JSON_PATH = '/data/locations.json'
CURRENT_DESTINATION_FILE_PATH = '/data/currentDestination.json'
VALIDATION_FILE_PATH = '/tmp/currentDestination.json'
DRONES_IP_ADDRESSES = '/rest/parametrized_drones.json'
BASE_STATION_IP = '10.0.0.1'
LOCALHOST_IP = '0.0.0.0'
LATITUDE_KEY = 'latitude'
LONGITUDE_KEY = 'longitude'
TIMESTAMP_KEY = 'timestamp'

# Places the log files into /data/ directory
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)

logging.basicConfig(filename=LOCATION_REST_SERVER_LOG_PATH,
                    filemode='w',
                    format="%(asctime)s %(name)s:%(levelname)s:%(message)s")

console = logging.StreamHandler()
console.setLevel(logging.INFO)

logging.getLogger().addHandler(console)

api = Flask(__name__)
locations = [{TIMESTAMP_KEY: str(datetime.now().strftime('%Y-%m-%dT%H-%M-%S')), LATITUDE_KEY: 0, LONGITUDE_KEY: 0}]
api.testing = True


def extract_ip():
    """
    Extracts the IP address of the running host in the network
    """
    st = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Points to the base station to get the host IP
        st.connect((BASE_STATION_IP, 5000))
        ip = st.getsockname()[0]
    except ConnectionError:
        print('Could not get the iface address. Using localhost as default')
        ip = LOCALHOST_IP
    finally:
        st.close()
    return ip


localhost_ip = extract_ip()


def propagate_message(new_coordinates):
    """
    Propagates the new coordinates to the other hosts that belongs to the network
    """

    # The file that contains the IP address from the hosts in the network
    logging.info('Set which IP address to use')
    fanet_hosts = open(DRONES_IP_ADDRESSES)
    json_array = json.load(fanet_hosts)
    drones_ip_list = []

    # Verifies all the hosts IP addresses and excludes the source host from the list
    for item in json_array:
        if item['address'] != localhost_ip:
            drones_ip_list.append(item['address'])
    logging.info(
        'Propagating the message to the following hosts: ' + str(drones_ip_list))

    # Send the new coordinates for each host
    for drone_ip in drones_ip_list:
        logging.info('Sending coordinates ' +
                     str(new_coordinates) + ' to host' + str(drone_ip))
        
        # Split the command into a list of arguments
        command = shlex.split(f'setLocation.py {drone_ip} {new_coordinates[LATITUDE_KEY]} {new_coordinates[LONGITUDE_KEY]}')

        # Pass the list of arguments to Popen
        result = subprocess.Popen(command, stdout=subprocess.PIPE)
        logging.debug(result)


def compare_coordinates(reference_host, request_info):
    """
    Compares the latitude and longitude between the reference host and the request
        :param reference_host Reference host JSON files
        :param request_info Request content in JSON format
        Returns True if the values matches
    """
    return reference_host[LATITUDE_KEY] == request_info[LATITUDE_KEY] \
        and reference_host[LONGITUDE_KEY] == request_info[LONGITUDE_KEY]


def validate_coordinates_with_base_station(request_json, base_station_url):
    """
    Validates the coordinates before propagate the information to other hosts
        :request_json Request content in JSON format
        :base_station_url Base station validation REST API endpoint
        Returns True if the validation is successful
    """
    error_message = 'Propagation of coordinates does not match with the base station information. Validation failed'
    success_message = 'Base Station matches with the request. Validation successful!'

    logging.info('Retrieving destination coordinates from base station')
    current_location = requests.get(base_station_url)

    logging.info(current_location)
    logging.info('Base station response: ' + str(current_location.content))
    logging.info('New coordinates payload' + str(request_json))

    if compare_coordinates(json.loads(current_location.content), request_json) and current_location.status_code == 200:
        logging.info(success_message)
        return True
    logging.error(error_message)
    return False


def save_location_data(request_json):
    locations.append(request_json)
    print(locations)
    pd.read_json(json.dumps(locations)).to_csv(LOCATION_DATA_CSV_PATH)
    with open(LOCATION_DATA_JSON_PATH, 'wb') as f:
        json.dump(locations, codecs.getwriter('utf-8')(f), ensure_ascii=False)
    with open(CURRENT_DESTINATION_FILE_PATH, 'wb') as f:
        json.dump(request_json, codecs.getwriter('utf-8')(f), ensure_ascii=False)


@api.route('/locations', methods=['GET', 'POST'])
def handle_locations():
    # If the request is a POST method, then it will store the coordinates into the location data files
    if request.method == 'POST':
        save_location_data(request.get_json())
        return json.dumps(locations)

    # If the request is a GET method, then it will return the coordinate history stored in the location data JSON file
    return json.dumps(locations)


def propagate(propagation_request):
    # Add the new coordinate in the JSON and CSV files
    save_location_data(propagation_request.get_json())

    # Propagate the message to the other hosts in the network
    propagate_message(propagation_request.get_json())
    return json.dumps(locations)


@api.route('/propagate', methods=['POST'])
def propagate_locations():
    """
    Propagates the coordinates change request using this REST API
    """

    # Validates if the new coordinates information matches with the values stored in the base station current request
    try:
        base_station_url = 'http://' + BASE_STATION_IP + ':5000/validate'
        if validate_coordinates_with_base_station(request.get_json(), base_station_url):
            return propagate(request)
        else:
            # Fails if the validation does not match
            return 'Propagation failed', 500

    # If the connection with the base station is lost, show must go on :)
    except ConnectionError:
        error_message = 'Connection with the base station failed. '
        warning_message = '!!!!!!!!!!!!!!!! PROPAGATING INFORMATION WITHOUT VALIDATION !!!!!!!!!!!!!!'
        logging.error(error_message)
        logging.warning(warning_message)
        propagate(request)
        return error_message + warning_message, 203


@api.route('/validate', methods=['GET'])
def validate_locations():
    return json.dumps(json.load(open(VALIDATION_FILE_PATH)))


if __name__ == '__main__':
    api.run(host=LOCALHOST_IP, debug=False)
