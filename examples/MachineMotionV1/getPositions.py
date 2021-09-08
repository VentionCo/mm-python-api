import sys, time
sys.path.append("../..")
from MachineMotion import *

### This Python example showcases how to read actuator positions with MachineMotion v1. ###

###### CONFIGURING MACHINEMOTION ######

mm = MachineMotion()

# When starting a program, one must remove the software stop before moving
print("--> Removing software stop")
mm.releaseEstop()
print("--> Resetting system")
mm.resetSystem()

# Configure actuator
axis = 1
print("--> Configuring actuator")
mm.configAxis(axis, MICRO_STEPS.ustep_8, MECH_GAIN.rack_pinion_mm_turn)

# Home Axis Before Moving
print("--> Axis " + str(axis) + " moving home")
mm.moveToHome(axis)
print("--> Axis " + str(axis) + " homed")


###### READ POSITIONS ######

# Read the position of one axis
print("--> Read the position of one axis")
desiredPosition_axis = mm.getDesiredPositions(axis)
actualPosition_axis  = mm.getActualPositions(axis)
print("Desired position of axis " + str(axis) + " is : " + str(desiredPosition_axis) + " mm.")
print("Actual position of axis " + str(axis) + " is : " + str(actualPosition_axis) + " mm.")

# Read the position of several axes
print("--> Read the position of several axes")
desiredPositions = mm.getDesiredPositions()
actualPositions  = mm.getActualPositions()
print("Desired position of axis 1 is : " + str(desiredPositions[1]) + " mm.")
print("Desired position of axis 2 is : " + str(desiredPositions[2]) + " mm.")
print("Desired position of axis 3 is : " + str(desiredPositions[3]) + " mm.")
print("Actual position of axis 1 is : " + str(actualPositions[1]) + " mm.")
print("Actual position of axis 2 is : " + str(actualPositions[2]) + " mm.")
print("Actual position of axis 3 is : " + str(actualPositions[3]) + " mm.")


###### MOVE AND READ POSITIONS ######

# Define Motion Parameters
distance = 500

# Move 500mm and check position again
mm.moveRelative(axis, distance)
desiredPosition_axis = mm.getDesiredPositions(axis)
print("--> Move ongoing")
print("Desired position of axis " + str(axis) + " is : " + str(desiredPosition_axis) + " mm.")
while not mm.isMotionCompleted():
    actualPosition_axis  = mm.getActualPositions(axis)
    print("Actual position of axis " + str(axis) + " is : " + str(actualPosition_axis) + " mm.")

mm.waitForMotionCompletion()
print("--> Move completed")
desiredPosition_axis = mm.getDesiredPositions(axis)
actualPosition_axis  = mm.getActualPositions(axis)
print("Desired position of axis " + str(axis) + " is : " + str(desiredPosition_axis) + " mm.")
print("Actual position of axis " + str(axis) + " is : " + str(actualPosition_axis) + " mm.")

print("--> End of example")
