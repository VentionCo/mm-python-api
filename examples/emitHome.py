from _MachineMotion import *

mm = MachineMotion(DEFAULT_IP_ADDRESS.usb_windows)
axis = AXIS_NUMBER.DRIVE1

mm.emitHome(axis)
print ("Application Message: Axis "+ str(axis) +" is going home")
mm.waitForMotionCompletion()
print("Application Message: Axis "+ str(axis) +" is at home")

