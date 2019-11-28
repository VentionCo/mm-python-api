from _MachineMotion import *
import time

# Define a callback to process controller gCode responses if desired. This is mostly used for debugging purposes.
enableDebug = False
def debug(data):
    if(enableDebug): print("Debug Message: " + data)
mm = MachineMotion(debug, DEFAULT_IP_ADDRESS.usb_windows)

#Define Relative Move Parameters
axis = 1
speed = 200
acceleration = 500
distance = 1000
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
print("Axis " + str(axis) + " is moving " + str(distance) + "mm in the " + direction + " direction")

#This move should take 5 (distance/speed) seconds to complete. Instead, we wait 2 seconds and then stop the machine.
time.sleep(2)
mm.emitStop()
