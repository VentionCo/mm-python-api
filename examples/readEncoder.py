from _MachineMotion import *

mm = MachineMotion(DEFAULT_IP_ADDRESS.usb_windows)

#Adjust this line to match whichever AUX port the encoder is plugged into
encoderPort = AUX_PORTS.AUX1

print("Reading and printing encoder output for 10 seconds:")
for i in range(1,50):
   encoderOutput = mm.readEncoder(encoderPort)
   print("Encoder on port AUX" + str(encoderPort+1) + " reads a value of " + str(encoderOutput) + " counts")
   time.sleep(0.2)

