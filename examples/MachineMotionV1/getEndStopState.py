import sys
sys.path.append("../..")
from MachineMotion import *

### This Python example showcases how to read enstop sensor states with MachineMotion v1. ###

mm = MachineMotion()

# When starting a program, one must remove the software stop
print("--> Removing software stop")
mm.releaseEstop()
print("--> Resetting system")
mm.resetSystem()

# Get End Stop State
endstopStates = mm.getEndStopState()
# If the direction of the axis is normal, 
#   then the home sensor is the "_min" sensor, and the end sensor is the "_max" sensor.
# If the direction of the axis reversed, 
#   then the home sensor is the "_max" sensor, and the end sensor is the "_min" sensor.
axis1_home_sensor_status      = endstopStates['x_min']
axis1_endstop_sensor_status   = endstopStates['x_max']
axis2_home_sensor_status      = endstopStates['y_min']
axis2_endstop_sensor_status   = endstopStates['y_max']
axis3_home_sensor_status      = endstopStates['z_min']
axis3_endstop_sensor_status   = endstopStates['z_max']

print("Axis 1 : " + "Home sensor is : " + str(axis1_home_sensor_status) )
print("Axis 1 : " + "End sensor is : " + str(axis1_endstop_sensor_status) )
print("Axis 2 : " + "Home sensor is : " + str(axis2_home_sensor_status) )
print("Axis 2 : " + "End sensor is : " + str(axis2_endstop_sensor_status) )
print("Axis 3 : " + "Home sensor is : " + str(axis3_home_sensor_status) )
print("Axis 3 : " + "End sensor is : " + str(axis3_endstop_sensor_status) )
