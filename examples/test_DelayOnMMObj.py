# System imports
import sys
import random
import time

# Custom imports
sys.path.append("..")

from MachineMotion import *

device = 2
state = 0
value = 0
pin = 0

# Define a callback to process controller gCode responses (if desired)
def templateCallback(data):
   print ( "Controller gCode responses " + data )

machine_motion_example = MachineMotion(templateCallback, "192.168.7.2")

if ( machine_motion_example.isIoExpanderAvailable(device) == False ):
  print ( "IO Exapnder "+str(device)+" is not available!!! Please verify connection.")
else:
  print ( "Connected!!" )
  
print (" I got this far -- 1" )


if ( machine_motion_example.isIoExpanderAvailable(device) == False ):
  print ( "IO Exapnder "+str(device)+" is not available!!! Please verify connection.")
else:
  print ( "Connected!!" )
  
print (" I got this far -- 2" )

time.sleep(1)

if ( machine_motion_example.isIoExpanderAvailable(device) == False ):
  print ( "IO Exapnder "+str(device)+" is not available!!! Please verify connection.")
else:
  print ( "Connected!!" )
  
print (" I got this far -- 3" )