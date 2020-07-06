# Testing the speed functions on Marlin using gCode and thin client
# System imports
import sys
import random
import time

# Custom imports
sys.path.append("..")
from MachineMotion import *

m1 = MachineMotion("192.168.7.2", None)

m1.configAxisDirection(AXIS_NUMBER.DRIVE3, DIRECTION.NORMAL)
m1.configAxis(AXIS_NUMBER.DRIVE3, MICRO_STEPS.ustep_8, MECH_GAIN.legacy_timing_belt_200_mm_turn)

m1.releaseEstop()
m1.resetSystem()

time.sleep(2.0)

move = 42000.0
speed = 500

m1.emitSpeed(500)
m1.emitAcceleration(500)

print("Expecting a duration of : " + str(move/speed) + " seconds.")
start_time = time.gmtime()

m1.emitRelativeMove(3, DIRECTION.NORMAL, move)

m1.waitForMotionCompletion()

end_time = time.gmtime()

duration = end_time - start_time

print("Command took : " + time.strftime("%Y-%m-%d %H:%M:%S", duration) + " to complete.")
