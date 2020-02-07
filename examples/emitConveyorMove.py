#!/usr/bin/python

# System imports
import sys
# Custom imports
sys.path.append("..")

import time

from MachineMotion import *

# Create MachineMotion instance
mm = MachineMotion("192.168.7.2", None)

#When starting a program, one must remove the software stop before moving
print("--> Removing software stop")
mm.releaseEstop()
print("--> Resetting system")
mm.resetSystem()

mechGain = MECH_GAIN.roller_conveyor_mm_turn
CONVEYOR_AXIS = int(input("Input conveyor axis : "))

if CONVEYOR_AXIS < 0 or CONVEYOR_AXIS > 3:
  print("Conveyor axis number undefined..exit")
  exit(1)

mm.configAxis(CONVEYOR_AXIS, MICRO_STEPS.ustep_8, mechGain)

print("Start Conveyor Move...")
print("Continuous move: speed 100mm/s & acceleration 100mm/s^2")
mm.startContinuousMove(CONVEYOR_AXIS,100,100)
time.sleep(5)
mm.stopContinuousMove(CONVEYOR_AXIS)
time.sleep(2)

print("Continuous move: speed 500mm/s & acceleration 500mm/s^2")
mm.startContinuousMove(CONVEYOR_AXIS, 500, 500)
time.sleep(5)
mm.stopContinuousMove(CONVEYOR_AXIS)
time.sleep(2)

print("Continuous move: speed 1000mm/s & acceleration 1000mm/s^2")
mm.startContinuousMove(CONVEYOR_AXIS, 1000, 1000)
time.sleep(5)

print("Stop Conveyor Move...")
mm.stopContinuousMove(CONVEYOR_AXIS)
time.sleep(5)
print("--> Example completed")
