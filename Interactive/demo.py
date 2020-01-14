##################################################
## Demo
##################################################
## Version: 1.6.8
## Email: info@vention.cc
## Status: tested
##################################################

enableDebug = False

import os, sys
import configWizard
#Adds mm-python-api to the sys path so that we can access MachineMotion.py 
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parentdir)

from _MachineMotion import *

# Define a callback to process controller gCode responses if desired. This is mostly used for debugging purposes.
def debug(data):
    if(enableDebug): print("Debug Message: " + data + "\n")

print ("Application Message: MachineMotion Program Starting \n")

mm = MachineMotion(debug, DEFAULT_IP_ADDRESS.usb_windows)
print ("Application Message: MachineMotion Controller Connected \n")

cw = configWizard.configWizard()

try:

    axis = cw.askForSingleAxis()
    mechGain = cw.askForMechGain(axis)

    mm.configAxis(axis, MICRO_STEPS.ustep_8, mechGain)
    cw.write("MachineMotion Axis " + str(axis) + " Configured\n")

    cw.forceUserToHome(axis)
    cw.write("Machine Motion going home")
    mm.emitHome(axis)

    mm.waitForMotionCompletion()

    machineSpeed = cw.askNumeric("Please set the machine speed in mm/s")
    mm.emitSpeed(machineSpeed)

    cw.write("Machine Motion is waving!")

    mm.emitAbsoluteMove(axis,40)
    mm.emitAbsoluteMove(axis,0)
    mm.emitAbsoluteMove(axis,40)
    mm.emitAbsoluteMove(axis,0)

    mm.waitForMotionCompletion()

    cw.write("Goodbye!")
    cw.quitCW()

except cw.userQuit:
    mm.emitStop()
    pass

time.sleep(1)
sys.exit(0)