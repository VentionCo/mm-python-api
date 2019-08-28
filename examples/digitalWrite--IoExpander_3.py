#!/usr/bin/python
from _MachineMotion import *

# Define a callback to process controller gCode responses (if desired)
def templateCallback(data):
   print ( "Controller gCode responses " + data )
   
machine_motion_example = MachineMotion(templateCallback, DEFAULT_IP_ADDRESS.usb_mac_linux)

# -- Read the input on the IO Expander. --
device = 3
count = 0
state = 0
for count in range (0, 100):
    # -- Verify if the IO Expander is currently attached. --
    if ( machine_motion_example.isIoExpanderAvailable(device) == False ):
        print ( "IO Exapnder "+str(device)+" is not available!!! Please verify connection.")
    else:
        machine_motion_example.digitalWrite(device, 0, state)
        print ( "Device= "+str(device)+", pin= 0, value= " + str(state) )
        machine_motion_example.digitalWrite(device, 1, state)
        print ( "Device= "+str(device)+", pin= 1, value= " + str(state) )
        machine_motion_example.digitalWrite(device, 2, state)
        print ( "Device= "+str(device)+", pin= 2, value= " + str(state) )
        machine_motion_example.digitalWrite(device, 3, state)
        print ( "Device= "+str(device)+", pin= 3, value= " + str(state) )
    time.sleep(1)
    state = 1 if state == 0 else 0

