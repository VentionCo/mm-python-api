import sys
sys.path.append("../..")
from MachineMotion import *

### This Python example configures actuator direction for MachineMotion v1. ###

mm = MachineMotion()

#When starting a program, one must remove the software stop before moving
print("--> Removing software stop")
mm.releaseEstop()
print("--> Resetting system")
mm.resetSystem()

# Configure the axis number 1, 8 uSteps and 150 mm / turn for a timing belt
axis = AXIS_NUMBER.DRIVE1
uStep = MICRO_STEPS.ustep_8
mechGain = MECH_GAIN.timing_belt_150mm_turn
mm.configAxis(axis, uStep, mechGain)

homesTowards = {
    DIRECTION.NORMAL: "sensor " + str(axis) + "A",
    DIRECTION.REVERSE: "sensor " + str(axis) + "B"
}

# Change axis direction, and see how it affects subsequent moves
direction = DIRECTION.REVERSE
mm.configAxisDirection(axis, direction)
print("Axis " + str(axis) + " is set to " + direction + " mode. It will now home towards " + homesTowards[direction] + "." )
mm.moveToHome(axis)

direction = DIRECTION.NORMAL
mm.configAxisDirection(axis, direction)
print("Axis " + str(axis) + " is set to " + direction + " mode. It will now home towards " + homesTowards[direction] + "." )
mm.moveToHome(axis)
