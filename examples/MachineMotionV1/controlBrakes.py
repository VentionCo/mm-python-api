import sys, time
sys.path.append("../..")
from MachineMotion import *

### This Python example control brakes on MachineMotion v1. ###

print(" ----- WARNING ------ Does your hardware version support brakes?")

mm = MachineMotion()

# When starting a program, one must remove the software stop before moving
print("--> Removing software stop")
mm.releaseEstop()
print("--> Resetting system")
mm.resetSystem()

# Define the brake parameters
brake_port_number = 1           # The AUX port number the brake is plugged in
safety_adapter_presence = True  # Is a yellow safety adapter plugged in between the brake cable and the AUX port

# Read brake state
brake_state = mm.getBrakeState (brake_port_number, safety_adapter_presence)
print ("The brake connected to AUX" + str(brake_port_number) + " is : " + brake_state)

# Lock the brake
mm.lockBrake (brake_port_number, safety_adapter_presence)
time.sleep(0.2);                # Wait before reading brake state, for it to get correctly updated

# Read brake state
brake_state = mm.getBrakeState (brake_port_number, safety_adapter_presence)
print ("The brake connected to AUX" + str(brake_port_number) + " is : " + brake_state)

# DO NOT MOVE WHILE BRAKE IS ENGAGED
print ("Waiting two seconds. Do not move the actuator while the brake is locked !")
time.sleep(2)                   # Unlock the brake after two seconds

# Release the brakes
mm.unlockBrake (brake_port_number, safety_adapter_presence)
time.sleep(0.2);                # Wait before reading brake state, for it to get correctly updated

# Read brake state
brake_state = mm.getBrakeState (brake_port_number, safety_adapter_presence)
print ("The brake connected to AUX" + str(brake_port_number) + " is : " + brake_state)
