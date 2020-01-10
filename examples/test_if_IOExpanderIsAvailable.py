#!/usr/bin/python

# System imports
import sys
# Custom imports
sys.path.append("..")

from MachineMotion import *

from random import *

# Define a callback to process controller gCode responses (if desired)
def templateCallback(data):
 print ( "Controller gCode responses " + data )

mm = MachineMotion(templateCallback, "192.168.7.2")
time.sleep(1)

test0 = mm.isIoExpanderAvailable(0)
test1 = mm.isIoExpanderAvailable(1)
test2 = mm.isIoExpanderAvailable(2)
test3 = mm.isIoExpanderAvailable(3)

print("is IO Expander available: " + str(test0))
print("is IO Expander available: " + str(test1))
print("is IO Expander available: " + str(test2))
print("is IO Expander available: " + str(test3))