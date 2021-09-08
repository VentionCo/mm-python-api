import sys, time
sys.path.append("../..")
from MachineMotion import *

### This Python example control brakes on MachineMotion v2. ###

mm = MachineMotionV2()

# When starting a program, one must remove the software stop before moving
print("--> Removing software stop")
mm.releaseEstop()
print("--> Resetting system")
mm.resetSystem()

# Define the brake parameters
axis = 1                        # Drive number
safety_adapter_presence = True  # Is a yellow safety adapter plugged in between the brake cable and the brake port
                                # Important Note : This flag must always be set to "True" on MachineMotions v2.

# Read brake state
brake_state = mm.getBrakeState(axis, safety_adapter_presence)
print ("The brake connected to port " + str(axis) + " is : " + brake_state)

# Lock the brake
mm.lockBrake(axis, safety_adapter_presence)
time.sleep(0.2);                # Wait before reading brake state, for it to get correctly updated

# Read brake state
brake_state = mm.getBrakeState(axis, safety_adapter_presence)
print ("The brake connected to port " + str(axis) + " is : " + brake_state)

# DO NOT MOVE WHILE BRAKE IS ENGAGED
print ("Waiting two seconds. Do not move the actuator while the brake is locked !")
time.sleep(2)                   # Unlock the brake after two seconds

# Release the brakes
mm.unlockBrake(axis, safety_adapter_presence)
time.sleep(0.2);                # Wait before reading brake state, for it to get correctly updated

# Read brake state
brake_state = mm.getBrakeState(axis, safety_adapter_presence)
print ("The brake connected to port " + str(axis) + " is : " + brake_state)
