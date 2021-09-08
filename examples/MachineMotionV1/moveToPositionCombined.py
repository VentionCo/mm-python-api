import sys
sys.path.append("../..")
from MachineMotion import *

### This Python example showcases combined absolute moves with MachineMotion v1. ###

mm = MachineMotion()

# When starting a program, one must remove the software stop before moving
print("--> Removing software stop")
mm.releaseEstop()
print("--> Resetting system")
mm.resetSystem()

# Configure actuators
axesToMove = [1,2,3]
for axis in axesToMove:
    mm.configAxis(axis, MICRO_STEPS.ustep_8, MECH_GAIN.timing_belt_150mm_turn)

### HOMING ###

# Home actuators before performing absolute moves
print("All Axes Moving Home Sequentially")
mm.moveToHomeAll()
print("All Axes homed.")

### SIMULTANEOUS ABSOLUTE MOVES OF THREE AXES ###

#   Moves axis 1 to absolute position 50mm
#   Moves axis 2 to absolute position 100mm
#   Moves axis 3 to absolute position 50mm
positions = [50, 100, 50]
mm.moveToPositionCombined(axesToMove, positions)
mm.waitForMotionCompletion()
for index, axis in enumerate(axesToMove):
    print("Axis " + str(axis) + " moved to position " + str(positions[index]) + "mm")
