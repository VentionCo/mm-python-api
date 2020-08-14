import sys
sys.path.append("..")
from MachineMotion import *

# Define a callback to process controller gCode responses (if desired)
def templateCallback(data):
   print ( "Controller gCode responses " + data )

mm = MachineMotion(DEFAULT_IP_ADDRESS.usb_windows, gCodeCallback = templateCallback)

# When starting a program, one must remove the software stop before moving
print("--> Removing software stop")
mm.releaseEstop()
print("--> Resetting system")
mm.resetSystem()

# Define the brake parameters
brake_aux_port_number = 1        # The AUX port number the brake is plugged in
safety_adapter_presence = False  # Is a yellow safety adapter plugged in between the brake cable and the AUX port

# Define Axis Parameters
axis = 1                         # Drive number
mechGain = MECH_GAIN.rack_pinion_mm_turn

# Configure the axis
mm.configAxis(axis, MICRO_STEPS.ustep_8, mechGain)

# Read brake state
brake_state = mm.getBrakeState (brake_aux_port_number, safety_adapter_presence)
print ("The brake connected to AUX" + str(brake_aux_port_number) + " is : " + brake_state)

# Lock the brake
mm.lockBrake (brake_aux_port_number, safety_adapter_presence)
time.sleep(0.2);                # Wait before reading brake state, for it to get correctly updated

# Read brake state
brake_state = mm.getBrakeState (brake_aux_port_number, safety_adapter_presence)
print ("The brake connected to AUX" + str(brake_aux_port_number) + " is : " + brake_state)

# DO NOT MOVE WHILE BRAKE IS ENGAGED
print ("Waiting two seconds. Do not move the actuator while the brake is locked !")
time.sleep(2)                   # Unlock the brake after two seconds

# Release the brakes
mm.unlockBrake (brake_aux_port_number, safety_adapter_presence)
time.sleep(0.2);                # Wait before reading brake state, for it to get correctly updated

# Read brake state
brake_state = mm.getBrakeState (brake_aux_port_number, safety_adapter_presence)
print ("The brake connected to AUX" + str(brake_aux_port_number) + " is : " + brake_state)

# Home Axis Before Move
print("Axis " + str(axis) + " moving home.")
mm.emitHome(axis)
print("Axis " + str(axis) + " homed")

# Move Relative
speed = 400                      # Speed in mm/sec
acceleration = 500               # Acceleration in mm/sec^2
distance = 100                   # Distance in mm
direction = "positive"

mm.emitSpeed(speed)
mm.emitAcceleration(acceleration)
mm.emitRelativeMove(axis, direction, distance)
mm.waitForMotionCompletion()
print("Axis " + str(axis) + " moved " + str(distance) + "mm in the " + direction + " direction")
