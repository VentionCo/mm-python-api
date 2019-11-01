#!/usr/bin/python
from _MachineMotion import *

# Define a callback to process controller gCode responses (if desired)
def templateCallback(data):
   print ( "Controller gCode responses " + data )

machine_motion_example = MachineMotion(templateCallback, DEFAULT_IP_ADDRESS.usb_windows)

# Homing axis one
machine_motion_example.emitHome(1)
# Wait for the message to be acknowledged by the motion controller
while machine_motion_example.isReady() != "true": pass

print ( "--> This line executes after the motion controller has acknowledged the reception of the command." )
