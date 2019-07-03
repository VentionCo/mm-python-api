from _MachineMotion_v1_6_5 import *

# Define a callback to process controller gCode responses (if desired)
def templateCallback(data):
   print "Controller gCode responses " + data

machine_motion_example = MachineMotion(templateCallback, DEFAULT_IP_ADDRESS.usb_windows)

# Homing axis one
machine_motion_example.emitHome(1)
machine_motion_example.waitForMotionCompletion()

print "--> Axis 1 is now at home position."