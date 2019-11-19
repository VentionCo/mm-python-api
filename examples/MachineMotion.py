##################################################
## MachineMotion Object Constructor Example
##################################################
## Version: 1.6.8
## Email: info@vention.cc
## Status: tested
##################################################

# Define a callback to process controller gCode responses (if desired)
def templateCallback(data):
   print ( "Controller gCode responses " + data )

from _MachineMotion import *

# Define a callback to process controller gCode responses if desired. This is mostly used for debugging purposes.
def debug(data):
    if(enableDebug): print("Debug Message: " + data + "\n")

print ("Application Message: MachineMotion Program Starting \n")

mm = MachineMotion(debug, DEFAULT_IP_ADDRESS.usb_windows)
print ("Application Message: MachineMotion Controller Connected \n")

print ("Application Message: Program terminating ... \n")
time.sleep(1)
sys.exit(0)
