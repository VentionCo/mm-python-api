#!/usr/bin/python

# System imports
import sys
# Custom imports
sys.path.append("..")

import time

from MachineMotion import *

# Create MachineMotion instance
mm = MachineMotion("192.168.7.2", None)

mm.triggerEstop()
print("--> eStop triggered")
time.sleep(3.0)

mm.releaseEstop()
print("--> eStop released")
time.sleep(3.0)

mm.resetSystem()
print("--> System resetted")

print("--> Example completed")
