import os, sys
sys.path.append(os.path.abspath(__file__ + "/../../"))
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

axis = AXIS_NUMBER.DRIVE1

mm.configAxis(axis, MICRO_STEPS.ustep_8, MECH_GAIN.timing_belt_150mm_turn)
mm.emitHome(axis)
print ("Application Message: Axis "+ str(axis) +" is going home")
mm.waitForMotionCompletion()
print("Application Message: Axis "+ str(axis) +" is at home")
