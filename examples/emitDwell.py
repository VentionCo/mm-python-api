import sys, os
this_script_folder = os.path.dirname(__file__)
relative_path_to_MachineMotion_folder = os.path.dirname("../")
sys.path.insert(1, os.path.join(this_script_folder,relative_path_to_MachineMotion_folder))
from MachineMotion import *

#Declare parameters for g-Code command
axis = 3
speed = 1000
acceleration = 2000
mechGain = MECH_GAIN.timing_belt_150mm_turn

#Load parameters for emitting g-code
mm = MachineMotion(DEFAULT_IP_ADDRESS.usb_windows)
mm.emitSpeed(speed)
mm.emitAcceleration(acceleration)
mm.emitHome(axis)

# Moves axis back and forth, waiting a specified amount of time between each move
mm.emitAbsoluteMove(axis, 100)
mm.emitDwell(250)
mm.emitAbsoluteMove(axis, 50)
mm.emitDwell(500)
mm.emitAbsoluteMove(axis, 100)
mm.emitDwell(1000)
mm.emitAbsoluteMove(axis, 50)
mm.emitDwell(5000)
print("emitDwell does not block this line from printing")
mm.waitForMotionCompletion()
print("but waitForMotionCompletion() will force python to wait the full 5000ms until emitDwell has finished.")


