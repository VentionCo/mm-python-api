#!/usr/bin/python

# System imports
import sys
# Custom imports
sys.path.append("..")

from MachineMotion import *

# Define a callback to process controller gCode responses (if desired)
def templateCallback(data):
   print ( "Controller gCode responses " + data )

machine_motion_example = MachineMotion(templateCallback, DEFAULT_IP_ADDRESS.usb_windows)

#When starting a program, one must remove the software stop before moving
print("--> Removing software stop")
machine_motion_example.releaseEstop()
print("--> Resetting system")
machine_motion_example.resetSystem()

# Homing all the axes of the controller sequentially
machine_motion_example.emitHomeAll()

print ( "--> All Axes are now at home position." )
