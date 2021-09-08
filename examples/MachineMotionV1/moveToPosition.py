import sys
sys.path.append("../..")
from MachineMotion import *

### This Python example showcases moveToPosition with MachineMotion v1. ###

mm = MachineMotion()

# When starting a program, one must remove the software stop before moving
print("--> Removing software stop")
mm.releaseEstop()
print("--> Resetting system")
mm.resetSystem()

# Axis configuration
axis = 1             #The axis that you'd like to move
mm.configAxis(axis, MICRO_STEPS.ustep_8, MECH_GAIN.timing_belt_150mm_turn)

# Movement configuration
position = 100       #The position to which you'd like to move

# Home Axis before moving to position
print("Axis " + str(axis) + " is going to home.")
mm.moveToHome(axis)
print("Axis " + str(axis) + " homed.")

# Move
mm.moveToPosition(axis, position)
print("Axis " + str(axis) + " is moving towards position " + str(position) + "mm.")
mm.waitForMotionCompletion()
print("Axis " + str(axis) + " is at position " + str(position) + "mm.")
