import sys, time
sys.path.append("../..")
from MachineMotion import *

### This Python example showcases how to stop motion on MachineMotion v1. ###

mm = MachineMotion()

# When starting a program, one must remove the software stop before moving
print("--> Removing software stop")
mm.releaseEstop()
print("--> Resetting system")
mm.resetSystem()

# Configure the actuator
axis = 1
mm.configAxis(axis, MICRO_STEPS.ustep_8, MECH_GAIN.rack_pinion_mm_turn)

# Configure Move Parameters
speed = 200
mm.emitSpeed(speed)

# Begin Relative Move
distance = 1000
direction = DIRECTION.POSITIVE
mm.emitRelativeMove(axis, direction, distance)
print("Axis " + str(axis) + " is moving " + str(distance) + "mm in the " + direction + " direction.")
# This move should take 5 seconds to complete (distance/speed). Instead, we wait 2 seconds and then stop the machine.
time.sleep(2)
mm.emitStop()
print("Axis " + str(axis) + " stopped.")
