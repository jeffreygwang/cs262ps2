import unittest
from machine import *
import copy
import time
import re

class MachineTest(unittest.TestCase):
  # Runs a simulation of machines with clock rates specified by
  # `machine_clock_rates`, and returns strings of the log files generated.
  def run_simulation(self, machine_clock_rates):
    # Initialize variables and machines.
    num_second_execution = 10
    rand_port = random.randint(8000, 28000)
    ports = [rand_port + i for i in range(len(machine_clock_rates))]
    logs = ['../logs/test-log' + str(i) for i in range(len(machine_clock_rates))]
    machines = [Machine(interactive=False, clock_rate=clock_rate) for clock_rate in machine_clock_rates]

    # Start machines on the relevant ports.
    for i, machine in enumerate(machines):
      machine.start(ports[i], logs[i])

    time.sleep(1)

    # Add non-interactive connections for each machine.
    for i, machine in enumerate(machines):
      ports_copy = copy.deepcopy(ports)
      ports_copy.pop(i)
      machines[i].add_nonint_connections(['localhost' for j in range(len(machines) - 1)], ports_copy)

    time.sleep(num_second_execution)

    # Terminate the machines.
    for m in machines:
      m.kill_flag.set()

    # Read the log files.
    log_values = []
    for logfile in logs:
      with open(logfile) as f:
        log_values.append(f.read())
    return log_values

  # Finds the maximum queue size across each log file.
  def find_max_queue_by_machine(self, logfiles):
    out = []
    # Iterate every log file.
    for logfile in logfiles:
      max_found = 0
      for row in logfile.split('\n'):
        # Find the queue size, and if it's greater than the previous max,
        # increase it.
        match = re.search('[\w\d ]+\t[\d.]+\t(\d+)\t\d+', row)
        try:
          queue_match = match.group(1)
          match_int = int(queue_match)
          if match_int > max_found:
            max_found = match_int
        except:
          pass
      out.append(max_found)
    return out

  # Test that logs are non-empty.
  def test_creates_logs(self):
    logs = self.run_simulation([1, 1, 1])
    self.assertGreater(min([len(log) for log in logs]), 0)

  # Test that a [1, 1, 1] configuration has a low maximum queue size.
  def test_111(self):
    logs = self.run_simulation([1, 1, 1])
    max_queues = self.find_max_queue_by_machine(logs)
    self.assertLessEqual(max(max_queues), 2)

  # Test that a [3, 3, 3] configuration has a low maximum queue size.
  def test_333(self):
    logs = self.run_simulation([3, 3, 3])
    max_queues = self.find_max_queue_by_machine(logs)
    self.assertLessEqual(max(max_queues), 2)

  # Test that a [1, 1, 6] configuration has a high maximum queue size, since
  # the machine with clock-rate 6 should inflate the queues of the 1-rate
  # machines.
  def test_116(self):
    logs = self.run_simulation([1, 1, 6])
    max_queues = self.find_max_queue_by_machine(logs)
    print(max_queues)
    self.assertGreaterEqual(max(max_queues), 5)

if __name__ == '__main__':
  unittest.main(buffer=False)
