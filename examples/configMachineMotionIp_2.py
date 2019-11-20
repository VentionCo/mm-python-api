##################################################
## Ethernet Port Dynamic Configuration
##################################################
## Version: 2.2
## Email: info@vention.cc
## Status: tested
##################################################

enableDebug = False

from _MachineMotion import *

# Define a callback to process controller gCode responses if desired. This is mostly used for debugging purposes.
def debug(data):
    if(enableDebug): print("Debug Message: " + data + "\n")

print ("Application Message: MachineMotion Program Starting \n")

mm = MachineMotion(debug, DEFAULT_IP_ADDRESS.usb_windows)
print ("Application Message: MachineMotion Controller Connected \n")

# Setting the ETHERNET port of the controller in dhcp mode
mode = NETWORK_MODE.dhcp,
machineIp = "",
machineNetmask="",
machineGateway = ""
mm.configMachineMotionIp(NETWORK_MODE.dhcp, machineIp, machineNetmask, machineGateway)
print ("Application Message: Ethernet Port Configured \n")

print ("Application Message: Program terminating ... \n")
time.sleep(1)
sys.exit(0)
