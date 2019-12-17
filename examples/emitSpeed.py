import sys, os
this_script_folder = os.path.dirname(__file__)
relative_path_to_MachineMotion_folder = os.path.dirname("../")
sys.path.insert(1, os.path.join(this_script_folder,relative_path_to_MachineMotion_folder))
from MachineMotion import *

mm = MachineMotion(DEFAULT_IP_ADDRESS.usb_windows)
speed = 500      # The speed [mm/s] that all subsequent moves will move at 
mm.emitSpeed(speed)
print("Global acceleration set to " + str(speed))


