import sys
sys.path.append("..")
from MachineMotion import *

# Initialize the key-value pair to save on the controller
dataKey = "example_key"
dataContent = "save_this_string_on_the_controller"

def templateCallback(data) :
	print("Data: '" + str(data) + "' retrieved from controller using key '" + dataKey + "'")

	return

mm = MachineMotion(DEFAULT_IP_ADDRESS.usb_windows)

# Saving a string on the controller
mm.saveData(dataKey, dataContent)
print("Data: '" + dataContent + "' saved on controller under key '" + dataKey + "'")

# Retreiving data from the controller
retrievedData = mm.getData(dataKey, templateCallback)
