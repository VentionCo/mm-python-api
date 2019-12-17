import sys, os
this_script_folder = os.path.dirname(__file__)
relative_path_to_MachineMotion_folder = os.path.dirname("../")
sys.path.insert(1, os.path.join(this_script_folder,relative_path_to_MachineMotion_folder))
from MachineMotion import *

mm = MachineMotion(DEFAULT_IP_ADDRESS.usb_windows)

axis = 1                                    #The axis that you'd like to move
speed = 400                                 #The max speed you'd like to move at
acceleration = 500                          #The constant acceleration and decceleration value for the move
position = 100                              #The absolute position you'd like to move to
mechGain = MECH_GAIN.rack_pinion_mm_turn    #The mechanical gain of the actuator on the axis

mm.emitSpeed(speed)
mm.emitAcceleration(acceleration)
mm.configAxis(axis, MICRO_STEPS.ustep_16, mechGain)

mm.emitHome(axis)
mm.waitForMotionCompletion()
print("Axis " + str(axis) + " homed")

print("Absolute Moves are referenced from home")
mm.emitAbsoluteMove(axis, position)
mm.waitForMotionCompletion()
print("Axis " + str(axis) + " is " + str(position) + "mm away from home")

mm.setPosition(axis, 0)
print("Absolute moves on axis " + str(axis) + " are now referenced from " +  str(position) + "mm from home. ")
time.sleep(2)
print("Now moving to absolute Position 10 mm, referenced from location 'setPosition' was called")
position2 = 30
mm.emitAbsoluteMove(axis, position2)
mm.waitForMotionCompletion()
print("Axis " + str(axis) + " is now " + str(position2) + "mm from reference position and " + str(position + position2) + "mm from home")

