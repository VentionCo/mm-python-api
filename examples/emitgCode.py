import sys, os
this_script_folder = os.path.dirname(__file__)
relative_path_to_MachineMotion_folder = os.path.dirname("../")
sys.path.insert(1, os.path.join(this_script_folder,relative_path_to_MachineMotion_folder))
from MachineMotion import *

#Declare parameters for g-Code command
speed = 500
acceleration = 500
mechGain = MECH_GAIN.timing_belt_150mm_turn

#Load parameters for emitting g-code
mm = MachineMotion(DEFAULT_IP_ADDRESS.usb_windows)
mm.emitSpeed(speed)
mm.emitAcceleration(acceleration)
mm.emitHomeAll()
print("All Axes homed.")

# Use the G0 command to move both axis 1 and 2 by 50mm
gCodeCommand = "G0 X50 Y50"
mm.emitgCode(gCodeCommand)
mm.waitForMotionCompletion()
print("G-code command '" + gCodeCommand + "' completed by MachineMotion.")
