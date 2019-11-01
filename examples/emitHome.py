##################################################
## Home Individual Axis
##################################################
## Author: Francois Giguere
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

# Configure the axis number 1, 8 uSteps and 150 mm / turn for a timing belt
mm.configAxis(1, MICRO_STEPS.ustep_8, MECH_GAIN.timing_belt_150mm_turn)
print ("Application Message: Axis 1 configured \n")

# Homing axis 1
mm.emitHome(1)
print ("Application Message: Axis 1 is going home\n")
mm.waitForMotionCompletion()
print("Application Message: Axis 1 is at home \n")

print ("Application Message: Program terminating ... \n")
time.sleep(1)
sys.exit(0)
