from _MachineMotion import *

# Define a callback to process controller gCode responses (if desired)
def motionControllerMessagesCallback(data):
   print "Controller gCode responses " + data

def unusedCallback(data):
    pass

# Define a callback to invoke when a control device is read    
def writeControlCallback(data):
    print "Read control device callback: " + data      

machine_motion_example = MachineMotion(motionControllerMessagesCallback, DEFAULT_IP_ADDRESS.usb_windows)

# Attach a control device (in this case, and encoder) to the MachineMotion controller.
machine_motion_example.attachControlDevice("SENSOR5",CONTROL_DEVICE_TYPE.IO_EXPANDER_GENERIC, unusedCallback)

count = 0

for count in range (0, 100):

    # Read the signal of a control device. SIGNAL0 of the encoder returns the relative position in turns. The encoder resets its position to 0 at power-on. Position is given in turns.
    machine_motion_example.writeControlDevice("SENSOR5", "SIGNAL0", False, writeControlCallback)
    # Read the signal of a control device. SIGNAL0 of the encoder returns the relative position in turns. The encoder resets its position to 0 at power-on. Position is given in turns.
    machine_motion_example.writeControlDevice("SENSOR5", "SIGNAL1", False, writeControlCallback)
    # Read the signal of a control device. SIGNAL0 of the encoder returns the relative position in turns. The encoder resets its position to 0 at power-on. Position is given in turns.
    machine_motion_example.writeControlDevice("SENSOR5", "SIGNAL2", False, writeControlCallback)

    time.sleep(1)

    # Read the signal of a control device. SIGNAL0 of the encoder returns the relative position in turns. The encoder resets its position to 0 at power-on. Position is given in turns.
    machine_motion_example.writeControlDevice("SENSOR5", "SIGNAL0", True, writeControlCallback)
    # Read the signal of a control device. SIGNAL0 of the encoder returns the relative position in turns. The encoder resets its position to 0 at power-on. Position is given in turns.
    machine_motion_example.writeControlDevice("SENSOR5", "SIGNAL1", True, writeControlCallback)
    # Read the signal of a control device. SIGNAL0 of the encoder returns the relative position in turns. The encoder resets its position to 0 at power-on. Position is given in turns.
    machine_motion_example.writeControlDevice("SENSOR5", "SIGNAL2", True, writeControlCallback)

    time.sleep(1)

# Detach (deconfigure) a control device that was previously attached to the MachineMotion controller.
machine_motion_example.detachControlDevice("SENSOR5", unusedCallback)

