import sys, time
sys.path.append("../..")
from MachineMotion import *

### This Python example showcases how to read actuator positions with MachineMotion v2. ###

###### CONFIGURING MACHINEMOTION ######

mm = MachineMotionV2()

# When starting a program, one must remove the software stop before moving
print("--> Removing software stop")
mm.releaseEstop()
print("--> Resetting system")
mm.resetSystem()

# Configure actuator
axis = 1
print("--> Configuring actuator")
mm.configServo(axis, MECH_GAIN.rack_pinion_mm_turn, DIRECTION.POSITIVE, 5.0)

# Home Axis Before Moving
print("--> Axis " + str(axis) + " moving home")
mm.moveToHome(axis)
mm.waitForMotionCompletion()
print("--> Axis " + str(axis) + " homed")


###### READ POSITIONS ######

# Read the position of one axis
print("--> Read the position of one axis")
actualPosition_axis  = mm.getActualPositions(axis)
print("Actual position of axis " + str(axis) + " is : " + str(actualPosition_axis) + " mm.")

# Read the position of several axes
print("--> Read the position of several axes")
actualPositions  = mm.getActualPositions()
print("Actual position of axis 1 is : " + str(actualPositions[1]) + " mm.")
print("Actual position of axis 2 is : " + str(actualPositions[2]) + " mm.")
print("Actual position of axis 3 is : " + str(actualPositions[3]) + " mm.")
print("Actual position of axis 4 is : " + str(actualPositions[4]) + " mm.")

###### MOVE AND READ POSITIONS ######

# Define Motion Parameters
distance = 100

# Move 100mm and check position again
mm.moveRelative(axis, distance)
print("--> Move ongoing")
while not mm.isMotionCompleted():
    actualPosition_axis  = mm.getActualPositions(axis)
    print("Actual position of axis " + str(axis) + " is : " + str(actualPosition_axis) + " mm.")

mm.waitForMotionCompletion()
print("--> Move completed")
actualPosition_axis  = mm.getActualPositions(axis)
print("Actual position of axis " + str(axis) + " is : " + str(actualPosition_axis) + " mm.")

print("--> End of example")
