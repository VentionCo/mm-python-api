# Testing the speed functions on Marlin using gCode and thin client
# System imports
import sys
import random
import time

# Custom imports
sys.path.append("..")
from MachineMotion import MachineMotion

m1 = MachineMotion("192.168.7.2", None)

m1.releaseEstop()
m1.resetSystem()

while (True) :
    m1.emitSpeed(2000)

    cspeed1 = 10000.0
    cspeed2 = 0.0
    cacceleration = 20000.0
    quickacceleration = 40000.0
    cduration = 3.0
    stoptime = 2.0
    axis = "X"

    print("Conveyor speed = 0")
    m1.emitgCode(("V4 S%d A%d " + axis) % (cspeed2, quickacceleration))
    time.sleep(2.0)
