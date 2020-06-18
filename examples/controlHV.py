import sys
sys.path.append("ad5761")
import glob
import os
import json
import struct
import time
import threading
import Queue
import readline
import numpy as np
import math
import rlcompleter
from ad5761 import ad5761


def get_key_value(keys, flag, default = "0"):
  index = 1
  while True:
    if index >= len(keys) - 1:
      return default
    if keys[index] == ("-" + flag):
      return keys[index+1]
    index += 1

def get_message_value(keys, flag):
  index = 1
  while True:
    if index >= len(keys) - 1:
      return ""
    if keys[index] == ("-" + flag):
      return " ".join(keys[index+1:]).split('"')[1]
    index += 1


if "libedit" in readline.__doc__:
    readline.parse_and_bind("bind ^I rl_complete")

cmds = ['help','start', 'reset', 'setvoltage']

def completer(text, state):
    options = [x for x in cmds if x.startswith(text)]
    try:
        return options[state]
    except IndexError:
        return None

HISTORY_FILENAME = 'mu2e_roc.hist'

if os.path.exists(HISTORY_FILENAME):
    print 'reading'
    readline.read_history_file(HISTORY_FILENAME)


readline.set_completer(completer)        
readline.parse_and_bind("tab: complete")
        
print "Waiting for ARM to connect"
print "=========================="

output_queue = Queue.Queue()

interrupted = threading.Lock()
interrupted.acquire()



l = ad5761.ad5761(0, 0)
l._max_speed_hz = 100000
l.open()
    
def process_command(line):

  keys = line.split(" ")
  try:
    if keys[0] == "start":
        l._ad5761_write_cr()
        l._ad5761_read_cr()
        l._print()


    elif keys[0] == "help":
        print("start: Open comm wit the DAC")
        print("reset: Issue a hard reset")
        print ("setvoltage -v voltage(in Volts)") 
        
    elif keys[0] == "reset":
        l._ad5761_hard_reset()
        l._print()
        
    elif keys[0] == "setvoltage":
        fvalue = float(get_key_value(keys,"v",-1))
        dacdata = int(fvalue*65536./5.0)
        l._ad5761_write_dac(dacdata)
        l._ad5761_read_dac()


    elif keys[0] == "rampto":
        vvalue = float(get_key_value(keys,"v",-1))
        tvalue = float(get_key_value(keys,"t",-1))

        l._ad5761_read_dac()
        currentdacval = l._rawdata[1] << 8 | l._rawdata[2]
        todacvalue = int(fvalue*65536./5.0)
        

 
    else:
      print "Unknown command"
  except (ValueError, struct.error), e:
    print "Bad Input:",e



# keyboard input loop
try:
  while True:
    line = raw_input()
    if line:
      process_command(line)
except KeyboardInterrupt:
  interrupted.release()
except Exception, e:
  print type(e),e
  interrupted.release()
finally:
  print 'Ending...'
  readline.write_history_file(HISTORY_FILENAME)    
