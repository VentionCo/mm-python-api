import sys
sys.path.append("../..")
from MachineMotion import *

### This Python example configures system acceleration for MachineMotion v1. ###

mm = MachineMotion()

acceleration = 500      # The max acceleration [mm/s^2] that all subsequent moves will move at
mm.setAcceleration(acceleration)
print("Global acceleration set to " + str(acceleration) + "mm/s^2.")
