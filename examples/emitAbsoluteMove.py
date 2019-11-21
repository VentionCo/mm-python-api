##################################################
## Absolute Move
##################################################
## Version: 2.2
## Email: info@vention.cc
## Status: tested
##################################################

import os, sys
import configWizard
#Adds mm-python-api to the sys path so that we can access MachineMotion.py 
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parentdir)
from _MachineMotion import *

enableDebug = False

# Define a callback to process controller gCode responses if desired. This is mostly used for debugging purposes.
def debug(data):
    if(enableDebug): print("Debug Message: " + data + "\n")
    
print ("Application Message: MachineMotion Program Starting \n")

mm = MachineMotion(debug, DEFAULT_IP_ADDRESS.usb_windows)
print ("Application Message: MachineMotion Controller Connected \n")

try:
    cw = configWizard.configWizard()
    axis = cw.askForSingleAxis()
    mechGain = cw.askForMechGain(axis)
    # Configure the axis number 1, 8 uSteps and 150 mm / turn for a timing belt
    mm.configAxis(axis, MICRO_STEPS.ustep_8, mechGain)
    cw.write("MachineMotion Axis" + str(axis) + " Configured")

    speed, acceleration = cw.askForSpeedAndAcceleration()

    mm.emitSpeed(speed)
    cw.write("Global speed configured to " + str(speed) + " mm/s")

    mm.emitAcceleration(acceleration)
    cw.write("Global acceleration configured to " + str(acceleration) + " mm/s^2")

    # Homing axis
    mm.emitHome(axis)
    cw.write("Axis " + str(axis) + " going home \n")
    mm.waitForMotionCompletion()
    cw.write("Axis " + str(axis) + " is at home \n")

    while True:
        # Move the axis
        position = cw.askNumeric("Please enter the absolute position you wish to move to")
        mm.emitAbsoluteMove(axis, position)
        cw.write("Motion on-going ... \n")
        mm.waitForMotionCompletion()
        if not cw.askYesNo("Would you like to do another move?"):
            break

    cw.quitCW()

except cw.userQuit:
    mm.emitStop()
    pass

time.sleep(1)
sys.exit(0)


