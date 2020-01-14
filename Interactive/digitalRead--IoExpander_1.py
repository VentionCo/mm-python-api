
##################################################
## digitalRead--IoExpander
##################################################
## Version: 1.6.8
## Email: info@vention.cc
## Status: tested
##################################################

import os, sys
import configWizard
#Adds mm-python-api to the sys path so that we can access MachineMotion.py 
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parentdir)
from _MachineMotion import *

# Define a callback to process controller gCode responses (if desired)
def templateCallback(data):
   print ( "Controller gCode responses " + data )
   
mm = MachineMotion(templateCallback, DEFAULT_IP_ADDRESS.usb_windows)

cw = configWizard.configWizard()
#Ask user to select/confirm how many IO expanders have been found
#See what sensors exist:
ioModulesFound = False
foundIOModules = {}
numIOModules = 0
while ioModulesFound == False:
    for ioDeviceID in range(1,3):
        if mm.isIoExpanderAvailable(ioDeviceID):
            foundIOModules["IO Network Id " + str(ioDeviceID)] = ioDeviceID
            numIOModules = numIOModules + 1

    if numIOModules == 0:
        cw.write("No IO devices found. Please ensure the IO modules are plugged into machine motion, then hit any key to continue.")
    else:
        if cw.askYesNo(str(numIOModules) + " device(s) detected. Is this correct?"):
            ioModulesFound = True
        else:
            cw.write("Please verify your connections. IO modules can be plugged into any port (AUX1, AUX2, AUX3), and the IO module id is printed on the box.")
            cw.write("Press enter continue")
            numIOModules = 0
            cw.getUserInput()


testAnotherIO = True

while testAnotherIO == True:
    if numIOModules > 1:
        selectedIODevice = cw.askMultipleChoice("Which IO expander would you like to read/write from?", foundIOModules)
    else:
        selectedIODevice = list(foundIOModules)[0]
        
    
    validPins = {"Pin 1":0, "Pin 2":1, "Pin 3":2, "Pin 4":3}
    selectedPin = cw.askMultipleChoice("Please select a pin to read or write to.", validPins)

    pinActions = {"Read":"R", "Write High":"WH", "Write Low":"WL"}
    action = cw.askMultipleChoice("What action would you like to perform on pin " + str(selectedPin), pinActions)

    if(action == "R"):
        value= mm.digitalRead(selectedIODevice, selectedPin)
        cw.write("Pin " + str(selectedPin) + " on Digital IO #" + str(selectedIODevice) + " has value: " + str(value))
    elif(action == "WH"):
        mm.digitalWrite(selectedIODevice, selectedPin, 1)
        cw.write("Pin " + str(selectedPin) + " on Digital IO #" + str(selectedIODevice) + " was set to HIGH (24V)")
    elif(action == "WL"):
        mm.digitalWrite(selectedIODevice, selectedPin, 0)
        cw.write("Pin " + str(selectedPin) + " on Digital IO #" + str(selectedIODevice) + " was set to LOW (0V)")


    if cw.askYesNo("Would you like to test another pin?"):
        pass
    else:
        testAnotherIO = False

cw.quitCW()








# if 1 - select that one
    #if 2 - ask which expander to select

# Type R1 to read from input 1 and W1 to write to output 1
    #Output - Device ID - X - input from pin X - pin X set to Y


# -- Read the input on the IO Expander. --
device = 1
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

