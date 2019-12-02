from _MachineMotion import *

mm = MachineMotion(DEFAULT_IP_ADDRESS.usb_windows)
mm.emitHome(1)

# Move the axis one to position 100 mm
mm.emitAbsoluteMove(1, 100)
print("This message gets printed immediately")
mm.waitForMotionCompletion()
print("This message gets printed once machine is finished moving")

