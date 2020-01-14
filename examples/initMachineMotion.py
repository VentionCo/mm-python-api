import sys
sys.path.append("..")
from MachineMotion import *

print('Initialize MachineMotion object...')
mm = MachineMotion(DEFAULT_IP_ADDRESS.usb_windows)
print('Complete!')
