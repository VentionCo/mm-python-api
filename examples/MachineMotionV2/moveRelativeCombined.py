import sys
sys.path.append("../..")
from MachineMotion import *

### This Python example showcases combined relative moves with MachineMotion v1. ###

mm = MachineMotionV2()

# When starting a program, one must remove the software stop before moving
print("--> Removing software stop")
mm.releaseEstop()
print("--> Resetting system")
mm.resetSystem()

# Configure actuators
axesToMove = [1,2,3]
for axis in axesToMove:
    mm.configServo(axis, MECH_GAIN.timing_belt_150mm_turn, DIRECTION.NORMAL, 10.0, motorSize=MOTOR_SIZE.LARGE)

# Simultaneously moves three axis:
#   Move axis 1 in the positive direction by 50 mm
#   Move axis 2 in the negative direction by 100 mm
#   Move axis 3 in the positive direction by 50 mm
distances = [50, 100, 50]
mm.moveRelativeCombined(axesToMove, distances)
mm.waitForMotionCompletion()
for index, axis in enumerate(axesToMove):
    print("Axis " + str(axis) + " moved " + str(distances[index]) + "mm")
