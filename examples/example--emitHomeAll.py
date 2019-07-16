from _MachineMotion import *

# Define a callback to process controller gCode responses (if desired)
def templateCallback(data):
   print "Controller gCode responses " + data

machine_motion_example = MachineMotion(templateCallback, DEFAULT_IP_ADDRESS.usb_windows)

# Homing all the axes of the controller sequentially
machine_motion_example.emitHomeAll()

print "--> All Axes are now at home position."