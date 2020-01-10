#!/usr/bin/python

# System import
import sys
import time
# Custom imports
sys.path.append("..")

from MachineMotion import *

# Define a callback to process controller gCode responses (if desired)
def templateCallback(data):
   print ( "Controller gCode responses " + data )

mm = MachineMotion(None, "192.168.7.2")

mm.triggerEstop()
print("trigger eStop")
time.sleep(2)

mm.releaseEstop()
print("release eStop")
time.sleep(2)

mm.resetSystem()
print("reset System")
time.sleep(2)

print("===Test complete===")

#mm.releaseEstop()
#print("Release eStop")

#mm.resetSystem()
#print("Reset system")

