from _MachineMotion import *

# Define a callback to process controller gCode responses (if desired)
def templateCallback(data):
   print ( "Controller gCode responses " + data )
   
# Define a callback to invoke when a control device is attached to the controller
def attachControlDeviceCallback(data):
    print ( "Attach control device callback: " + data )  

# Define a callback to invoke when a control device is detached from the controller    
def detachControlDeviceCallback(data):
    print ( "Detach control device callback: " + data )    

# Define a callback to invoke when a control device is read    
def readControlDeviceCallback(data):
    print ( "Read control device callback: " + data )     

machine_motion_example = MachineMotion(templateCallback, DEFAULT_IP_ADDRESS.usb_windows)


# Attach a control device (in this case, and encoder) to the MachineMotion controller.
machine_motion_example.attachControlDevice("SENSOR4",CONTROL_DEVICE_TYPE.ENCODER, attachControlDeviceCallback)

count = 0

for count in range (0, 100):

    # Read the signal of a control device. SIGNAL0 of the encoder returns the relative position in turns. The encoder resets its position to 0 at power-on. Position is given in turns.
    machine_motion_example.readControlDevice("SENSOR4", "SIGNAL0", readControlDeviceCallback)

    time.sleep(1)

# Detach (deconfigure) a control device that was previously attached to the MachineMotion controller.
machine_motion_example.detachControlDevice("SENSOR4", detachControlDeviceCallback)
