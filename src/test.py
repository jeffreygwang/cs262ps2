import unittest
from machine import *
import copy
import time
import re

class MachineTest(unittest.TestCase):
  def run_simulation(self, machine_clock_rates):
    num_second_execution = 10
    rand_port = random.randint(8000, 28000)
    ports = [rand_port + i for i in range(len(machine_clock_rates))]
    logs = ['../logs/test-log' + str(i) for i in range(len(machine_clock_rates))]
    machines = [Machine(interactive=False, clock_rate=clock_rate) for clock_rate in machine_clock_rates]
    for i, machine in enumerate(machines):
      machine.start(ports[i], logs[i])

    time.sleep(1)

    for i, machine in enumerate(machines):
      ports_copy = copy.deepcopy(ports)
      ports_copy.pop(i)
      machines[i].add_nonint_connections(['localhost' for j in range(len(machines) - 1)], ports_copy)

    time.sleep(num_second_execution)

    for m in machines:
      m.kill_flag.set()

    log_values = []
    for logfile in logs:
      with open(logfile) as f:
        log_values.append(f.read())
    return log_values

  def find_max_queue_by_machine(self, logfiles):
    out = []
    for logfile in logfiles:
      max_found = 0
      for row in logfile.split('\n'):
        print(row)
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

  def test_creates_logs(self):
    logs = self.run_simulation([1, 1, 1])
    self.assertGreater(min([len(log) for log in logs]), 0)

  def test_111(self):
    logs = self.run_simulation([1, 1, 1])
    max_queues = self.find_max_queue_by_machine(logs)
    self.assertLessEqual(max(max_queues), 2)

  def test_333(self):
    logs = self.run_simulation([3, 3, 3])
    max_queues = self.find_max_queue_by_machine(logs)
    self.assertLessEqual(max(max_queues), 2)

  def test_116(self):
    logs = self.run_simulation([1, 1, 6])
    max_queues = self.find_max_queue_by_machine(logs)
    print(max_queues)
    self.assertGreaterEqual(max(max_queues), 5)

if __name__ == '__main__':
  unittest.main(buffer=False)
