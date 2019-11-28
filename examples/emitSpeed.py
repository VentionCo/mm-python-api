from _MachineMotion import *

# Define a callback to process controller gCode responses if desired. This is mostly used for debugging purposes.
enableDebug = False
def debug(data):
    if(enableDebug): print("Debug Message: " + data)

mm = MachineMotion(debug, DEFAULT_IP_ADDRESS.usb_windows)
speed = 500      # The speed [mm/s] that all subsequent moves will move at 
mm.emitSpeed(acceleration)
print("Global acceleration set to " + str(acceleration))


