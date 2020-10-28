import os, sys
sys.path.append(os.path.abspath(__file__ + "/../../"))
from MachineMotion import *

mm = MachineMotion(DEFAULT_IP_ADDRESS.usb_windows)

#When starting a program, one must remove the software stop before moving
print("--> Removing software stop")
mm.releaseEstop()
print("--> Resetting system")
mm.resetSystem()

axis = 1                                    #The axis that you'd like to move
speed = 400                                 #The max speed you'd like to move at
acceleration = 500                          #The constant acceleration and decceleration value for the move
position = 100                              #The absolute position you'd like to move to
mechGain = MECH_GAIN.rack_pinion_mm_turn    #The mechanical gain of the actuator on the axis

mm.emitSpeed(speed)
mm.emitAcceleration(acceleration)
mm.configAxis(axis, MICRO_STEPS.ustep_16, mechGain)

mm.emitHome(axis)
mm.waitForMotionCompletion()
print("Axis " + str(axis) + " homed")

print("Absolute Moves are referenced from home")
mm.emitAbsoluteMove(axis, position)
mm.waitForMotionCompletion()
print("Axis " + str(axis) + " is " + str(position) + "mm away from home")

mm.setPosition(axis, 0)
print("Absolute moves on axis " + str(axis) + " are now referenced from " +  str(position) + "mm from home. ")
time.sleep(2)
position2 = 30
print("Now moving to absolute Position " + str(position2) + " mm, referenced from location 'setPosition' was called")
mm.emitAbsoluteMove(axis, position2)
mm.waitForMotionCompletion()
print("Axis " + str(axis) + " is now " + str(position2) + "mm from reference position and " + str(position + position2) + "mm from home")
