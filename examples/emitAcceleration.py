import sys
sys.path.append("..")
from _MachineMotion import *


mm = MachineMotion(DEFAULT_IP_ADDRESS.usb_windows)
acceleration = 500      # The acceleration [mm/s^2] that all subsequent moves will move at 
mm.emitAcceleration(acceleration)
print("Global acceleration set to " + str(acceleration))


