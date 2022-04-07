#!/usr/bin/python
import time
from MachineMotion import *

### IMPORTANT: This example file is compatible with MachineMotion Software version 2.4.0 or newer. ###

### This Python example configures and moves an independent axis.
### The individual axis speed and acceleration are set, 
### then motion on the axis is selectively started, stopped and monitored

mm = MachineMotionV2()

# When starting a program, one must remove the software stop before moving
print("--> Removing software stop")
mm.releaseEstop()
print("--> Resetting system")
mm.resetSystem()

# Configure the axis
axis = 1
mm.configServo(axis, MECH_GAIN.timing_belt_150mm_turn, DIRECTION.NORMAL, 10.0, motorSize=MOTOR_SIZE.LARGE)

# Move, stop and monitor the axis
axisSpeed = 50          # mm/s
axisAcceleration = 50   # mm/s^2
distance = 250          # mm

print(
    'Configuring axis: ', axis,
    ' speed: ', axisSpeed, 'mm/s',
    ' acceleration: ', axisAcceleration, 'mm/s^2'
)
mm.setAxisMaxSpeed(axis, axisSpeed)
mm.setAxisMaxAcceleration(axis, axisAcceleration)

print('Relative move: ', distance, 'mm')
mm.moveRelative(axis,distance)

axisMotionCompleted = mm.isMotionCompleted(axis)
if axisMotionCompleted :
    print ('Axis ', axis, ' is NOT currently moving.')
else :
    print ('Axis ', axis, ' is currently moving.')

time.sleep(3)

print('Stopping just axis: ', axis)
mm.stopAxis(axis)

time.sleep(3)

print('Moving and waiting for axis: ', axis)
mm.moveToPosition(axis,distance)
mm.waitForMotionCompletion(axis)

print('Done!')
