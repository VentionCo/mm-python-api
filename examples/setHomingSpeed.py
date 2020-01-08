import sys, os
this_script_folder = os.path.dirname(__file__)
relative_path_to_MachineMotion_folder = os.path.dirname("../")
sys.path.insert(1, os.path.join(this_script_folder,relative_path_to_MachineMotion_folder))
from MachineMotion import *

mm = MachineMotion(DEFAULT_IP_ADDRESS.usb_windows)

axis = 1                                    #The axis that you'd like to move
speed = 500                                 #The max speed you'd like to move at
acceleration = 500                          #The constant acceleration and decceleration value for the move
mechGain = MECH_GAIN.rack_pinion_mm_turn    #The mechanical gain of the actuator on the axis

mm.configAxis(axis, MICRO_STEPS.ustep_8, mechGain)
mm.emitSpeed(speed)
mm.emitAcceleration(acceleration)
homingSpeeds = [20, 500, 1000]

for homingSpeed in homingSpeeds:
    print("Moving to position = 500")
    mm.emitAbsoluteMove(axis, 500)
    mm.waitForMotionCompletion()
    print("Now going home at " + str(homingSpeed) + " mm/s")
    mm.setHomingSpeed(axis, homingSpeed)
    mm.emitHome(axis)
    mm.waitForMotionCompletion()

print("All future homing commands will now be set at " + str(homingSpeed) + " mm/s")