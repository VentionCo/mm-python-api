import sys
sys.path.append("..")
from MachineMotion import *

# Define a callback to process controller gCode responses (if desired)
def templateCallback(data):
   print ( "Controller gCode responses " + data )

mm = MachineMotion(DEFAULT_IP_ADDRESS.usb_windows, gCodeCallback = templateCallback)

acceleration = 500      # The acceleration [mm/s^2] that all subsequent moves will move at
mm.emitAcceleration(acceleration)
print("Global acceleration set to " + str(acceleration))
