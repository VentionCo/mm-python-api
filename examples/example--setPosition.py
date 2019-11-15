##################################################
## Set Position
##################################################
## Author: Francois Giguere
## Version: 1.6.8
## Email: info@vention.cc
## Status: tested
##################################################

enableDebug = False

from _MachineMotion_1_6_8 import *

# Define a callback to process controller gCode responses if desired. This is mostly used for debugging purposes.
def debug(data):
    if(enableDebug): print("Debug Message: " + data + "\n")

print ("Application Message: MachineMotion Program Starting \n")

mm = MachineMotion(debug, DEFAULT_IP_ADDRESS.usb_windows)
print ("Application Message: MachineMotion Controller Connected \n")

# Configure the axis number 1, 8 uSteps and 150 mm / turn for a timing belt
mm.configAxis(1, MICRO_STEPS.ustep_8, MECH_GAIN.timing_belt_150mm_turn)
print ("Application Message: MachineMotion axis 1 configured \n")

# Override the current position of the machine motion controller with a new value - without moving the axis.
mm.setPosition(1, 100)
print ("Application Message: Position set to 100 mm on axis 1\n")

mm.emitRelativeMove(1, "negative", 50)
print ("Application Message: Moving in the negative direction ... \n")

mm.waitForMotionCompletion()
print ("Application Message: Motion completed \n")

print ("Application Message: Program terminating ... \n")
time.sleep(1)
sys.exit(0)