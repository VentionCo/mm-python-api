import sys, time, math
sys.path.append("../..")
from MachineMotion import *
from multiDriveExtension import *

### This Python example showcases how control an actuator driven by multiple motors, with MachineMotion v2. ###
### Please note that you can only couple motors connected to drives 1, 2, or 3. ###
### Please note that continuous moves are not supported on coupled drives. ###

############################
###### INITIALIZATION ######
############################

# Create MachineMotion instance first
mm = MachineMotion(machineMotionHwVersion=MACHINEMOTION_HW_VERSIONS.MMv2)
# Add a multidrive extension to the created machineMotion instance
mm_multidrive = MultiDriveExtension(mm)

# When starting a program, one must remove the software stop before moving
print("--> Removing software stop")
mm.releaseEstop()
print("--> Resetting system")
mm.resetSystem()

###########################
###### CONFIGURATION ######
###########################

print("Configuring coupled drives")
# Couple the movement of the motors plugged in drives 1 and 2.
# Note : you can only couple motors connected to drives 1, 2, or 3.
# Each motor is connected to a drive port, and installed in a given direction.
# All motors connected to the same actuator will share the same mechanical gain, motor current, and tuning profile values.
coupledDrives   = [AXIS_NUMBER.DRIVE1, AXIS_NUMBER.DRIVE2]  # coupled drive port numbers
directionList   = [DIRECTION.NORMAL, DIRECTION.REVERSE]     # the directions of each motor. IMPORTANT : Make sure the motors are spinning in the right direction
mechGain        = MECH_GAIN.timing_belt_150mm_turn          # mechanical gain of the actuator, in mm/turn
motorCurrent    = 6                                         # motor current, in Amp
mm_multidrive.configServoMulti(coupledDrives, mechGain, directionList, motorCurrent)

print("Configuring single drive")
# A single motor drives the axis corresponding to the 3rd drive.
singleDrive     = AXIS_NUMBER.DRIVE3                        # drive port numbers
direction       = DIRECTION.NORMAL                          # direction of the motor
mechGain        = MECH_GAIN.timing_belt_150mm_turn          # mechanical gain of the actuator, in mm/turn
motorCurrent    = 6                                         # motor current, in Amp
mm.configServo(singleDrive, mechGain, direction, motorCurrent)

#######################
###### MOVEMENTS ######
#######################

# Home the axes
print("Homing single drive")
mm.emitHome(singleDrive)
print("Homing coupled drives")
mm_multidrive.emitHomeMulti(coupledDrives)
# Note : always set speed and acceleration after emitHomeMulti

# Move the axes
speed = 200         # mm/sec
acceleration = 200  # mm/sec^2
distance = 100      # mm
position = 50       # mm
mm_multidrive.emitSpeedMulti(coupledDrives, speed)                # sets the speed of all axes
mm_multidrive.emitAccelerationMulti(coupledDrives, acceleration)  # sets the acceleration of all axes
print("Moving coupled drives by " + str(distance) + "mm")
mm_multidrive.emitRelativeMoveMulti(coupledDrives, DIRECTION.POSITIVE, distance)
mm.waitForMotionCompletion()
print("Moving coupled drives to " + str(position) + "mm")
mm_multidrive.emitAbsoluteMoveMulti(coupledDrives, position)
mm.waitForMotionCompletion()

mm.emitSpeed(speed)                 # sets the speed of all axes
mm.emitAcceleration(acceleration)   # sets the acceleration of all axes
print("Moving single drive by " + str(distance) + "mm")
mm.emitRelativeMove(singleDrive, DIRECTION.POSITIVE, distance)
mm.waitForMotionCompletion()
print("Moving single drive to " + str(position) + "mm")
mm.emitAbsoluteMove(singleDrive, position)
mm.waitForMotionCompletion()

# Read the position
print("Position of singleDrive is : ", mm.getActualPositions(singleDrive))
print("Position of coupledDrives is : ", mm_multidrive.getActualPositionsMulti(coupledDrives))

# Set the position
new_position = 0    # mm
print("Setting positions to zero")
mm.setPosition(singleDrive, new_position)
mm_multidrive.setPositionMulti(coupledDrives, new_position)
