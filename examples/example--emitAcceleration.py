from _MachineMotion import *

# Define a callback to process controller gCode responses (if desired)
def templateCallback(data):
   print ( "Controller gCode responses " + data )

machine_motion_example = MachineMotion(templateCallback, DEFAULT_IP_ADDRESS.usb_windows)

# Configuring the travel speed to 1000 mm / second^2
machine_motion_example.emitAcceleration(1000)

print ( "--> Machine moves are now set to accelerate @ 1000 mm / second^2" )