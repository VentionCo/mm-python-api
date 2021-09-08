import sys
sys.path.append("../..")
from MachineMotion import *

### This Python example showcases combined absolute moves with MachineMotion v2. ###

mm = MachineMotionV2()

# When starting a program, one must remove the software stop before moving
print("--> Removing software stop")
mm.releaseEstop()
print("--> Resetting system")
mm.resetSystem()

# Configure actuators
axesToMove = [1,2,3]
for axis in axesToMove:
    mm.configServo(axis, MECH_GAIN.timing_belt_150mm_turn, DIRECTION.NORMAL, 5.0)

# Home actuators before performing absolute moves
print("Axes Moving Home Sequentially")
for axis in axesToMove:
    mm.moveToHome(axis)
    mm.waitForMotionCompletion()
print("Axes homed")

# Simultaneously moves three axis:
#   Moves axis 1 to absolute position 50mm
#   Moves axis 2 to absolute position 100mm
#   Moves axis 3 to absolute position 50mm
positions = [50, 100, 50]
mm.moveToPositionCombined(axesToMove, positions)
mm.waitForMotionCompletion()
for index, axis in enumerate(axesToMove):
    print("Axis " + str(axis) + " moved to position " + str(positions[index]) + "mm")
