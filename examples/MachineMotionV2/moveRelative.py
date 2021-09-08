import sys
sys.path.append("../..")
from MachineMotion import *

### This Python example showcases relative moves with MachineMotion v2. ###

mm = MachineMotionV2()

# When starting a program, one must remove the software stop before moving
print("--> Removing software stop")
mm.releaseEstop()
print("--> Resetting system")
mm.resetSystem()

# Configure the actuator
axis = 1
mm.configServo(axis, MECH_GAIN.timing_belt_150mm_turn, DIRECTION.NORMAL, 5.0)

# Begin Relative Move
distance = 100 # in mm
mm.moveRelative(axis, distance)
mm.waitForMotionCompletion()
print("--> Axis " + str(axis) + " moved " + str(distance) + "mm")

# Pass a negative distance value to move in the opposite direction
distance = -100 # in mm
mm.moveRelative(axis, distance)
mm.waitForMotionCompletion()
print("--> Axis " + str(axis) + " moved " + str(distance) + "mm")

print("--> Example Complete")
