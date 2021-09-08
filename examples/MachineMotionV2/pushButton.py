import sys
import time
sys.path.append("../..")
from MachineMotion import *

### This Python example showcases different uses for a push button module on MachineMotion v2. ###
mm = MachineMotionV2()

### Define the module and button you would like to monitor.
deviceNetworkId = 5
blackButton = PUSH_BUTTON.COLOR.BLACK
whiteButton = PUSH_BUTTON.COLOR.WHITE

### Block the script until a button is pushed:
print("--> Waiting 5 seconds for the white button to be pushed!")
buttonWasPushed = mm.waitOnPushButton(deviceNetworkId, whiteButton, PUSH_BUTTON.STATE.PUSHED, 5)
if buttonWasPushed:
    print("--> White button was pushed!")
else:
    print("--> waitOnPushButton timed out!")
    
time.sleep(1)

### Manually read the state of a push button
buttonState = mm.readPushButton(deviceNetworkId, whiteButton)
print("--> Reading from white push button: " + buttonState)
time.sleep(2)

### Define a callback to process push button status
def templateCallback(button_state):
    print("--> templateCallback: Black push button on module: " + str(deviceNetworkId) + " has changed state.")      
    if button_state == PUSH_BUTTON.STATE.PUSHED :      
        print("--> Black push button has been pushed.")
    elif button_state == PUSH_BUTTON.STATE.RELEASED :
        print("--> Black push button has been released.")

###  You must first bind the callback function!
mm.bindPushButtonEvent(deviceNetworkId, blackButton, templateCallback)

print("--> Push the black button to trigger event! Press ctrl-c to exit")

while True:
    time.sleep(0.5)
