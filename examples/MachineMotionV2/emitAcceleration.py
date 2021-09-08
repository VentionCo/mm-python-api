import sys
sys.path.append("../..")
from MachineMotion import *

### This Python example configures system acceleration for MachineMotion v2. ###

mm = MachineMotion(machineMotionHwVersion=MACHINEMOTION_HW_VERSIONS.MMv2)

acceleration = 500      # The max acceleration [mm/s^2] that all subsequent moves will move at
mm.emitAcceleration(acceleration)
print("Global acceleration set to " + str(acceleration) + "mm/s^2.")
