from _MachineMotion import *

# Define a callback to process controller gCode responses (if desired)
enableDebug = False
def debug(data):
    if(enableDebug): print("Debug Message: " + data)
mm = MachineMotion(debug, DEFAULT_IP_ADDRESS.usb_windows)

# Initialize the key-value pair to save on the controller
dataKey = "example_key"
dataContent = "save_this_string_on_the_controller"

# Saving a string on the controller
mm.saveData(dataKey, dataContent)
print("Data: '" + dataContent + "' saved on controller under key '" + dataKey + "'")

# Retreiving data from the controller
retrievedData = mm.getData(dataKey)
print("Data: '" + retrievedData + "' retrieved from controller using key '" + dataKey + "'")

