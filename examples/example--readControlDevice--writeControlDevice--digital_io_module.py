##################################################
## Digital IO Module Contro Example
##################################################
## Author: Francois Giguere
## Version: 1.6.8
## Email: info@vention.cc
## Status: tested
##################################################

enableDebug = False

from _MachineMotion_1_6_8 import *

# Define a callback to process controller gCode responses if desired. This is mostly used for debugging purposes.
def debug(data):
    if(enableDebug): print("Debug Message: " + data + "\n")
   
# Define a callback to invoke when a control device is attached to the controller
def attachCallback(data):
    print ("Application Message: attachCallback invoked. Message received = " + json.loads(data)["message"] + " \n");

# Define a callback to invoke when a control device is detached from the controller    
def detachCallback(data):
    print ("Application Message: detachCallback invoked. Message received = " + json.loads(data)["message"] + " \n");

# Define a callback to invoke when a control device is read    
def readCallback(data):    
    print ( "Application Message: readCallback invoked. Message received = " + data + " \n" )

# Define a callback to invoke when a control device is written    
def writeCallback(data):
    print ( "Application Message: writeCallback invoked. Message received = " + data + " \n" )

print ("Application Message: MachineMotion Program Starting \n")

# Creating a MachineMotion instance
mm = MachineMotion(debug, DEFAULT_IP_ADDRESS.usb_windows)
print ("Application Message: MachineMotion Controller Connected \n")

# Attach a control device (in this case a digital IO module) to the MachineMotion controller
# Digital IO Module connected to port "SENSOR4" which corresponds to address 1
mm.attachControlDevice("SENSOR4",CONTROL_DEVICE_TYPE.IO_EXPANDER_GENERIC, attachCallback)
print ("Application Message: Digital IO Module configured \n")

count = 0

def readInputs():
    # Read a control device (in this case a digital IO module)
    # Port "SENSOR4" corresponds to address 1
    # SIGNAL4 corresponds to INPUT1
    mm.readControlDevice("SENSOR4", "SIGNAL4", readCallback)
    time.sleep(0.1)

    # SIGNAL5 corresponds to INPUT2
    mm.readControlDevice("SENSOR4", "SIGNAL5", readCallback)
    time.sleep(0.1)

    # SIGNAL6 corresponds to INPUT3
    mm.readControlDevice("SENSOR4", "SIGNAL6", readCallback)
    time.sleep(0.1)
    
    # SIGNAL7 corresponds to INPUT4
    mm.readControlDevice("SENSOR4", "SIGNAL7", readCallback)
    time.sleep(0.1)

def readOutputs():
    # Read a control device (in this case a digital IO module)
    # Port "SENSOR4" corresponds to address 1
    # SIGNAL4 corresponds to INPUT1
    mm.readControlDevice("SENSOR4", "SIGNAL0", readCallback)
    time.sleep(0.1)

    # SIGNAL5 corresponds to INPUT2
    mm.readControlDevice("SENSOR4", "SIGNAL1", readCallback)
    time.sleep(0.1)

    # SIGNAL6 corresponds to INPUT3
    mm.readControlDevice("SENSOR4", "SIGNAL2", readCallback)
    time.sleep(0.1)
    
    # SIGNAL7 corresponds to INPUT4
    mm.readControlDevice("SENSOR4", "SIGNAL3", readCallback)
    time.sleep(0.1)

def writeOutputs():

    # SIGNAL0 corresponds to OUTPUT1
    mm.writeControlDevice("SENSOR4", "SIGNAL0", False, writeCallback)
    
    # SIGNAL1 corresponds to OUTPUT2
    mm.writeControlDevice("SENSOR4", "SIGNAL1", False, writeCallback)
    
    # SIGNAL2 corresponds to OUTPUT3
    mm.writeControlDevice("SENSOR4", "SIGNAL2", False, writeCallback)
    
    # SIGNAL3 corresponds to OUTPUT4
    mm.writeControlDevice("SENSOR4", "SIGNAL3", False, writeCallback)
    
    time.sleep(1)
    
    # SIGNAL0 corresponds to OUTPUT1
    mm.writeControlDevice("SENSOR4", "SIGNAL0", True, writeCallback)
    
    # SIGNAL1 corresponds to OUTPUT2
    mm.writeControlDevice("SENSOR4", "SIGNAL1", True, writeCallback)
    
    # SIGNAL2 corresponds to OUTPUT3
    mm.writeControlDevice("SENSOR4", "SIGNAL2", True, writeCallback)
    
    # SIGNAL3 corresponds to OUTPUT4
    mm.writeControlDevice("SENSOR4", "SIGNAL3", True, writeCallback)

for count in range (0, 5):

    readInputs()
    
    time.sleep(1)
    
    readOutputs()
    
    time.sleep(1)
    
    writeOutputs()
    
    time.sleep(1)

# Detach (deconfigure) a control device that was previously attached to the MachineMotion controller.
mm.detachControlDevice("SENSOR4", detachCallback)

print ("Application Message: Program terminating ... \n")
time.sleep(1)
sys.exit(0)
