
from _MachineMotion import *
   
mm = MachineMotion(DEFAULT_IP_ADDRESS.usb_windows)

# Toggles the output pins on all connected IO Modules
detectedIOModules = mm.detectIOModules()
for IO_Name, IO_NetworkID in detectedIOModules.items():
    writePins = [1,2,3,4]
    for writePin in writePins:
        print("Pin "+ str(writePin) + " on " + IO_Name + " is going to flash twice")
        
        mm.digitalWrite(IO_NetworkID, writePin, 1)
        time.sleep(1)
        mm.digitalWrite(IO_NetworkID, writePin, 0)
        time.sleep(1)
        mm.digitalWrite(IO_NetworkID, writePin, 1)
        time.sleep(1)
        mm.digitalWrite(IO_NetworkID, writePin, 0)

  

