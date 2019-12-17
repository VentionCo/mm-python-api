import sys, os
this_script_folder = os.path.dirname(__file__)
relative_path_to_MachineMotion_folder = os.path.dirname("../")
sys.path.insert(1, os.path.join(this_script_folder,relative_path_to_MachineMotion_folder))
from MachineMotion import *

mm = MachineMotion(DEFAULT_IP_ADDRESS.usb_windows)
axis = AXIS_NUMBER.DRIVE1

mm.configAxis(axis, MICRO_STEPS.ustep_8, MECH_GAIN.timing_belt_150mm_turn)
mm.emitHome(axis)
print ("Application Message: Axis "+ str(axis) +" is going home")
mm.waitForMotionCompletion()
print("Application Message: Axis "+ str(axis) +" is at home")

