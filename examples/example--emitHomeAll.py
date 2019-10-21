##################################################
## Home All Axes
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

# Configure the axis number 2, 8 uSteps and 150 mm / turn for a timing belt
mm.configAxis(2, MICRO_STEPS.ustep_8, MECH_GAIN.timing_belt_150mm_turn)
print ("Application Message: Axis 2 configured \n")

# Configure the axis number 3, 8 uSteps and 150 mm / turn for a timing belt
mm.configAxis(3, MICRO_STEPS.ustep_8, MECH_GAIN.timing_belt_150mm_turn)
print ("Application Message: Axis 3 configured \n")

# Homing all the axes of the controller sequentially
mm.emitHomeAll()
print ("Application Message: Axes are going home\n")
mm.waitForMotionCompletion()
print("Application Message: Axes are home\n")

print ("Application Message: Program terminating ... \n")
time.sleep(1)
sys.exit(0)
