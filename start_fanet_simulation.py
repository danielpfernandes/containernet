from datetime import datetime, timedelta
import numbers
import os
import time


def main_menu() -> int:
    os.system("clear")
    print("########## FANET SIMULATOR ##########")
    print("[1] Start unprotected scenarios")
    print("[2] Start Sawtooth scenarios")
    print("[3] Quit")

    option = get_option()
    if option == 1:
        unprotected_scenarios_menu()
    elif option == 2:
        consensus_algorithm_menu()
    elif option == 3:
        exit()
    else:
        print("Invalid option")
        time.sleep(2)
    option = main_menu()


def unprotected_scenarios_menu():
    os.system("clear")
    print("########## Unprotected (REST-based) FANET Communication ########## ")
    print("[1] Run default test case (5 preconfigured drones)")
    print("[2] Run custom test case")
    print("[3] Return to main menu")
    option = get_option()
    if option == 1 or option == 2:
        run_unprotected_scenario(option);
        return
    elif option == 3:
        main_menu()
        return
    else:
        print("Invalid option")
        time.sleep(2)
    option = unprotected_scenarios_menu()


def sawtooth_scenarios_menu():
    os.system("clear")
    print("########## Secured (Hyperledger Sawtooth-based) FANET Communication ##########")
    print("[1] Run default test case (5 preconfigured drones)")
    print("[2] Run custom test case")
    print("[3] Return to main menu")
    option = get_option()
    if option == 1 or option == 2:
        run_sawtooth_scenario(option)
        return
    elif option == 3:
        main_menu()
        return
    else:
        print("Invalid option")
        time.sleep(2)
    option = sawtooth_scenarios_menu()


def consensus_algorithm_menu():
    os.system("clear")
    print("########## Secured (Hyperledger Sawtooth-based) FANET Communication ##########")
    print("Please select the consensus algorithm")
    print("[1] PoET")
    print("[2] PBFT")
    print("[3] RAFT")
    print("[4] Return to main menu")
    option = get_option()
    if option == 1 or option == 2 or option == 3:
        sawtooth_scenarios_menu()
        return
    elif option == 4:
        main_menu()
        return
    else:
        print("Invalid option")
        time.sleep(2)
    option = consensus_algorithm_menu()


def run_unprotected_scenario(option: int):
    os.system("clear")
    if option == 1:
        os.system("sudo python examples/fanet-sawtooth/fanet_simulation_wifi_unsecured.py")
        pause()
    elif option == 2:
        number_of_drones = validate_number_of_drones(3)
        iterations, interval = get_iterations_and_interval()
        os.system("sudo python examples/fanet-sawtooth/fanet_simulation_wifi_unsecured_parameterized.py " 
        + str(number_of_drones) + " "
        + str(iterations) + " "
        + str(interval))
        pause()


def run_sawtooth_scenario(option: int):
    os.system("clear")
    if option == 1:
        os.system("sudo python examples/fanet-sawtooth/fanet_simulation_wifi_sawtooth.py")
        pause()
    elif option == 2:
        number_of_drones = validate_number_of_drones(3)
        iterations, interval = get_iterations_and_interval()
        os.system("sudo python examples/fanet-sawtooth/fanet_simulation_wifi_sawtooth_parameterized.py " 
        + str(number_of_drones) + " "
        + str(iterations) + " "
        + str(interval))
        pause()


def get_iterations_and_interval() -> tuple:
    print("Enter how many times the drones will trigger the messaging events")
    iterations = get_option()
    print("Enter the interval in seconds between the messages")
    interval = get_option()
    total_seconds = (int(interval)+1) * int(iterations) * 5
    m, s = divmod(total_seconds, 60)
    h, m = divmod(m, 60)
    print("Estimated simulation time: " + f'{h:d}:{m:02d}:{s:02d}')
    return iterations, interval


def validate_number_of_drones(minimum_qty: int) -> int:
    number_of_drones = 0
    while number_of_drones < minimum_qty:
        print("Enter the number of  drones")
        number_of_drones = get_option()
        if number_of_drones < minimum_qty:
            print ("Invalid quantity, this simulation required at least {:d} drones".format(minimum_qty))
    return number_of_drones


def get_option() -> int:
    return int(input("Enter your option: "))


def pause():
    input("Press any key to continue...")


main_menu()
