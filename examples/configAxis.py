import sys, os
this_script_folder = os.path.dirname(__file__)
relative_path_to_MachineMotion_folder = os.path.dirname("../")
sys.path.insert(1, os.path.join(this_script_folder,relative_path_to_MachineMotion_folder))
from MachineMotion import *

mm = MachineMotion(DEFAULT_IP_ADDRESS.usb_windows)

# Configure the axis number 1, 8 uSteps and 150 mm / turn for a timing belt
axis = AXIS_NUMBER.DRIVE1
uStep = MICRO_STEPS.ustep_8
mechGain = MECH_GAIN.timing_belt_150mm_turn
mm.configAxis(axis, uStep, mechGain)
print("Axis " + str(axis) + " configured with " + str(uStep) + " microstepping and " + str(mechGain) + "mm/turn mechanical gain")

