##################################################
## Encoder Control Example
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
    
print ("Application Message: MachineMotion Program Starting \n")

# Creating a MachineMotion instance
mm = MachineMotion(debug, DEFAULT_IP_ADDRESS.usb_windows)
print ("Application Message: MachineMotion Controller Connected \n")

# Attach a control device (in this case an encoder) to the MachineMotion controller.
# Encoder connected to port "SENSOR4" (now labelled "AUX1" on new controllers)
mm.attachControlDevice("SENSOR4",CONTROL_DEVICE_TYPE.ENCODER, attachCallback)
print ("Application Message: Encoder attached \n")

def readPosition():
    # SIGNAL0 corresponds to the number of rotations
    mm.readControlDevice("SENSOR4", "SIGNAL0", readCallback)
    time.sleep(0.1)

# Configuring the travel speed to 600 mm / min
mm.emitSpeed(600)
print ("Application Message: Speed configured \n")

# Configuring the travel speed to 250 mm / second^2
mm.emitAcceleration(250)
print ("Application Message: Acceleration configured \n")

# Homing axis 1
mm.emitHome(1)
print ("Application Message: Axis 1 at home \n")

time.sleep(0.5)

readPosition()

# Move the axis one to position 100 mm
mm.emitRelativeMove(1, "positive", 100)
print ("Application Message: Move on-going ... \n")

count = 0

for count in range (0, 10):

    readPosition()
    
    time.sleep(1)

# Detach (deconfigure) a control device that was previously attached to the MachineMotion controller.
mm.detachControlDevice("SENSOR4", detachCallback)

time.sleep(1)

sys.exit(0)
