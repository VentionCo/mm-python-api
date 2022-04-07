#!/usr/bin/python

from MachineMotion import *

### IMPORTANT: This example file is compatible with MachineMotion Software version 2.4.0 or newer. ###

### speedAndAcceleration.py
# This example shows how to change the configured max speed and max acceleration for an axis,
# as well as how to retrieve the configured max speed, max acceleration and actual speed of a specific axis.

mm = MachineMotionV2()

axis        = AXIS_NUMBER.DRIVE1

maxSpeedAxis        = 50   # mm/s
maxAccelerationAxis = 150  # mm/s^2

# Setting speeds and accelerations

print('Setting max speed for axis ', axis, ': ', maxSpeedAxis, "mm/s")
mm.setAxisMaxSpeed(axis, maxSpeedAxis)
print('Setting max acceleration for axis ', axis, ': ', maxAccelerationAxis, "mm/s^2")
mm.setAxisMaxAcceleration(axis, maxAccelerationAxis)

# Getting speeds and accelerations

print('Getting speeds and accelerations...')

maxSpeed = mm.getAxisMaxSpeed(axis)
maxAccel = mm.getAxisMaxAcceleration(axis)
print('For axis ', axis, ' retrieved max speed: ', maxSpeed, 'mm/s, max acceleration: ', maxAccel, 'mm/s^2')

actualSpeed = mm.getActualSpeeds(axis)
print('For axis ', axis, ' retrieved actual speed: ', actualSpeed, 'mm/s') # The value should be 0 as the axis is not moving.

print("Getting actual speeds for all axes, in mm/s:")
actualSpeeds = mm.getActualSpeeds()
print(actualSpeeds) # The values should be 0 as the axes are not moving.

print('Done!')
