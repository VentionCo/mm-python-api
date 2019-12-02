from _MachineMotion import *

mm = MachineMotion(DEFAULT_IP_ADDRESS.usb_windows)

axis = 1
direction = "reverse" 
mm.emitSetAxisDirection(axis, direction)

homesTowards={
    "normal": "sensor " + str(axis) + "A",
    "reverse": "sensor " + str(axis) + "B"
}
print("Axis " + str(axis) + " is set to " + direction + " mode. It will home towards " + homesTowards[direction] + "." )
