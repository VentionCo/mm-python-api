import sys, os
this_script_folder = os.path.dirname(__file__)
relative_path_to_MachineMotion_folder = os.path.dirname("../")
sys.path.insert(1, os.path.join(this_script_folder,relative_path_to_MachineMotion_folder))
from MachineMotion import *
import time

mm = MachineMotion(DEFAULT_IP_ADDRESS.usb_windows)

#Define Relative Move Parameters
axis = 1
speed = 200
acceleration = 500
distance = 1000
direction = "positive"
mechGain = MECH_GAIN.rack_pinion_mm_turn

#Load Relative Move Parameters
mm.emitSpeed(speed)
mm.emitAcceleration(acceleration)
mm.configAxis(axis, MICRO_STEPS.ustep_8, mechGain)

#Home Axis Before Move
mm.emitHome(axis)
print("Axis " + str(axis) + " is going home")
mm.waitForMotionCompletion()
print("Axis " + str(axis) + " homed")

#Begin Relative Move
mm.emitRelativeMove(axis, direction, distance)
print("Axis " + str(axis) + " is moving " + str(distance) + "mm in the " + direction + " direction")

#This move should take 5 (distance/speed) seconds to complete. Instead, we wait 2 seconds and then stop the machine.
time.sleep(2)
mm.emitStop()
print("Axis " + str(axis) + " stopped.")
