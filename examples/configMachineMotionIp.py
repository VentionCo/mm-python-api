
from MachineMotion import *

#Initialize MachineMotion with default IP address
mm = MachineMotion(DEFAULT_IP_ADDRESS.usb_windows)
print("Application Message: MachineMotion Controller Connected")

#Configure machine motion with a static IP address
mode = NETWORK_MODE.static
machineIp = "192.168.0.2"
machineNetmask="255.255.255.0"
machineGateway = "192.168.0.1"
mm.configMachineMotionIp(mode, machineIp, machineNetmask, machineGateway)
print("MachineMotion configured in static mode with an ip of " + str(machineIp) +".")


#Configure MachineMotion IP to use Dynamic Host Configuration Protocol (DHCP)
mm.configMachineMotionIp(NETWORK_MODE.dhcp)
print("MachineMotion configured in DHCP mode.")

