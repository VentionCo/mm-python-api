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
    question = "What axis would you like to test?"
    valid = {"Drive 1":1, "Drive 2":2, "Drive 3":3}
    axis = cw.askMultipleChoice(question, valid)

    question = "What actuator do you have installed on axis " + str(axis)+ "?"
    valid = {
        "timing belt"    :MECH_GAIN.timing_belt_150mm_turn,
        "ballscrew"      :MECH_GAIN.ballscrew_10mm_turn,
        "indexer"        : MECH_GAIN.indexer_deg_turn,   
        "conveyor"       : MECH_GAIN.conveyor_mm_turn,               
        "rack and pinion": MECH_GAIN.rack_pinion_mm_turn                  
        }

    mechGain = cw.askMultipleChoice(question, valid)
    mm.configAxis(axis, MICRO_STEPS.ustep_8, mechGain)
    cw.write("MachineMotion Axis " + str(axis) + " Configured\n")


    if cw.askYesNo("Would you like to begin homing Axis " + str(axis) + " ?") == False:
        cw.write("You must home Axis " + axis + " before sending motion commands")
        if cw.askYesNo("Are you ready to home Axis " + axis + "? If No, the demo will exit") == False:
            exit()



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
    cw.quit()

except cw.userQuit:
    mm.emitStop()
    pass

time.sleep(1)
sys.exit(0)