import sys, time
sys.path.append("../..")
from MachineMotion import *

### This Python example writes digital outputs for MachineMotion v1. ###

mm = MachineMotion()

# Detect all connected digital IO Modules
detectedIOModules = mm.detectIOModules()

# Toggles the output pins
if detectedIOModules is not None :
    for IO_Name, IO_NetworkID in detectedIOModules.items():
        writePins = [0, 1, 2, 3]
        for writePin in writePins :
            print("Pin " + str(writePin) + " on " + IO_Name + " is going to flash twice")

            mm.digitalWrite(IO_NetworkID, writePin, 1)
            time.sleep(1)
            mm.digitalWrite(IO_NetworkID, writePin, 0)
            time.sleep(1)
            mm.digitalWrite(IO_NetworkID, writePin, 1)
            time.sleep(1)
            mm.digitalWrite(IO_NetworkID, writePin, 0)
            time.sleep(1)
