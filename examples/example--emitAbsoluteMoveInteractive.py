##################################################
## Absolute Move Interactive
##################################################
## Author: Jack Dundas
## Version: 1.6.8
## Email: info@vention.cc
## Status: tested
##################################################

enableDebug = False

from _MachineMotion_1_6_8 import *
import configWizard

# Define a callback to process controller gCode responses if desired. This is mostly used for debugging purposes.
def debug(data):
    if(enableDebug): print("Debug Message: " + data + "\n")

print ("Application Message: MachineMotion Program Starting \n")

mm = MachineMotion(debug, DEFAULT_IP_ADDRESS.usb_windows)
print ("Application Message: MachineMotion Controller Connected \n")

# Configure the axis number 1, 8 uSteps and 150 mm / turn for a timing belt
mm.configAxis(1, MICRO_STEPS.ustep_8, MECH_GAIN.timing_belt_150mm_turn)
print ("Application Message: MachineMotion Axis 1 Configured \n")


cw = configWizard.configWizard()

# Configuring the travel speed to 10000 mm / min
speed = cw.askNumeric("Please enter a travel speed")
mm.emitSpeed(speed)
cw.write("Speed Configured")

# Configuring the travel speed to 250 mm / second^2
accel = cw.askNumeric("Please enter a travel acceleration")
mm.emitAcceleration(250)
cw.write("Application Message: Acceleration configured")

# Homing axis 1
mm.emitHome(1)
cw.write("Application Message: Axis 1 going home")
mm.waitForMotionCompletion()
cw.write("Application Message: Axis 1 is at home")


while True:
    # Move the axis 1 to position 100 mm
    distanceToMove = cw.askNumeric("Please enter the absolute position you'd like to move to [mm]:")
    if distanceToMove is not None:
        mm.emitAbsoluteMove(1, distanceToMove)
        cw.write("Application Message: Motion on-going ...")

        mm.waitForMotionCompletion()
        cw.write("Application Message: Motion completed")
    else:
        cw.quit()
        break




print ("Application Message: Program terminating ... \n")
time.sleep(1)
sys.exit(0)
