import sys
sys.path.append("../..")
from MachineMotion import *

### This Python example configures system speed for MachineMotion v2. ###

mm = MachineMotion(machineMotionHwVersion=MACHINEMOTION_HW_VERSIONS.MMv2)

speed = 500      # The max speed [mm/s] that all subsequent moves will move at
mm.emitSpeed(speed)
print("Global speed set to " + str(speed) + "mm/s.")
