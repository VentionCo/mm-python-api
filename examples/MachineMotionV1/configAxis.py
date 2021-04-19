import sys
sys.path.append("../..")
from MachineMotion import *

### This Python example configures an actuator for a MachineMotion v1. ###

mm = MachineMotion()

# Configure the axis number 1, 8 uSteps and 150 mm / turn for a timing belt
axis = AXIS_NUMBER.DRIVE1
uStep = MICRO_STEPS.ustep_8
mechGain = MECH_GAIN.timing_belt_150mm_turn
mm.configAxis(axis, uStep, mechGain)
print("Axis " + str(axis) + " configured with " + str(uStep) + " microstepping and " + str(mechGain) + "mm/turn mechanical gain")