#!/usr/bin/python

# System imports
import sys
# Custom imports
sys.path.append("..")

from MachineMotion import *

# Define a callback to process controller gCode responses (if desired)
def templateCallback(data):
   print ( "Controller gCode responses " + data )

machine_motion_example = MachineMotion(templateCallback, "192.168.7.2")

machine_motion_example = machine_motion_example.configMachineMotionIp(NETWORK_MODE.dhcp)

print ( "--> Controller connected & ethernet interface configured (dhcp)" )
