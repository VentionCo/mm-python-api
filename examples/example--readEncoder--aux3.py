from _MachineMotion import *

# Define a callback to process controller gCode responses (if desired)
def templateCallback(data):
   print ( "Controller gCode responses " + data )
   
machine_motion_example = MachineMotion(templateCallback, DEFAULT_IP_ADDRESS.usb_mac_linux)

# -- Read the input on the IO Expander. --
device = 2
count = 0
for count in range (0, 400):
    # -- Verify if the IO Expander is currently attached. --
    position= machine_motion_example.getEncoderRealtimePosition(device)
    print ( "Encoder= "+str(device)+", realtimePosition= " + str(position) )
    time.sleep(0.25)

