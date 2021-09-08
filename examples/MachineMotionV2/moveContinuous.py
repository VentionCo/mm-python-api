#!/usr/bin/python
import sys, time
sys.path.append("../..")
from MachineMotion import *

### This Python example showcases continuous moves with MachineMotion v2. ###

### MachineMotion CONFIGURATION ###

# Create MachineMotion instance
mm = MachineMotionV2()

# When starting a program, one must remove the software stop before moving
print("--> Removing software stop")
mm.releaseEstop()
print("--> Resetting system")
mm.resetSystem()

# Configure actuator
conveyor_axis = 1
mm.configServo(conveyor_axis, MECH_GAIN.roller_conveyor_mm_turn, DIRECTION.NORMAL, 5.0)

### CONTINUOUS MOVES ###

# Start the continuous move
print("Start Conveyor Move...")
print("Continuous move: speed 100mm/s & acceleration 50mm/s^2")
mm.moveContinuous(conveyor_axis, 100, 50)
time.sleep(5)

# Change speed while moving 
print("Continuous move: speed 500mm/s & acceleration 250mm/s^2")
mm.moveContinuous(conveyor_axis, 500, 250)
time.sleep(5)

# Reverse direction of conveyor by changing the sign of the speed
print("Reverse continuous move: speed -1000mm/s & acceleration 500mm/s^2")
mm.moveContinuous(conveyor_axis, -1000, 500)
time.sleep(5)

# Stop the continuous move
print("Stop Conveyor Move...")
mm.stopMoveContinuous(conveyor_axis, 500)
time.sleep(3)
print("--> Example completed")
