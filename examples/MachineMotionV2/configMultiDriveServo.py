import sys
sys.path.append("../..")
from MachineMotion import *

### This Python example configures and moves a multi-drive axis. ###

### Multiple motors that are mechanically linked can now be treated
### as though they are a single axis. Once propely configured,
### multi-drive axes can be moved just as with single-drive axes.

### Machine Motion declaration
mm = MachineMotionV2()

### If not on a conveyor, the parent drive must have home and end sensors.
### The child drive's sensors will be ignored.
parent = 1
parentDirection = DIRECTION.NORMAL
child = 2
childDirection = DIRECTION.NORMAL

mechGain = MECH_GAIN.timing_belt_150mm_turn
motorCurrent = 5.0 # Current (A)

print("--> Configuring parent drive " + str(parent) + " with child " + str(child))

### Configure your multi-drive axis by passing the list of drives, directions and parent drive.
mm.configServo([parent, child], mechGain, [parentDirection, childDirection], motorCurrent, parentDrive = parent)

### The parent and child drives are now linked.
### Control the multi-drive axis via the parent drive:

print("--> Multi-drive axis is moving relative by 200mm!")
mm.moveRelative(parent, 200)
mm.waitForMotionCompletion()

print("--> Example Complete!")
