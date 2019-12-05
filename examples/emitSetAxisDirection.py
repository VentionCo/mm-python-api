from _MachineMotion import *

mm = MachineMotion(DEFAULT_IP_ADDRESS.usb_windows)

axis = AXIS_NUMBER.DRIVE3                               
mm.configAxis(axis, MICRO_STEPS.ustep_8, MECH_GAIN.timing_belt_150mm_turn)

homesTowards={
    "normal": "sensor " + str(axis) + "A",
    "reverse": "sensor " + str(axis) + "B"
}

direction = "normal" 
print("Axis " + str(axis) + " is set to " + direction + " mode. It will now home towards " + homesTowards[direction] + "." )
mm.emitSetAxisDirection(axis, direction)
mm.emitHome(axis)
mm.waitForMotionCompletion()


direction = "reverse" 
print("Axis " + str(axis) + " is set to " + direction + " mode. It will now home towards " + homesTowards[direction] + "." )
mm.emitSetAxisDirection(axis, direction)
mm.emitHome(axis)
