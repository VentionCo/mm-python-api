import sys, time
sys.path.append("../..")
from MachineMotion import *

### This Python example showcases how to set actuator position with MachineMotion v2. ###

mm = MachineMotionV2()

# When starting a program, one must remove the software stop before moving
print("--> Removing software stop")
mm.releaseEstop()
print("--> Resetting system")
mm.resetSystem()

# Configure the actuator
axis = 1
mm.configServo(axis, MECH_GAIN.timing_belt_150mm_turn, DIRECTION.NORMAL, 10.0, motorSize=MOTOR_SIZE.LARGE)

# Home the actuator
print("Axis " + str(axis) + " will home")
mm.moveToHome(axis)
mm.waitForMotionCompletion()
print("Axis " + str(axis) + " homed")

### Perform asolute moves with different reference points ###

print("Absolute Moves are referenced from home")
position = 100
mm.moveToPosition(axis, position)
mm.waitForMotionCompletion()
print("Axis " + str(axis) + " is " + str(position) + "mm away from home.")

# Change the reference point to the current position
mm.setPosition(axis, 0)
print("Absolute moves on axis " + str(axis) + " are now referenced from " +  str(position) + "mm from home. ")
time.sleep(2)

# Move again
position2 = 30
print("Now moving to absolute position " + str(position2) + " mm, referenced from location 'setPosition' was called")
mm.moveToPosition(axis, position2)
mm.waitForMotionCompletion()
print("Axis " + str(axis) + " is now " + str(position2) + "mm from reference position and " + str(position + position2) + "mm from home")
