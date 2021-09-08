import sys
sys.path.append("../..")
from MachineMotion import *

### This Python example showcases how to wait for actuator motion completion on MachineMotion v2. ###

mm = MachineMotionV2()

# When starting a program, one must remove the software stop before moving
print("--> Removing software stop")
mm.releaseEstop()
print("--> Resetting system")
mm.resetSystem()

# Configure the actuator
axis = 1
mm.configServo(axis, MECH_GAIN.timing_belt_150mm_turn, DIRECTION.NORMAL, 5.0)

# Move the axis by 100mm
distance = 100

print("Moving %d mm!"  % distance)
mm.moveRelative(axis, distance)
print("This message gets printed immediately")
mm.waitForMotionCompletion()
print("This message gets printed once machine has finished moving")
