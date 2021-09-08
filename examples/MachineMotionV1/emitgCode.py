import sys
sys.path.append("../..")
from MachineMotion import *

### This Python example showcases how to emit custom gcode with MachineMotion v1. ###

# Define a callback to process controller gCode responses (if desired)
def templateCallback(data):
   print ( "Controller gCode responses " + data )

mm = MachineMotion(DEFAULT_IP, gCodeCallback = templateCallback)

#When starting a program, one must remove the software stop before moving
print("--> Removing software stop")
mm.releaseEstop()
print("--> Resetting system")
mm.resetSystem()

# Use the G2 to perform combined arc move on the first 2 axes
gCodeCommand = "G2 I10 J10"
reply = mm.emitgCode(gCodeCommand)
mm.waitForMotionCompletion()
print("G-code command '" + gCodeCommand + "' completed by MachineMotion.")
print("Reply is : " + reply)
