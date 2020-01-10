import sys
sys.path.append("..")
from _MachineMotion import *

mm = MachineMotion(DEFAULT_IP_ADDRESS.usb_windows)

axis = AXIS_NUMBER.DRIVE1                               
mm.configAxis(axis, MICRO_STEPS.ustep_8, MECH_GAIN.timing_belt_150mm_turn)

homesTowards={
    AXIS_DIRECTION.positive: "sensor " + str(axis) + "A",
    AXIS_DIRECTION.negative: "sensor " + str(axis) + "B"
}

direction = AXIS_DIRECTION.positive 
print("Axis " + str(axis) + " is set to " + direction + " mode. It will now home towards " + homesTowards[direction] + "." )
mm.configAxisDirection(axis, direction)
mm.emitHome(axis)

mm.waitForMotionCompletion()

direction = AXIS_DIRECTION.negative 
print("Axis " + str(axis) + " is set to " + direction + " mode. It will now home towards " + homesTowards[direction] + "." )
mm.configAxisDirection(axis, direction)
mm.emitHome(axis)

mm.waitForMotionCompletion()
