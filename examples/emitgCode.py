from _MachineMotion import *

# Define a callback to process controller gCode responses if desired. This is mostly used for debugging purposes.
enableDebug = False
def debug(data):
    if(enableDebug): print("Debug Message: " + data + "\n")

#Declare parameters for g-Code command
speed = 500
acceleration = 500
axesToMove = [1,2,3]
positions = [50, 100, 50]
mechGain = MECH_GAIN.timing_belt_150mm_turn

#Load parameters for emitting g-code
mm = MachineMotion(debug, DEFAULT_IP_ADDRESS.usb_windows)
mm.emitSpeed(speed)
mm.emitAcceleration(acceleration)
for axis in axesToMove:
    mm.configAxis(axis, MICRO_STEPS.ustep_8, mechGain)
mm.emitHomeAll()
print("All Axes homed.")


# Use the G0 command to move both axis 1 and 2 by 50mm
gCodeCommand = "G0 X50 Y50"
mm.emitgCode(gCodeCommand)
mm.waitForMotionCompletion()
print("G-code command '" + gCodeCommand + "' completed by MachineMotion.")
