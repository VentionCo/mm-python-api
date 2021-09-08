import sys
sys.path.append("../..")
from MachineMotion import *

### This Python example configures homing speed for MachineMotion v1. ###

mm = MachineMotion()

# When starting a program, one must remove the software stop before moving
print("--> Removing software stop")
mm.releaseEstop()
print("--> Resetting system")
mm.resetSystem()

### Configuring ###

axes = [1,2]
homingSpeeds = [50,100] # The homing speeds to set for each axis, in mm/sec

mm.configAxis(1, MICRO_STEPS.ustep_8, MECH_GAIN.timing_belt_150mm_turn)
mm.configAxis(2, MICRO_STEPS.ustep_8, MECH_GAIN.timing_belt_150mm_turn)
mm.configHomingSpeed(axes, homingSpeeds)    # Sets homing speeds for all selected axes.

### Testing the configuration ###

axis = 1    # The axis to move

print("Moving axis " + str(axis) + " by 100mm.")
mm.moveRelative(axis, 100)
mm.waitForMotionCompletion()

#Homes the axis at the newly configured homing speed.
print("Homing axis " + str(axis))
mm.moveToHome(axis)
