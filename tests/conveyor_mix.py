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

    cspeed = 20000
    cacceleration = 20
    cduration = 1.0

    print("Conveyor +")
    m1.emitgCode("V4 S0 A30000 X")
    time.sleep(0.2)
    m1.emitgCode("V5 X2")
    m1.emitgCode("V4 S%d A%d X" % (cspeed, cacceleration))
    time.sleep(cduration)
    print("Position -")
    m1.emitgCode("V5 X1")
    m1.emitgCode("G91")
    m1.emitgCode("G0 X-300")
    m1.waitForMotionCompletion()
    time.sleep(0.1)

    print("Conveyor -")
    m1.emitgCode("V4 S0 A30000 X")
    time.sleep(0.2)
    m1.emitgCode("V5 X2")
    m1.emitgCode("V4 S-%d A%s X" % (cspeed, cacceleration))
    time.sleep(cduration)
    print("Position +")
    m1.emitgCode("V5 X1")
    m1.emitgCode("G91")
    m1.emitgCode("G0 X300")
    m1.waitForMotionCompletion()
    time.sleep(0.1)

