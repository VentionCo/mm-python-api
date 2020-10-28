import sys
sys.path.append("..")
from MachineMotion import *

mm = MachineMotion(DEFAULT_IP_ADDRESS.usb_windows)

#When starting a program, one must remove the software stop before moving
# print("--> Removing software stop")
# mm.releaseEstop()
# print("--> Resetting system")
# mm.resetSystem()

axes = [1,2,3]
homingSpeeds = [15,15,4]                        #The homing speeds to set for each axis



#Sets minimum and maximum allowable homing speeds for each axis
minHomingSpeeds = [3, 3, 3]
maxHomingSpeeds = [50, 50, 50]
mm.configMinMaxHomingSpeed(axes,minHomingSpeeds, maxHomingSpeeds, UNITS_SPEED.mm_per_sec)

#Sets homing speeds for all three axes. The selected homing speed must be within the range set by configMinMaxHomingSpeeds
mm.configHomingSpeed(axes, homingSpeeds)
mm.waitForMotionCompletion()

print("Done")
