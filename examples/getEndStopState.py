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

#Define Move Parameters
axes = [1, 2, 3]
speed = 400
acceleration = 500
direction = ["positive", "positive", "positive"]
Position500mm = [150, 150, 150]
mechGain = MECH_GAIN.timing_belt_150mm_turn

#Load Relative Move Parameters
mm.emitSpeed(speed)
mm.emitAcceleration(acceleration)

for i in axes:
    mm.configAxis(i, MICRO_STEPS.ustep_8, mechGain)

# Home Axis Before Move
print("Axis " + str(axes) + " moving home.")
mm.emitHomeAll()
mm.waitForMotionCompletion()
print("Axis " + str(axes) + " homed")

# Get End Stop State (Homed)
mm.getEndStopState()
time.sleep(5.0)

# Move 150mm
mm.emitCombinedAxisRelativeMove(axes, direction, Position500mm)
mm.waitForMotionCompletion()

# Get End Stop State (not Home)
mm.getEndStopState()
time.sleep(5.0)

mm.emitHomeAll()
mm.waitForMotionCompletion()
print("End of example")