import sys
sys.path.append("..")
from MachineMotion import *

# Define a callback to process controller gCode responses (if desired)
def templateCallback(data):
   print ( "Controller gCode responses " + data )

mm = MachineMotion(DEFAULT_IP_ADDRESS.usb_windows, gCodeCallback = templateCallback)

#When starting a program, one must remove the software stop before moving
print("--> Removing software stop")
mm.releaseEstop()
print("--> Resetting system")
mm.resetSystem()

axis = 1                                       #The axis that you'd like to move
speed = 400                                    #The max speed you'd like to move at
acceleration = 500                             #The constant acceleration and decceleration value for the move
position = 100                                 #The absolute position you'd like to move to
mechGain = MECH_GAIN.timing_belt_150mm_turn    #The mechanical gain of the actuator on the axis
mm.configAxis(axis, MICRO_STEPS.ustep_8, mechGain)

# Home Axis before absolute move
mm.emitHome(axis)
print("Axis " + str(axis) + " is going home.")
mm.waitForMotionCompletion()
print("Axis " + str(axis) + " homed.")

# Configure movement speed, acceleration and then move
mm.emitSpeed(speed)
mm.emitAcceleration(acceleration)
mm.emitAbsoluteMove(axis, position)
print("Axis " + str(axis) + " is moving towards position " + str(position) + "mm")
mm.waitForMotionCompletion()
print("Axis " + str(axis) + " is at position " + str(position) + "mm")
