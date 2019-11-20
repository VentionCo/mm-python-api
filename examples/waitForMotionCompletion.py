##################################################
## Wait for Motion Completion Example
##################################################
## Version: 1.6.8
## Email: info@vention.cc
## Status: tested
##################################################

from _MachineMotion_1_6_8 import *

# Define a callback to process controller gCode responses if desired. This is mostly used for debugging purposes.
def debug(data):
    pass
    
print ("Application Message: MachineMotion Program Starting \n")

mm = MachineMotion(debug, DEFAULT_IP_ADDRESS.usb_windows)
print ("Application Message: MachineMotion Controller Connected \n")

# Homing axis one
mm.emitHome(1)
print ("Application Message: Axis 1 is at home \n")

# Move the axis one to position 100 mm
mm.emitAbsoluteMove(1, 100)
print ("Application Message: Motion on-going ... \n")

# This function call waits for the motion to be completed before returning
mm.waitForMotionCompletion()
print ("Application Message: Motion has completed \n")

print ("Application Message: Program terminating \n")
time.sleep(1)
sys.exit(0)


