import sys
sys.path.append("../..")
from MachineMotion import *

### This Python example configures system speed for MachineMotion v2. ###

mm = MachineMotionV2()

speed = 500      # The max speed [mm/s] that all subsequent moves will move at
mm.setSpeed(speed)
print("Global speed set to " + str(speed) + "mm/s.")
