from _MachineMotion import *

mm = MachineMotion(DEFAULT_IP_ADDRESS.usb_windows)

#Adjust this line to match whichever AUX port the encoder is plugged into
encoderPort = AUX_PORTS.AUX1
encoderPortLabel = {AUX_PORTS.AUX1: "AUX 1", AUX_PORTS.AUX2: "AUX 2", AUX_PORTS.AUX3: "AUX 3"}

print("Reading and printing encoder output for 10 seconds:")
for i in range(1,50):
   encoderOutput = mm.readEncoder(encoderPort)
   print("Encoder on port " + encoderPortLabel[encoderPort] + " reads a value of " + str(encoderOutput) + " counts")
   time.sleep(0.2)

