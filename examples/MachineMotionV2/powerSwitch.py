import sys
import time
sys.path.append("../..")
from MachineMotion import *

### This Python example control a power switch module on MachineMotion v2. ###

mm = MachineMotionV2()

deviceNetworkId = 7

### Set the power switch
print("--> Turning power switch on")
mm.setPowerSwitch(deviceNetworkId, POWER_SWITCH.ON)
time.sleep(3)
print("--> Turning power switch off")
mm.setPowerSwitch(deviceNetworkId, POWER_SWITCH.OFF)
time.sleep(3)

print("--> Example Complete")
