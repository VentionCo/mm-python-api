import sys, os
this_script_folder = os.path.dirname(__file__)
relative_path_to_MachineMotion_folder = os.path.dirname("../")
sys.path.insert(1, os.path.join(this_script_folder,relative_path_to_MachineMotion_folder))
from MachineMotion import *

mm = MachineMotion(DEFAULT_IP_ADDRESS.usb_windows)

#Adjust this line to match whichever AUX port the encoder is plugged into
encoderPort = AUX_PORTS.aux_1
encoderPortLabel = {AUX_PORTS.aux_1: "AUX 1", AUX_PORTS.aux_2: "AUX 2", AUX_PORTS.aux_3: "AUX 3"}

print("Reading and printing encoder output for 10 seconds:")
for i in range(1,100):
   realTimeOutput = mm.readEncoder(encoderPort, ENCODER_TYPE.real_time)
   stableOutput = mm.readEncoder(encoderPort, ENCODER_TYPE.stable)
   print("Encoder on port " + encoderPortLabel[encoderPort] + "\t Realtime Position =" + str(realTimeOutput) + " counts\t StablePosition = " + str(stableOutput))
   time.sleep(.5)

