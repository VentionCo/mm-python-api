import sys
sys.path.append("../..")
from MachineMotion import *

### This Python example showcases relative moves with MachineMotion v1. ###

mm = MachineMotion()

# When starting a program, one must remove the software stop before moving
print("--> Removing software stop")
mm.releaseEstop()
print("--> Resetting system")
mm.resetSystem()

# Configure the actuator
axis = 1
mm.configAxis(axis, MICRO_STEPS.ustep_8, MECH_GAIN.rack_pinion_mm_turn)

# Begin Relative Move
distance = 100 # in mm
direction = DIRECTION.POSITIVE
mm.emitRelativeMove(axis, direction, distance)
mm.waitForMotionCompletion()
print("Axis " + str(axis) + " moved " + str(distance) + "mm in the " + direction + " direction.")
