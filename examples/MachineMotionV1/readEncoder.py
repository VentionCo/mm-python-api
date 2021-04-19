import sys, time
sys.path.append("../..")
from MachineMotion import *

### This Python example showcases how to read encoder positions with MachineMotion v1. ###

mm = MachineMotion()

# Adjust this line to match whichever AUX port the encoder is plugged into
encoderPort = AUX_PORTS.aux_1

checkInput = True
print("Reading and printing encoder output for 10 seconds:")
for i in range(1,30):
   realTimeOutput = mm.readEncoder(encoderPort, ENCODER_TYPE.real_time)
   stableOutput = mm.readEncoder(encoderPort, ENCODER_TYPE.stable)
   print("Encoder on port AUX " + str(encoderPort+1) + "\t Realtime Position =" + str(realTimeOutput) + " counts\t StablePosition = " + str(stableOutput))
   time.sleep(.25)

   if realTimeOutput != 0:
      checkInput = False

if(checkInput):
   print("The encoder is not receiving any data. Please check the following: \n\t Is the encoder plugged into AUX " + str(encoderPort+1) + "? \n\t Ensure the encoder rotates during program execution. (Readings are triggered only when the encoder moves)")
