
from _MachineMotion import *

# Define a callback to process controller gCode responses (if desired)
def templateCallback(data):
   print ( "Controller gCode responses " + data )
   
mm = MachineMotion(templateCallback, DEFAULT_IP_ADDRESS.usb_windows)

# Toggles the output pins on all connected IO Modules
detectedIOModules = mm.detectIOModules()
for IO_Name, IO_NetworkID in detectedIOModules:
    for writePin in range(0,3):
        print("Pin "+ str(writePin) + " on " + IO_Name + " is going to flash twice")
        
        pinValue = mm.digitalWrite(IO_NetworkID, writePin, 1)
        time.sleep(1)
        pinValue = mm.digitalWrite(IO_NetworkID, writePin, 0)
        time.sleep(1)
        pinValue = mm.digitalWrite(IO_NetworkID, writePin, 1)
        time.sleep(1)
        pinValue = mm.digitalWrite(IO_NetworkID, writePin, 0)
  

