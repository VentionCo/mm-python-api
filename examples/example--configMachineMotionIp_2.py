##################################################
## Ethernet Port Dynamic Configuration
##################################################
## Author: Francois Giguere
## Version: 1.6.8
## Email: info@vention.cc
## Status: tested
##################################################

from _MachineMotion_1_6_8 import *

# Define a callback to process controller gCode responses if desired. This is mostly used for debugging purposes.
def debug(data):
    pass

print ("Application Message: MachineMotion Program Starting \n")

# TODO: Uncomment the appropriate default static IP Address
#ip_address = DEFAULT_IP_ADDRESS.usb_windows 
#ip_address = DEFAULT_IP_ADDRESS.usb_mac_linux
#ip_address = DEFAULT_IP_ADDRESS.ethernet

mm = MachineMotion(debug, ip_address)
print ("Application Message: MachineMotion Controller Connected \n")

# Setting the ETHERNET port of the controller in dhcp mode
mm.configMachineMotionIp(NETWORK_MODE.dhcp, "", "", "")
print ("Application Message: Ethernet Port Configured \n")

print ("Application Message: Program terminating ... \n")
time.sleep(1)
sys.exit(0)

#Having Issues? Please ensure that your computer is configured in 