"""
   @author: Ramon Fontes (ramon.fontes@ufrn.br)
"""
import re

from threading import Thread as thread
from datetime import datetime
from time import sleep

from mininet.log import error


class Energy(object):

    thread_ = None

    def __init__(self, nodes):
        Energy.thread_ = thread(target=self.start, args=(nodes,))
        Energy.thread_.daemon = True
        Energy.thread_._keep_alive = True
        Energy.thread_.start()

    def start(self, nodes):
        try:
            while self.thread_._keep_alive:
                sleep(0.1)  # set sleep time to 1 second
                for node in nodes:
                    if(self.thread_._keep_alive):
                        node.consumption += self.get_energy(node)
        except:
            error("Error with the energy consumption function\n")

    def get_cpu_usage_v2(self, node):
        cpu_usage = node.pexec("grep '^usage_usec' /sys/fs/cgroup/cpu.stat | awk '{print $2}' | tr -cd '0-9'", shell=True)[0]
        try:
            return int(cpu_usage)
        except:
            return 0

    def calculate_cpu_percent_v2(self, node):
        usage_start = self.get_cpu_usage_v2(node)
        sleep(0.1)
        usage_end = self.get_cpu_usage_v2(node)
        cpu_delta = usage_end - usage_start

        cpu_percent = (cpu_delta / 1e6) * 100 / 0.1
        return cpu_percent

    def get_energy(self, node):
        """
        Calculates power consumption based on voltage, current, and duration.

        voltage (float): Processor operating voltage in volts (V).
        current (float): Current consumed by the processor in amperes (A).
        Returns: float: Energy consumed in watt-hours (Wh).
        """
        current_datetime = datetime.now()
        cpu_percent = self.calculate_cpu_percent_v2(node)
        formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
        node.pexec('echo {} > /tmp/consumption'.format(node.consumption), shell=True)
        cpu_utilization = cpu_percent / 100
        power = node.voltage * node.current * cpu_utilization  # Power in watts
        power_converted = power * 0.1 / 3600  # Converts to watt-hours (Wh) considering a 1-second interval
        return power_converted
