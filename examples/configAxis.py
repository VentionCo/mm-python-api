#!/usr/bin/python

# System imports
import sys
# Custom imports
sys.path.append("..")

from MachineMotion import *

# Define a callback to process controller gCode responses (if desired)
def templateCallback(data):
   print ( "Controller gCode responses " + data )

machine_motion_example = MachineMotion(DEFAULT_IP_ADDRESS.usb_windows, templateCallback)

# Configure the axis number one, 8 uSteps and 150 mm / turn for a timing belt
machine_motion_example = machine_motion_example.configAxis(1, MICRO_STEPS.ustep_8, MECH_GAIN.timing_belt_150mm_turn)

print ( "--> Controller axis 1 configured" )
