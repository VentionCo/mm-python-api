import os, sys
sys.path.append(os.path.abspath(__file__ + "/../../"))
from MachineMotion import *

print('Initialize MachineMotion object...')
mm = MachineMotion(DEFAULT_IP_ADDRESS.usb_windows)
print('Complete!')
