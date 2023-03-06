import sys

def receive_sized_int(s, size: int) -> int:
  """
  Convert [size] bytes to big-endian int.
  """
  return int.from_bytes(receive_sized(s, size), 'big')

def receive_sized(s, size: int) -> bytes:
  """
  Receive [size] bytes. Turn over to receive_sized_int or received_sized_string for decoding.
  """
  combined = b''

  while True:
    try:
      msg = s.recv(size)
    except: # when sockert closed
      sys.exit(0)

    combined += msg
    if len(combined) >= size:
      return combined

def send_sized_int(s, num: int, size: int) -> None:
  """
  Send an integer [num] of [size] bytes
  """
  s.send(num.to_bytes(size, 'big'))

