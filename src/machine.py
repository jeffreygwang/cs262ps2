import random
import socket
import threading
from sockets import *
import time

INT_SIZE = 4
MAX_CLOCK_RATE = 6

# A machine with a logical clock that sends actions to at most 2 other machines.
class Machine:
  # The number of actions per second, determined randomly at initialization,
  clock_rate = 0

  # The local value of the logical clock for this machine.
  logical_clock = 0

  # The path to the log file for this machine.
  logfile = None

  # Queued logical clock updates received from other machines.
  queue = []

  # A mutex used to lock the `queue` list.
  queue_lock = None

  # A list of sockets that this socket is a client for.
  connected_sockets_as_client = []

  # stop running (non-interactive mode)
  kill_flag = threading.Event()

  # whether or not interactive
  interactive = False

  # Initializes a new `Machine` with a random clock rate.
  def __init__(self, interactive=True):
    self.clock_rate = random.randint(1, MAX_CLOCK_RATE)
    print(f"This machine's random clock rate: {self.clock_rate}")
    self.queue_lock = threading.Lock()
    self.kill_flag.clear()
    self.interactive = interactive

  # Starts the machine's server and begins running the experiment.
  def start(self, port, logfile):
    # Open the logfile.
    self.logfile = logfile
    with open(self.logfile, 'w') as f:
      f.write('Event\tTime\tQueue\tClock\n')

    # Start listening for incoming socket connections.
    threading.Thread(target=self.start_network_thread, args=(port,)).start()

    # Prompt the user to enter other clients.
    if self.interactive:
      threading.Thread(target=self.start_interactive_thread, args=()).start()

    # Start the action cycle.
    threading.Timer(1 / self.clock_rate, self.run_cycle).start()

  # Starts listening for incoming sockets on a given port, and handles
  # messages received from those clients in a new thread.
  def start_network_thread(self, port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('', port))
    server_socket.listen()

    while True:
      s, _ = server_socket.accept()
      threading.Thread(target=self.client_loop, args=(s,)).start()

  # Receives messages from a client on a given socket that this machine is
  # listening on.
  def client_loop(self, s):
    while True:
      # Receive the new clock value, and append to the queue.
      new_clock = receive_sized_int(s, INT_SIZE)
      self.queue_lock.acquire()
      self.queue.append(new_clock)
      self.queue_lock.release()

  # Repeatedly prompts the user to enter a host and port to connect to another
  # machine.
  def start_interactive_thread(self):
    while True:
      new_address = input('Enter a new host to connect to: ')
      s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      new_port = input('The port: ')
      s.connect((new_address, int(new_port)))
      self.connected_sockets_as_client.append(s)
      print(f"Added {new_address}:{new_port}")

  # Add connections in non-interactive mode.
  def add_nonint_connections(self, addresses, ports):
    if len(addresses) != len(ports):
      print("len(addresses) != len(ports.)")
      return

    for i in range(len(addresses)):
      s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      s.connect((addresses[i], int(ports[i])))
      self.connected_sockets_as_client.append(s)
      print(f"Added {addresses[i]}:{ports[i]}")

  # Runs a single cycle of the machine's clock rate.
  def run_cycle(self):
    if self.kill_flag.is_set():
      return

    self.queue_lock.acquire()

    if len(self.queue) > 0:
      # If a message has been received, update the clock accordingly. We only
      # Update if the new clock value (`popped_clock` + 1) would be greater
      # than the old clock value.
      popped_clock = self.queue.pop(0)
      if self.logical_clock <= popped_clock:
        self.logical_clock = popped_clock + 1
        self.log('receive')
    else:
      # Determine a random action to take.
      action = random.randint(1, 10)
      if action == 1 and len(self.connected_sockets_as_client) >= 1:
        # Send the clock value to the first client and increment the
        # logical clock.
        s = self.connected_sockets_as_client[0]
        send_sized_int(s, self.logical_clock, INT_SIZE)
        self.logical_clock += 1
      elif action == 2 and len(self.connected_sockets_as_client) >= 2:
        # Send the clock value to the second connected client and increment the
        # logical clock.
        s = self.connected_sockets_as_client[1]
        send_sized_int(s, self.logical_clock, INT_SIZE)
        self.logical_clock += 1
      elif action == 3:
        # Send the clock value to both connected clients and increment the
        # logical clock.
        for s in self.connected_sockets_as_client:
          send_sized_int(s, self.logical_clock, INT_SIZE)
        self.logical_clock += 1
      else:
        # Increment the locgical clock.
        self.logical_clock += 1

      # Log the send action.
      self.log('send ' + str(action))

    self.queue_lock.release()

    threading.Timer(1 / self.clock_rate, self.run_cycle).start()

  # Writes an event, the current time, the queue size, and the clock value to
  # a log file.
  def log(self, event):
    with open(self.logfile, 'a') as f:
      f.write('{}\t{}\t{}\t{}\n'.format(event, time.time(), len(self.queue), self.logical_clock))
