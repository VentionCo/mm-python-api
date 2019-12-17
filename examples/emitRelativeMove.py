import sys, os
this_script_folder = os.path.dirname(__file__)
relative_path_to_MachineMotion_folder = os.path.dirname("../")
sys.path.insert(1, os.path.join(this_script_folder,relative_path_to_MachineMotion_folder))
from MachineMotion import *

mm = MachineMotion(DEFAULT_IP_ADDRESS.usb_windows)

#Define Relative Move Parameters
axis = 1
speed = 400
acceleration = 500
distance = 100
direction = "positive"
mechGain = MECH_GAIN.rack_pinion_mm_turn

#Load Relative Move Parameters
mm.emitSpeed(speed)
mm.emitAcceleration(acceleration)
mm.configAxis(axis, MICRO_STEPS.ustep_8, mechGain)

#Home Axis Before Move
print("Axis " + str(axis) + " moving home.")
mm.emitHome(axis)
mm.waitForMotionCompletion()
print("Axis " + str(axis) + " homed")

#Begin Relative Move
mm.emitRelativeMove(axis, direction, distance)
mm.waitForMotionCompletion()
print("Axis " + str(axis) + " moved " + str(distance) + "mm in the " + direction + " direction")
