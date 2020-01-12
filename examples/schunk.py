import sys
sys.path.append("..")
from _MachineMotion import *

mm = MachineMotion(DEFAULT_IP_ADDRESS.usb_windows)

schunkGripper = SchunkGripper(1, mm)

for i in range (0, 100):
    schunkGripper.open()
    time.sleep(1)
    schunkGripper.close()
    time.sleep(1)
