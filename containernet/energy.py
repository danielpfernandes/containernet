"""
   @author: Ramon Fontes (ramon.fontes@ufrn.br)
"""
import re
import psutil

from threading import Thread as thread
from time import sleep, time

from mininet.log import error


class Energy(object):

    thread_ = None

    def __init__(self, nodes):
        Energy.thread_ = thread(target=self.start, args=(nodes,))
        Energy.thread_.daemon = True
        Energy.thread_._keep_alive = True
        Energy.thread_.start()

    def start(self, nodes):

        for node in nodes:
            for intf in node.wintfs.values():
                intf.rx, intf.tx = 0, 0

        try:
            while self.thread_._keep_alive:
               sleep(1)  # set sleep time to 1 second
               for node in nodes:
                   for intf in node.wintfs.values():
                       intf.consumption += self.get_energy(intf)
        except:
            error("Error with the energy consumption function\n")

    def get_energy(self, intf):
        """
        Calculates power consumption based on voltage, current, and duration.

        voltage (float): Processor operating voltage in volts (V).
        current (float): Current consumed by the processor in amperes (A).
        Returns: float: Energy consumed in watt-hours (Wh).
        """

        cpu_utilization = psutil.cpu_percent(interval=1) / 100  # Fração de utilização (0 a 1)
        power = intf.voltage * intf.current * cpu_utilization  # Potência em watts
        return power / 3600  # Converte para watt-hora (Wh) considerando um intervalo de 1 segundo