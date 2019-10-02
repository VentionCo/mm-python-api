#!/usr/bin/python
from _MachineMotion import *

# Define a callback to process controller gCode responses (if desired)
def templateCallback(data):
   print ( "Controller gCode responses " + data )

machine_motion_example = MachineMotion(templateCallback, DEFAULT_IP_ADDRESS.usb_windows)

# Send a stop command to the Machine (even if it is not moving yet !)

for i in range(0, 50):
   machine_motion_example.emitStop()
   machine_motion_example.emitRelativeMove(1, "positive", 10)

print ( "--> Machine Stopped" )
