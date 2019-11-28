from _MachineMotion import *

# Define a callback to process controller gCode responses if desired. This is mostly used for debugging purposes.
enableDebug = True
def debug(data):
    if(enableDebug): print("Debug Message: " + data + "\n")

mm = MachineMotion(debug, DEFAULT_IP_ADDRESS.usb_windows)

