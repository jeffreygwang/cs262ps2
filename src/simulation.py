"""
Goal: cleanly simulate X seconds of runtime.
Runs X machines and then logs results.
"""

import random
from machine import Machine
import time
import copy

num_second_execution = 20
logfiles = ["l1.txt", "l2.txt", "l3.txt", "l4.txt"]
rand_port = random.randint(8000, 28000)
ports = [rand_port, rand_port + 1, rand_port + 2, rand_port+3]
hosts = ['localhost' for i in range(len(ports))]

print(f"Initializing machines on ports {ports}.")
machines = [Machine(interactive=False), Machine(interactive=False), Machine(interactive=False), Machine(interactive=False)]
for i in range(len(machines)):
    machines[i].start(ports[i], logfiles[i])

time.sleep(1)

print("Adding ports.")
for i in range(len(machines)):
    ports_copy = copy.deepcopy(ports)
    hosts_copy = copy.deepcopy(hosts)
    ports_copy.pop(i)
    hosts_copy.pop(i)
    machines[i].add_nonint_connections(hosts_copy, ports_copy)

time.sleep(1)

print("Running machines.")
time.sleep(num_second_execution)
for m in machines:
    m.kill_flag.set()

print(f"Done simulating for {num_second_execution} seconds. Quit now.")







