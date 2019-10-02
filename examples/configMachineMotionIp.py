#!/usr/bin/python
from _MachineMotion import *

# Define a callback to process controller gCode responses (if desired)
def templateCallback(data):
   print ( "Controller gCode responses " + data )

machine_motion_example = MachineMotion(templateCallback, "192.168.7.2",)

machine_motion_example = machine_motion_example.configMachineMotionIp(NETWORK_MODE.static, "192.168.0.2", "255.255.255.0", "192.168.0.1")

print ( "--> Controller connected & ethernet interface configured (static)" )