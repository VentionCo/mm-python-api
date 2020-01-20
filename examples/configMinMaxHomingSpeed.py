import sys
sys.path.append("..")
from MachineMotion import *

mm = MachineMotion(DEFAULT_IP_ADDRESS.usb_windows)

#When starting a program, one must remove the software stop before moving
print("--> Removing software stop")
mm.releaseEstop()
print("--> Resetting system")
mm.resetSystem()

axis = 1                                    #The axis that you'd like to move
speed = 500                                 #The max speed you'd like to move at
acceleration = 500                          #The constant acceleration and decceleration value for the move
mechGain = MECH_GAIN.rack_pinion_mm_turn    #The mechanical gain of the actuator on the axis

mm.configAxis(axis, MICRO_STEPS.ustep_8, mechGain)
mm.emitSpeed(speed)
mm.emitAcceleration(acceleration)

minHomingSpeeds = [10, 10, 10]
maxHomingSpeeds = [250, 250, 250]

mm.configMinMaxHomingSpeed([1,2,3], minHomingSpeeds, maxHomingSpeeds)

homingSpeeds = [20, 50, 100]

for homingSpeed in homingSpeeds:
    print("Moving to position = 2000")
    mm.emitAbsoluteMove(axis, 2000)
    mm.waitForMotionCompletion()
    print("Going home at " + str(homingSpeed) + " mm/s")
    mm.configHomingSpeed(axis, homingSpeed)
    mm.emitHome(axis)
    mm.waitForMotionCompletion()

print("All future homing commands will now be set at " + str(homingSpeed) + " mm/s")
