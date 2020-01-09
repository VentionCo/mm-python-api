import sys
sys.path.append("..")
from _MachineMotion import *
   
mm = MachineMotion(DEFAULT_IP_ADDRESS.usb_windows)

#Reads and Prints all input values on all connected digital IO Modules
detectedIOModules = mm.detectIOModules()
for IO_Name, IO_NetworkID in detectedIOModules.items():
    readPins ={"Pin 1":0, "Pin 2":1, "Pin 3": 2, "Pin 4":3}
    for readPin in readPins.keys():
        pinValue = mm.digitalRead(IO_NetworkID, readPins[readPin])
        print(readPin + " on " + IO_Name + " has value " + str(pinValue))
  

