from _MachineMotion import *

# Define a callback to process controller gCode responses if desired. This is mostly used for debugging purposes.
enableDebug = False
def debug(data):
    if(enableDebug): print("Debug Message: " + data)
mm = MachineMotion(debug, DEFAULT_IP_ADDRESS.usb_windows)

#Define Relative Move Parameters
axis = 1
speed = 400
acceleration = 500
distance = 100
direction = "positive"
mechGain = MECH_GAIN.rack_pinion_mm_turn

#Load Relative Move Parameters
mm.emitSpeed(speed)
mm.emitAcceleration(acceleration)
mm.configAxis(axis, MICRO_STEPS.ustep_8, mechGain)

#Home Axis Before Move
mm.emitHome(axis)
mm.waitForMotionCompletion()
print("Axis " + str(axis) + " homed")

#Begin Relative Move
mm.emitRelativeMove(axis, direction, distance)
mm.waitForMotionCompletion()
print("Axis " + str(axis) + " moved " + str(distance) + "mm in the " + direction + " direction")
