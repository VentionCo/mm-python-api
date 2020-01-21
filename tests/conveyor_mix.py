# Testing the speed functions on Marlin using gCode and thin client
# System imports
import sys
import random
import time

# Custom imports
sys.path.append("..")
from MachineMotion import MachineMotion

m1 = MachineMotion("192.168.7.2", None)

while (True) :
    m1.emitSpeed(2000)

    cspeed = 10000
    cacceleration = 20000
    cduration = 3.0
    stoptime = 2.0
    axis = "Y"

    print("Conveyor +")
    m1.emitgCode("V4 S0 A1000000 " + axis)
    time.sleep(stoptime)
    m1.emitgCode("V5 " + axis + "2")
    m1.emitgCode(("V4 S%d A%d " + axis) % (cspeed, cacceleration))
    time.sleep(cduration)
    print("Position -")
    m1.emitgCode("V5 " + axis + "1")
    m1.emitgCode("G91")
    m1.emitgCode("G0 " + axis + "-300")
    m1.waitForMotionCompletion()
    time.sleep(0.1)

    print("Conveyor -")
    m1.emitgCode("V4 S0 A1000000 " + axis)
    time.sleep(stoptime)
    m1.emitgCode("V5 " + axis + "2")
    m1.emitgCode(("V4 S-%d A%s " + axis) % (cspeed, cacceleration))
    time.sleep(cduration)
    print("Position +")
    m1.emitgCode("V5 " + axis + "1")
    m1.emitgCode("G91")
    m1.emitgCode("G0 " + axis + "300")
    m1.waitForMotionCompletion()
    time.sleep(0.1)
