import sys
sys.path.append("../..")
from MachineMotion import *

### This Python example showcases how to home actuators with MachineMotion v2. ###

mm = MachineMotionV2()

# When starting a program, one must remove the software stop before moving
print("--> Removing software stop")
mm.releaseEstop()
print("--> Resetting system")
mm.resetSystem()

# Configure the actuator
axis = AXIS_NUMBER.DRIVE1
mm.configServo(axis, MECH_GAIN.timing_belt_150mm_turn, DIRECTION.NORMAL, 5.0)

# Home the actuator
print ("Axis "+ str(axis) +" is going home")
mm.moveToHome(axis)
mm.waitForMotionCompletion()
print("Axis "+ str(axis) +" is at home")
