#!/usr/bin/python
import os, sys
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parentdir)
from _MachineMotion import *

# Define a callback to process controller gCode responses (if desired)
def templateCallback(data):
   print ( "Controller gCode responses " + data )

# Define a callback to print the data retrieved using the getData function
def printGetDataResult(data):
   print ( "--> Retrieved data = " + data )

machine_motion_example = MachineMotion(templateCallback, DEFAULT_IP_ADDRESS.usb_windows)

# Saving a string on the controller
machine_motion_example.saveData("data_1", "save_this_string_on_the_controller")

machine_motion_example.getData("data_1", printGetDataResult)