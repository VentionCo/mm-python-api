import sys
sys.path.append("..")
from MachineMotion import *

#declare parameters for combine move
speed = 500
acceleration = 500
axesToMove = [1,2]
distances = [50, 100, 50]
directions = ["positive","positive","positive"]
mechGain = MECH_GAIN.timing_belt_150mm_turn

# Define a callback to process controller gCode responses (if desired)
def templateCallback(data):
   print ( "Controller gCode responses " + data )

mm = MachineMotion(DEFAULT_IP_ADDRESS.usb_windows, gCodeCallback = templateCallback)

mm.emitSpeed(speed)
mm.emitAcceleration(acceleration)
for axis in axesToMove:
    mm.configAxis(axis, MICRO_STEPS.ustep_8, mechGain)
mm.emitHomeAll()
mm.waitForMotionCompletion()
print("All Axes homed.")

# Simultaneously moves three axis:
#   Move axis 1 in the positive direction by 50 mm
#   Move axis 2 in the negative direction by 100 mm
#   Move axis 3 in the positive direction by 50 mm
mm.emitCombinedAxisRelativeMove(axesToMove, directions, distances)


mm.waitForMotionCompletion()
for index, axis in enumerate(axesToMove):
    print("Axis " + str(axis) + " moved " + str(distances[index]) + " in the " + directions[index] + " direction.")
