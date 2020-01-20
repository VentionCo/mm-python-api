import sys
sys.path.append("..")
from MachineMotion import *

#Declare parameters for g-Code command
speed = 1000
acceleration = 2000
mechGain = MECH_GAIN.timing_belt_150mm_turn

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

mm.emitSpeed(speed)
mm.emitAcceleration(acceleration)
mm.emitHome(axis)
mm.configAxis(AXIS_NUMBER.DRIVE1, MICRO_STEPS.ustep_8, mechGain)
# Moves axis back and forth, waiting a specified amount of time between each move
mm.emitAbsoluteMove(axis, 100)
mm.emitDwell(250)
mm.emitAbsoluteMove(axis, 50)
mm.emitDwell(500)
mm.emitAbsoluteMove(axis, 100)
mm.emitDwell(1000)
mm.emitAbsoluteMove(axis, 50)
mm.emitDwell(5000)
print("emitDwell does not block this line from printing")
mm.waitForMotionCompletion()
print("but waitForMotionCompletion() will force python to wait the full 5000ms until emitDwell has finished.")
