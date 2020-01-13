import sys
sys.path.append("..")
from _MachineMotion import *

# Define a callback to process controller gCode responses (if desired)
def templateCallback(data):
   print ( "Controller gCode responses " + data )

mm = MachineMotion(DEFAULT_IP_ADDRESS.usb_windows, gCodeCallback = templateCallback)

mm.emitHome(1)

# Move the axis one to position 100 mm
mm.emitAbsoluteMove(1, 100)
print("This message gets printed immediately")
mm.waitForMotionCompletion()
print("This message gets printed once machine is finished moving")
