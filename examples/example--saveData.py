from _MachineMotion import *

# Define a callback to process controller gCode responses (if desired)
def templateCallback(data):
   print ( "Controller gCode responses " + data )

machine_motion_example = MachineMotion(templateCallback, DEFAULT_IP_ADDRESS.usb_windows)

# Saving a string on the controller
machine_motion_example = machine_motion_example.saveData("data_1", "save_this_string_on_the_controller")

print ( "--> Data sent on controller" )