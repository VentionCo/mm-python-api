import sys
sys.path.append("../..")
from MachineMotion import *

### This Python example showcases moveToPosition with MachineMotion v2. ###

mm = MachineMotionV2()

# When starting a program, one must remove the software stop before moving
print("--> Removing software stop")
mm.releaseEstop()
print("--> Resetting system")
mm.resetSystem()

# Axis configuration
axis = 1             #The axis that you'd like to move
mm.configServo(axis, MECH_GAIN.timing_belt_150mm_turn, DIRECTION.NORMAL, 5.0)

# Movement configuration
position = 100       # The absolute position to which you'd like to move

# Home Axis before move to position
print("Axis " + str(axis) + " is going home.")
mm.moveToHome(axis)
mm.waitForMotionCompletion()
print("Axis " + str(axis) + " homed.")

# Move
mm.moveToPosition(axis, position)
print("Axis " + str(axis) + " is moving towards position " + str(position) + "mm")
mm.waitForMotionCompletion()
print("Axis " + str(axis) + " is at position " + str(position) + "mm")
