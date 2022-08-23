import numbers
import os
import time


def main_menu() -> int:
    os.system("clear")
    print("########## FANET SIMULATOR ##########")
    print("[1] Start unprotected scenarios")
    print("[2] Start Sawtooth scenarios")
    return get_option()


def unprotected_scenarios_menu():
    os.system("clear")
    print("########## Unprotected (REST-based) FANET Communication ########## ")
    print("[1] Run default test case (5 preconfigured drones)")
    print("[2] Run custom test case")
    print("[3] Return to main menu")
    option = get_option()
    while option != 0:
        if option == 1 or option == 2:
            run_unprotected_scenario(option);
            break
        elif option == 3:
            main_menu()
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
    while option != 0:
        if option == 1 or option == 2:
            run_sawtooth_scenario(option);
            break
        elif option == 3:
            main_menu()
        else:
            print("Invalid option")
            time.sleep(2)
        option = sawtooth_scenarios_menu()


def run_unprotected_scenario(option: int):
    os.system("clear")
    if option == 1: os.system("sudo python examples/fanet-sawtooth/fanet_simulation_wifi_unsecured.py")
    elif option == 2:
        print("Enter the number of  drones")
        number_of_drones = get_option()
        os.system("sudo python examples/fanet-sawtooth/fanet_simulation_wifi_unsecured_parameterized.py " + str(number_of_drones))


def run_sawtooth_scenario(option: int):
    os.system("clear")
    if option == 1: os.system("sudo python examples/fanet-sawtooth/fanet_simulation_wifi_sawtooth.py")
    elif option == 2:
        print("Enter the number of  drones")
        number_of_drones = get_option()
        os.system("sudo python examples/fanet-sawtooth/fanet_simulation_wifi_sawtooth_parameterized.py " + str(number_of_drones))


def get_option() -> int:
    return int(input("Enter your option: "))


option = main_menu()

while option != 0:
    if option == 1:
        unprotected_scenarios_menu()
        break
    elif option == 2:
        sawtooth_scenarios_menu()
        break
    else:
        print("Invalid option")
        time.sleep(2)
    option = main_menu()
