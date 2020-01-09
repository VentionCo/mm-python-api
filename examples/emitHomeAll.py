import sys
sys.path.append("..")
from MachineMotion import *

mm = MachineMotion(DEFAULT_IP_ADDRESS.usb_windows)

# Home All Axes Sequentially
mm.emitHomeAll()
print ("All Axes Moving Home")
mm.waitForMotionCompletion()
print("All Axes Homed")