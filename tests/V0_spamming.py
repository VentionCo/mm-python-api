# This test spams the server with V0 commands and sees how it responds
import sys

sys.path.append("..")
from MachineMotion import *

# Create MachineMotion instance
mm = MachineMotion("192.168.7.2", None)

print("Start of test")

while(True):
    # Output V0 to Marlin
    mm.emitgCode("V0")

print("End of test")
