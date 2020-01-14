import sys
sys.path.append("..")
from MachineMotion import *

# Define a callback to process controller gCode responses (if desired)
def templateCallback(data):
   print ( "Controller gCode responses " + data )

mm = MachineMotion(DEFAULT_IP_ADDRESS.usb_windows, gCodeCallback = templateCallback)

# Home All Axes Sequentially
mm.emitHomeAll()
print ("All Axes Moving Home")
mm.waitForMotionCompletion()
print("All Axes Homed")
