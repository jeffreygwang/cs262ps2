import random
import socket
import threading
from sockets import *
import time

INT_SIZE = 4

class Machine:
  clock_rate = 0
  logical_clock = 0
  logfile = None
  queue = []
  queue_lock = None
  connected_sockets_as_client = []

  def __init__(self):
    self.clock_rate = random.randint(1, 6)
    self.queue_lock = threading.Lock()

  def start(self, port, logfile):
    self.logfile = logfile
    with open(self.logfile, 'w') as f:
      f.write('Event\tTime\tQueue\tClock\n')
    threading.Thread(target=self.start_network_thread, args=(port,)).start()
    threading.Thread(target=self.start_interactive_thread, args=()).start()
    threading.Timer(1 / self.clock_rate, self.run_cycle).start()

  def start_network_thread(self, port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('', port))
    server_socket.listen()

    while True:
      s, _ = server_socket.accept()
      threading.Thread(target=self.client_loop, args=(s,)).start()

  def start_interactive_thread(self):
    while True:
      new_address = input('Enter a new host to connect to: ')
      s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      new_port = input('The port: ')
      s.connect((new_address, int(new_port)))
      self.connected_sockets_as_client.append(s)
      print('Added.')

  def client_loop(self, s):
    while True:
      new_clock = receive_sized_int(s, INT_SIZE)
      self.queue_lock.acquire()
      self.queue.append(new_clock)
      self.queue_lock.release()

  def run_cycle(self):
    self.queue_lock.acquire()

    if len(self.queue) > 0:
      popped_clock = self.queue.pop(0)
      if self.logical_clock <= popped_clock:
        self.logical_clock = popped_clock + 1
        self.log('receive')
    else:
      action = random.randint(1, 10)
      if action == 1 and len(self.connected_sockets_as_client) >= 1:
        s = self.connected_sockets_as_client[0]
        send_sized_int(s, self.logical_clock, INT_SIZE)
        self.logical_clock += 1
      elif action == 2 and len(self.connected_sockets_as_client) >= 2:
        s = self.connected_sockets_as_client[1]
        send_sized_int(s, self.logical_clock, INT_SIZE)
        self.logical_clock += 1
      elif action == 3:
        for s in self.connected_sockets_as_client:
          send_sized_int(s, self.logical_clock, INT_SIZE)
        self.logical_clock += 1
      else:
        self.logical_clock += 1
      self.log('send ' + str(action))

    self.queue_lock.release()

    threading.Timer(1 / self.clock_rate, self.run_cycle).start()

  def log(self, event):
    with open(self.logfile, 'a') as f:
      f.write('{}\t{}\t{}\t{}\n'.format(event, time.time(), len(self.queue), self.logical_clock))
