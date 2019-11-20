##################################################
## Ethernet Port Dynamic Configuration
##################################################
## Version: 2.2
## Email: info@vention.cc
## Status: tested
##################################################

import os, sys
import configWizard
#Adds mm-python-api to the sys path so that we can access MachineMotion.py 
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parentdir)
from _MachineMotion import *

enableDebug = False
# Define a callback to process controller gCode responses if desired. This is mostly used for debugging purposes.
def debug(data):
    if(enableDebug): print("Debug Message: " + data + "\n")



print ("Application Message: MachineMotion Program Starting \n")
mm = MachineMotion(debug, DEFAULT_IP_ADDRESS.usb_windows)
print("Application Message: MachineMotion Controller Connected \n")

cw = configWizard.configWizard()

question = "Select either static or dhcp ethernet configuration:"
valid = {"static" : NETWORK_MODE.static,"dhcp" : NETWORK_MODE.dhcp}
mode = cw.askMultipleChoice(question, valid)

if mode ==NETWORK_MODE.static:
    machineIp = "192.168.0.2"
    machineNetmask="255.255.255.0"
    machineGateway = "192.168.0.1"
    mm.configMachineMotionIp(mode, machineIp, machineNetmask, machineGateway)
    cw.write("Application Message: Ethernet Port Configured in Static mode")

if  mode == NETWORK_MODE.dhcp:
    # Setting the ETHERNET port of the controller in dhcp mode
    mm.configMachineMotionIp(NETWORK_MODE.dhcp)
    cw.write("Application Message: Ethernet Port Configured in DHCP mode")

cw.write("Application Message: Program terminating ... \n")
time.sleep(1)
sys.exit(0)
