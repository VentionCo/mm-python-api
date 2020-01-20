import sys
sys.path.append("..")
from MachineMotion import *

import time

# Define a callback to process controller gCode responses (if desired)
def templateCallback(data):
   print ( "Controller gCode responses " + data )

mm = MachineMotion(DEFAULT_IP_ADDRESS.usb_windows, gCodeCallback = templateCallback)

#When starting a program, one must remove the software stop before moving
print("--> Removing software stop")
mm.releaseEstop()
print("--> Resetting system")
mm.resetSystem()

#Define Relative Move Parameters
axis = 1
speed = 400
acceleration = 500
distance = 1000
direction = "positive"
mechGain = MECH_GAIN.rack_pinion_mm_turn

#Load Relative Move Parameters
mm.emitSpeed(speed)
mm.emitAcceleration(acceleration)
mm.configAxis(axis, MICRO_STEPS.ustep_8, mechGain)

#Home Axis Before Move
mm.emitHome(axis)
print("Axis " + str(axis) + " is going home")
mm.waitForMotionCompletion()
print("Axis " + str(axis) + " homed")

#Begin Relative Move
mm.emitRelativeMove(axis, direction, distance)
print("Axis " + str(axis) + " is moving " + str(distance) + "mm in the " + direction + " direction")

#This move should take 5 (distance/speed) seconds to complete. Instead, we wait 2 seconds and then stop the machine.
time.sleep(2)
mm.emitStop()
print("Axis " + str(axis) + " stopped.")
