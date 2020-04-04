import sys
sys.path.append("..")
from MachineMotion import *

mm = MachineMotion(DEFAULT_IP_ADDRESS.usb_windows)

#When starting a program, one must remove the software stop before moving
print("--> Removing software stop")
mm.releaseEstop()
print("--> Resetting system")
mm.resetSystem()

axes = [1,2,3]
axis = 3                                    #The axis that you'd like to move
homingSpeeds = [50,50,50]                        #The homing speeds to set for each axis

mm.emitSpeed(100)
mm.emitAcceleration(50)
mm.configAxis(axis, MICRO_STEPS.ustep_8, MECH_GAIN.timing_belt_150mm_turn)

print("Moving to position = 100")
mm.emitAbsoluteMove(axis, 100)
mm.waitForMotionCompletion()

#Sets minimum and maximum allowable homing speeds for each axis
minHomingSpeeds = [20, 20, 20]
maxHomingSpeeds = [250, 250, 250]
mm.configMinMaxHomingSpeed(axes,minHomingSpeeds, maxHomingSpeeds, UNITS_SPEED.mm_per_sec)

#Sets homing speeds for all three axes. The selected homing speed must be within the range set by configMinMaxHomingSpeeds
mm.configHomingSpeed(axes, homingSpeeds)

#Homes the axis at the newly configured homing speed.
mm.emitHome(axis)
