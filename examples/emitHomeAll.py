
from _MachineMotion import *

# Define a callback to process controller gCode responses if desired. This is mostly used for debugging purposes.
enableDebug = False
def debug(data):
    if(enableDebug): print("Debug Message: " + data)
mm = MachineMotion(debug, DEFAULT_IP_ADDRESS.usb_windows)

# Home All Axes Sequentially
mm.emitHomeAll()
print ("All Axes Moving Home")
mm.waitForMotionCompletion()
print("All Axes Homed")