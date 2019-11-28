from _MachineMotion import *

# Define a callback to process controller gCode responses if desired. This is mostly used for debugging purposes.
enableDebug = False
def debug(data):
    if(enableDebug): print("Debug Message: " + data)
mm = MachineMotion(debug, DEFAULT_IP_ADDRESS.usb_windows)

# Homing axis 1
mm.emitHome(1)
print ("Application Message: Axis 1 is going home\n")
mm.waitForMotionCompletion()
print("Application Message: Axis 1 is at home \n")

