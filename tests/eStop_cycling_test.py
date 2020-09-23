# System imports
import sys
# Custom imports
sys.path.append("../mm-python-api")

import random
from MachineMotion import *

cycle_counter = 0

mm = MachineMotion(DEFAULT_IP_ADDRESS.usb_windows)


#Trying to trigger many time release eStop after trigger event
print("--> Trying to release many times eStop after trigger event <--")
mm.triggerEstop()
print("--> eStop triggered")

for i in range(10) :
    mm.releaseEstop()
    print("--> eStop released")

if mm.resetSystem() :
    print("--> System resetted")
else :
    print("--> Failed to reset system")

# While system is alive, try releasing estop many times.
print("--> Trying to release many times eStop while system is alive <--")

for i in range(20) :
    mm.releaseEstop()
    print("--> eStop released")
