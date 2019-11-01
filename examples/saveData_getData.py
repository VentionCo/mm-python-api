##################################################
## Save Data, Get Data Example
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
    
# Define a callback to print the data retrieved using the getData function
def printGetDataResult(data):

    dictionary = json.loads(data)

    print ( "Application Message: Retrieved file name = " + dictionary["fileName"] + "\n" )
    
    print ( "Application Message: Retrieved data = " + dictionary["data"]  + "\n")

mm = MachineMotion(debug, DEFAULT_IP_ADDRESS.usb_windows)
print ("Application Message: MachineMotion Controller Connected \n")

# Saving a string on the controller
mm.saveData("data_1", "save_this_string_on_the_controller")

print ("Application Message: Data saved \n")

# Reading a string from the controller
mm.getData("data_1", printGetDataResult)

print ("Application Message: Program terminating ... \n")
time.sleep(1)
sys.exit(0)


