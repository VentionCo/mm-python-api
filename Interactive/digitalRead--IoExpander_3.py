#!/usr/bin/python
from _MachineMotion import *

# Define a callback to process controller gCode responses (if desired)
def templateCallback(data):
   print ( "Controller gCode responses " + data )
   
machine_motion_example = MachineMotion(templateCallback, DEFAULT_IP_ADDRESS.usb_mac_linux)

# -- Read the input on the IO Expander. --
device = 3
count = 0
for count in range (0, 100):
    # -- Verify if the IO Expander is currently attached. --
    if ( machine_motion_example.isIoExpanderAvailable(device) == False ):
        print ( "IO Exapnder "+str(device)+" is not available!!! Please verify connection.")
    else:
        value= machine_motion_example.digitalRead(device, 0)
        print ( "Device= "+str(device)+", pin= 0, value= " + str(value) )
        value= machine_motion_example.digitalRead(device, 1)
        print ( "Device= "+str(device)+", pin= 1, value= " + str(value) )
        value= machine_motion_example.digitalRead(device, 2)
        print ( "Device= "+str(device)+", pin= 2, value= " + str(value) )
        value= machine_motion_example.digitalRead(device, 3)
        print ( "Device= "+str(device)+", pin= 3, value= " + str(value) )
    time.sleep(1)

