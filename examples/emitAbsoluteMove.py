import configWizard
from _MachineMotion import *


# Define a callback to process controller gCode responses if desired. This is mostly used for debugging purposes.
enableDebug = False
def debug(data):
    if(enableDebug): print("Debug Message: " + data)

mm = MachineMotion(debug, DEFAULT_IP_ADDRESS.usb_windows)


axis = 3                                    #The axis that you'd like to move
speed = 400                                 #The max speed you'd like to move at
acceleration = 500                          #The constant acceleration and decceleration value for the move
position = 100                              #The absolute position you'd like to move to
mechGain = MECH_GAIN.rack_pinion_mm_turn    #The mechanical gain of the actuator on the axis

mm.configAxis(axis, MICRO_STEPS.ustep_8, mechGain)

mm.emitHome(axis)
print("Axis " + str(axis) + " homed")
mm.emitSpeed(speed)
mm.emitAcceleration(acceleration)
mm.emitAbsoluteMove(axis, position)
mm.waitForMotionCompletion()
print("Motion Complete!")



