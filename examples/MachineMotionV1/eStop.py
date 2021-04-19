#!/usr/bin/python
import sys, time
sys.path.append("../..")
from MachineMotion import *

### This Python example showcases how to control eStop on MachineMotion v1. ###

# Define a callback to process estop status
def templateCallback(estop_status):
    print("eStop status is : " + str(estop_status))
    if estop_status == True :
        print("MachineMotion is in estop state.")
    elif estop_status == False :
        print("MachineMotion is not in estop state.") 

# Create MachineMotion instance
mm = MachineMotion()
time.sleep(0.1) # Wait to initialize internal eStop topics.

mm.bindeStopEvent(templateCallback)

result = mm.triggerEstop()
if result == True   : print("--> Software stop triggered")
else                : print("--> Failed to trigger software stop")

time.sleep(3.0)

result = mm.releaseEstop()
if result == True   : print("--> Software stop released")
else                : print("--> Failed to release software stop")

time.sleep(3.0)

result = mm.resetSystem()
if result == True   : print("--> System has been reset")
else                : print("--> Failed to reset system")

print("--> Example completed")
