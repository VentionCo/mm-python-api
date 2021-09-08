import sys, time
sys.path.append("../..")
from MachineMotion import *

### This Python example showcases how to stop motion on MachineMotion v2. ###

mm = MachineMotionV2()

# When starting a program, one must remove the software stop before moving
print("--> Removing software stop")
mm.releaseEstop()
print("--> Resetting system")
mm.resetSystem()

# Configure the actuator
axis = 1
mm.configServo(axis, MECH_GAIN.timing_belt_150mm_turn, DIRECTION.NORMAL, 5.0)

# Configure Move Parameters
speed = 200
mm.setSpeed(speed)

# Begin Relative Move
distance = 1000
mm.moveRelative(axis, distance)
print("Axis " + str(axis) + " is moving " + str(distance) + "mm")
# This move should take 5 seconds to complete (distance/speed). Instead, we wait 2 seconds and then stop the machine.
time.sleep(2)
mm.stopAllMotion()
print("Axis " + str(axis) + " stopped.")
