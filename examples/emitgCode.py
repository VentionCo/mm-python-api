import sys
sys.path.append("..")
from MachineMotion import *

#Declare parameters for g-Code command
speed = 500
acceleration = 500
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

mm.emitSpeed(speed)
mm.emitAcceleration(acceleration)
mm.emitHomeAll()
print("All Axes homed.")

# Use the G0 command to move both axis 1 and 2 by 50mm
gCodeCommand = "G0 X50 Y50"
mm.emitgCode(gCodeCommand)
mm.waitForMotionCompletion()
print("G-code command '" + gCodeCommand + "' completed by MachineMotion.")
