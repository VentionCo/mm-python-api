import sys
sys.path.append("..")
from MachineMotion import *

mm = MachineMotion(DEFAULT_IP_ADDRESS.usb_windows)

#When starting a program, one must remove the software stop before moving
print("--> Removing software stop")
mm.releaseEstop()
print("--> Resetting system")
mm.resetSystem()

axis = AXIS_NUMBER.DRIVE1
mm.configAxis(axis, MICRO_STEPS.ustep_8, MECH_GAIN.timing_belt_150mm_turn)

homesTowards={
    DIRECTION.POSITIVE: "sensor " + str(axis) + "A",
    DIRECTION.NEGATIVE: "sensor " + str(axis) + "B"
}

direction = DIRECTION.POSITIVE
print("Axis " + str(axis) + " is set to " + direction + " mode. It will now home towards " + homesTowards[direction] + "." )
mm.configAxisDirection(axis, direction)
mm.emitHome(axis)

mm.waitForMotionCompletion()

direction = DIRECTION.NEGATIVE
print("Axis " + str(axis) + " is set to " + direction + " mode. It will now home towards " + homesTowards[direction] + "." )
mm.configAxisDirection(axis, direction)
mm.emitHome(axis)

mm.waitForMotionCompletion()
