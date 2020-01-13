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

# Configuring the travel speed to 10 000 mm / min
machine_motion_example.emitSpeed(10000)

# Configuring the travel speed to 1000 mm / second^2
machine_motion_example.emitAcceleration(1000)

# Homing axis one
machine_motion_example.emitgCode("M92 X10")
#machine_motion_example.emitgCode("V2 X500")
machine_motion_example.emitHome(1)
machine_motion_example.waitForMotionCompletion()

# Use the G0 command to move both axis one and two by 500mm at a travel speed of 10 000 mm / minute
machine_motion_example.emitgCode("G0 X50 Y50 F10000")
machine_motion_example.waitForMotionCompletion()

print ( "--> Example completed." )
