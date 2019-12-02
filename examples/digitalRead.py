
from _MachineMotion import *
   
mm = MachineMotion(DEFAULT_IP_ADDRESS.usb_windows)

#Reads and Prints all input values on all connected digital IO Modules
detectedIOModules = mm.detectIOModules()
for IO_Name, IO_NetworkID in detectedIOModules.items():
    readPins =[1,2,3,4]
    for readPin in readPins:
        pinValue = mm.digitalRead(IO_NetworkID, readPin)
        print("Pin "+ str(readPin) + " on " + IO_Name + " has value " + str(pinValue))
  

