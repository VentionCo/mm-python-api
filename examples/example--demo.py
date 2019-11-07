##################################################
## Demo
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

cw = configWizard.configWizard()

try:
    question = "What actuator do you have installed on axis 1?"
    valid = {
        "timing belt":MECH_GAIN.timing_belt_150mm_turn,
        "ballscrew"    : MECH_GAIN.ballscrew_10mm_turn,
        "indexer"    : MECH_GAIN.indexer_deg_turn,   
        "conveyor"    : MECH_GAIN.conveyor_mm_turn,               
        "rack and pinion"    : MECH_GAIN.rack_pinion_mm_turn                  
        }

    mechGain = cw.askMultipleChoice(question, valid)
    mm.configAxis(1, MICRO_STEPS.ustep_8, mechGain)
    cw.write("MachineMotion Axis 1 Configured\n")


    if cw.askYesNo("Would you like to begin homing Axis 1?") == False:
        cw.write("You must home Axis 1 before sending motion commands")
        if cw.askYesNo("Are you ready to home Axis 1? If No, the demo will exit") == False:
            exit()



    cw.write("Machine Motion going home")
    mm.emitHome(1)

    mm.waitForMotionCompletion()

    machineSpeed = cw.askNumeric("Please set the machine speed in mm/s")
    mm.emitSpeed(machineSpeed)

    cw.write("Machine Motion is waving!")

    mm.emitAbsoluteMove(1,40)
    mm.emitAbsoluteMove(1,0)
    mm.emitAbsoluteMove(1,40)
    mm.emitAbsoluteMove(1,0)

    mm.waitForMotionCompletion()

    cw.write("Goodbye!")
    cw.quit()

except cw.userQuit:
    mm.emitStop()
    pass

time.sleep(1)
sys.exit(0)