import sys
sys.path.append("..")
from MachineMotion import *

# Define a callback to process controller gCode responses (if desired)
def templateCallback(data):
   print ( "Controller gCode responses " + data )

mm = MachineMotion(DEFAULT_IP_ADDRESS.usb_windows, gCodeCallback = templateCallback)

#When starting a program, one must remove the software stop before moving
print("--> Removing software stop")
mm.releaseEstop()
print("--> Resetting system")
mm.resetSystem()

#Define Move Parameters
axis = 1
speed = 400
acceleration = 500
direction = "positive"
mechGain = MECH_GAIN.roller_conveyor_mm_turn

#Load Relative Move Parameters
mm.emitSpeed(speed)
mm.emitAcceleration(acceleration)
mm.configAxis(axis, MICRO_STEPS.ustep_8, mechGain)

#Home Axis Before Move
print("Axis " + str(axis) + " moving home.")
mm.emitHome(axis)
mm.waitForMotionCompletion()
print("Axis " + str(axis) + " homed")

#Move 50mm and check position
mm.emitRelativeMove(axis, direction, 50)
mm.getCurrentPositions()
time.sleep(10.0)

#Move 100mm and check position
mm.emitRelativeMove(axis, direction, 50)
mm.getCurrentPositions()
time.sleep(10.0)

mm.emitHomeAll()
mm.waitForMotionCompletion()
print("End of example")