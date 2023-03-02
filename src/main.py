import sys
import argparse
from machine import *

parser = argparse.ArgumentParser()
parser.add_argument('--port', type=int)
parser.add_argument('--out', type=str)
args = parser.parse_args()

if args.port == None:
  print('Please specify a port.')
else:
  run_machine = Machine()
  run_machine.start(args.port, args.out)
