import os, sys
sys.path.append(os.path.abspath(__file__ + "/../../"))
from MachineMotion import *

mm = MachineMotion(DEFAULT_IP_ADDRESS.usb_windows)

#When starting a program, one must remove the software stop before moving
print("--> Removing software stop")
mm.releaseEstop()
print("--> Resetting system")
mm.resetSystem()


states = mm.getEndStopState()
axis = 1
mm.configAxisDirection(axis, "positive")
homeSensor = states[axis]["home"]
endSensor = states[axis]["end"]
print("Axis " + str(axis) + " home sensor is " + homeSensor)
print("Axis " + str(axis) + " end sensor is " + endSensor)
