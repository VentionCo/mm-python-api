import sys
sys.path.append("..")
from MachineMotion import *

# Define a callback to process controller gCode responses (if desired)
def templateCallback(data):
   print ( "Controller gCode responses " + data )

mm = MachineMotion(DEFAULT_IP_ADDRESS.usb_windows, gCodeCallback = templateCallback)

speed = 500      # The speed [mm/s] that all subsequent moves will move at
mm.emitSpeed(speed)
print("Global acceleration set to " + str(speed))
