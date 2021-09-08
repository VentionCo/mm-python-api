import sys
sys.path.append("../..")
from MachineMotion import *

### This Python example configures actuators for a MachineMotion v2. ###

mm = MachineMotionV2()

# When starting a program, one must remove the software stop before moving
print("--> Removing software stop")
mm.releaseEstop()
print("--> Resetting system")
mm.resetSystem()

# Configure a timing belt actuator in servo mode, on drive 1
drive = 1
mechGain = MECH_GAIN.timing_belt_150mm_turn
direction = DIRECTION.NORMAL
motorCurrent = 5.0 # Amperes
mm.configServo(drive, mechGain, direction, motorCurrent)

# Configure an electric cylinder actuator in stepper mode, on drive 2
drive = 2
mechGain = MECH_GAIN.electric_cylinder_mm_turn
direction = DIRECTION.NORMAL
motorCurrent = 1.6 # Amperes
mm.configStepper(drive, mechGain, direction, motorCurrent) # Microsteps will default to 8.
# If you need to use a different microstepping :
#mm.configStepper(drive, mechGain, direction, motorCurrent, microSteps = MICRO_STEPS.ustep_4)
