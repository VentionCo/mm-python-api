import sys
sys.path.append("../..")
from MachineMotion import *

### This Python example showcases how to home actuators with MachineMotion v2. ###

### MachineMotion configuration ###

mm = MachineMotion(machineMotionHwVersion=MACHINEMOTION_HW_VERSIONS.MMv2)

# When starting a program, one must remove the software stop before moving
print("--> Removing software stop")
mm.releaseEstop()
print("--> Resetting system")
mm.resetSystem()

### Home all axes sequentially
print ("All Axes Moving Home sequentially")
mm.emitHomeAll()
print("All Axes Homed")
