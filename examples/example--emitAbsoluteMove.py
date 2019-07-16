from _MachineMotion import *

# Define a callback to process controller gCode responses (if desired)
def templateCallback(data):
   print ( "Controller gCode responses " + data )

machine_motion_example = MachineMotion(templateCallback, DEFAULT_IP_ADDRESS.usb_windows)

# Configuring the travel speed to 10 000 mm / min
machine_motion_example.emitSpeed(10000)

# Configuring the travel speed to 1000 mm / second^2
machine_motion_example.emitAcceleration(1000)

# Homing axis one
machine_motion_example.emitHome(1)

# Move the axis one to position 100 mm
machine_motion_example.emitAbsoluteMove(1, 100)

print ( "--> Example completed." )