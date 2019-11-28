
from _MachineMotion import *

# Define a callback to process controller gCode responses (if desired)
def templateCallback(data):
   print ( "Controller gCode responses " + data )
   
mm = MachineMotion(templateCallback, DEFAULT_IP_ADDRESS.usb_windows)

#Reads and Prints all input values on all connected digital IO Modules
detectedIOModules = mm.detectIOModules()
for IO_Name, IO_NetworkID in detectedIOModules:
    for readPin in range(0,3):
        pinValue = mm.digitalRead(IO_NetworkID, readPin)
        print("Pin "+ str(readPin) + " on " + IO_Name + " has value " + str(pinValue))
  

