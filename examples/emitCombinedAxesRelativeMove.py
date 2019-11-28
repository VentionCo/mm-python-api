from _MachineMotion import *

# Define a callback to process controller gCode responses if desired. This is mostly used for debugging purposes.
enableDebug = False
def debug(data):
    if(enableDebug): print("Debug Message: " + data)

#declare parameters for combine move
speed = 500
acceleration = 500
axesToMove = [1,2,3]
distances = [50, 100, 50]
directions = ["positive","negative","postive"]
mechGain = MECH_GAIN.timing_belt_150mm_turn

#load parameters for combined move
mm = MachineMotion(debug, DEFAULT_IP_ADDRESS.usb_windows)
mm.emitSpeed(speed)
mm.emitAcceleration(acceleration)
for axis in axesToMove:
    mm.configAxis(axis, MICRO_STEPS.ustep_8, mechGain)
mm.emitHomeAll()
print("All Axes homed.")

# Simultaneously moves three axis:
#   Move axis 1 in the positive direction by 50 mm
#   Move axis 2 in the negative direction by 100 mm
#   Move axis 3 in the positive direction by 50 mm
mm.emitCombinedAxisRelativeMove(axesToMove, directions, distances)

mm.waitForMotionCompletion()
for axis in len(axesToMove):
    print("Axis " + str(axis) + " moved " + distances[axis] + " in the " + directions[axis] " direction.")

