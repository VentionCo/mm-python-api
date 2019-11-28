from _MachineMotion import *

# Define a callback to process controller gCode responses if desired. This is mostly used for debugging purposes.
enableDebug = False
def debug(data):
    if(enableDebug): print("Debug Message: " + data + "\n")
mm = MachineMotion(debug, DEFAULT_IP_ADDRESS.usb_windows)

axis = 1
direction = "reverse" 
mm.emitSetAxisDirection(axis, direction)

homesTowards={
    "normal": "sensor " + str(axis) + "A",
    "reverse": "sensor " + str(axis) + "B"
}
print("Axis " + str(axis) + " is set to " + direction " mode. It will home towards " + homesTowards[direction] + "." )
