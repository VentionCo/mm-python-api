from _MachineMotion import *

mm = MachineMotion(DEFAULT_IP_ADDRESS.usb_windows)
speed = 500      # The speed [mm/s] that all subsequent moves will move at 
mm.emitSpeed(speed)
print("Global acceleration set to " + str(speed))


