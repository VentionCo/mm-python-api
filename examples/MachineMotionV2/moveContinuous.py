#!/usr/bin/python
import sys, time
sys.path.append("../..")
from MachineMotion import *

### This Python example showcases continuous moves with MachineMotion v2. ###

# Create MachineMotion instance
mm = MachineMotionV2()

# When starting a program, one must remove the software stop before moving
print("--> Removing software stop")
mm.releaseEstop()
print("--> Resetting system")
mm.resetSystem()

# Configure actuator
conveyor_axis = 1
mm.configServo(conveyor_axis, MECH_GAIN.roller_conveyor_mm_turn, DIRECTION.NORMAL, 10.0, motorSize=MOTOR_SIZE.LARGE)

# Note: on MachineMotion software version 2.4.0 and newer, continuous moves are limited by the axis max speed and acceleration.
# Please see the section below for more details.

### CONTINUOUS MOVES ###
# Start the continuous move
print("Start Conveyor Move...")
print("Continuous move: speed 100mm/s & acceleration 100mm/s^2")
mm.moveContinuous(conveyor_axis, 100, 100)
time.sleep(5)

# Change speed while moving 
print("Continuous move: speed 500mm/s & acceleration 250mm/s^2")
mm.moveContinuous(conveyor_axis, 500, 250)
time.sleep(5)

# Reverse direction of conveyor by changing the sign of the speed
print("Reverse continuous move: speed -1000mm/s & acceleration 500mm/s^2")
mm.moveContinuous(conveyor_axis, -1000, 500)
time.sleep(5)

# Or pass in the optional direction argument
print("Reverse continuous move: speed -500mm/s & acceleration 500mm/s^2")
mm.moveContinuous(conveyor_axis, 500, 500, direction=DIRECTION.NEGATIVE)
time.sleep(5)

# Stop the continuous move
print("Stop Conveyor Move: acceleration 500mm/s^2")
mm.stopMoveContinuous(conveyor_axis, 500)
time.sleep(3)

# # For MachineMotion Software version >= 2.4.0 only:

# # Setting the axis max speed and acceleration will limit continuous moves:
# mm.setAxisMaxSpeed(conveyor_axis, 1000)
# mm.setAxisMaxAcceleration(conveyor_axis, 1000)

# # Start the continuous move at max speed and acceleration
# mm.moveContinuous(conveyor_axis)
# time.sleep(5)

# # Slow down conveyor
# mm.setAxisMaxSpeed(conveyor_axis, 500)
# time.sleep(5)

# # Reverse direction of conveyor
# mm.moveContinuous(conveyor_axis, direction=DIRECTION.NEGATIVE)
# time.sleep(5)

# # Stop the continuous move
# mm.stopMoveContinuous(conveyor_axis)
# time.sleep(5)

print("--> Example completed")
