##################################################
## Relative Move
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
print ("Application Message: MachineMotion Axis 1 Configured \n")

# Configuring the travel speed to 10000 mm / min
mm.emitSpeed(10000)
print ("Application Message: Speed configured \n")

# Configuring the travel speed to 250 mm / second^2
mm.emitAcceleration(250)
print ("Application Message: Acceleration configured \n")

# Homing axis 1
mm.emitHome(1)
print ("Application Message: Axis 1 is going home \n")
mm.waitForMotionCompletion()
print ("Application Message: Axis 1 at home \n")

# Move the axis one to position 100 mm
mm.emitRelativeMove(1, "positive", 100)
print ("Application Message: Move on-going ... \n")

mm.waitForMotionCompletion()
print ("Application Message: Motion completed \n")

print ("Application Message: Program terminating ... \n")
time.sleep(1)
sys.exit(0)


