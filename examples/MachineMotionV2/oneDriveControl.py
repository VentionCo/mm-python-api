import sys
sys.path.append("../..")
from MachineMotion import *

### This Python example showcases how to control a motor with a One Drive MachineMotion v2. ###

### MachineMotion configuration ###

mm = MachineMotionV2OneDrive()

# When starting a program, one must remove the software stop before moving
print("--> Removing software stop")
mm.releaseEstop()
print("--> Resetting system")
mm.resetSystem()

axis = AXIS_NUMBER.DRIVE1
motorCurrent = 7.5 # current (A)

print("--> Configuring axis " + str(axis) + " as timing belt")
mm.configServo(axis, MECH_GAIN.timing_belt_150mm_turn, DIRECTION.NORMAL, motorCurrent)

### Home axis 1 specifically
print("--> Homing axis " + str(axis))
mm.moveToHome(axis)
mm.waitForMotionCompletion()

### Relative move axis 1
print("--> Moving axis " + str(axis) + " by 100mm.")
mm.moveRelative(axis, 100)
mm.waitForMotionCompletion()

### Absolute move axis 1
position = 50 # in mm
mm.moveToPosition(axis, position)
print("--> Axis " + str(axis) + " is moving towards position " + str(position) + "mm")
mm.waitForMotionCompletion()
print("--> Axis " + str(axis) + " is at position " + str(position) + "mm")

### Getting position for axis 1
print("--> Read the position of axis " + str(axis))
actualPosition = mm.getActualPositions(axis)
print("--> Actual position is: " + str(actualPosition))

### Controlling any other axis will yield an error:
try:
    print("--> Controlling an axis that doesn't exist..")
    mm.moveToPosition(2, position)
except Exception as e:
    print (e)

print("Example Complete!")
