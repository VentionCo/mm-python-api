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

    print("Conveyor +")
    #m1.emitgCode(("V4 S%d A%d " + axis) % (cspeed2, quickacceleration))
    #time.sleep(abs(cspeed2-cspeed1)/quickacceleration)
    #m1.emitgCode("V5 " + axis + "2")
    m1.emitgCode(("V4 S%d A%d " + axis) % (cspeed1, cacceleration))
    time.sleep((cspeed1-cspeed2)/cacceleration + cduration)
    m1.emitgCode(("V4 S%d A%d " + axis) % (cspeed2, quickacceleration))
    time.sleep(abs(cspeed2-cspeed1)/quickacceleration)
    print("Position -")
    m1.emitgCode("V5 " + axis + "1")
    m1.emitgCode("G91")
    m1.emitgCode("G0 " + axis + "-300")
    m1.waitForMotionCompletion()
    time.sleep(3.0)

    print("Conveyor -")
    #m1.emitgCode(("V4 S%d A%d " + axis) % (cspeed2, quickacceleration))
    #time.sleep(abs(cspeed2-cspeed1)/quickacceleration)
    #m1.emitgCode("V5 " + axis + "2")
    m1.emitgCode(("V4 S-%d A%d " + axis) % (cspeed1, cacceleration))
    time.sleep((cspeed1-cspeed2)/cacceleration + cduration)
    m1.emitgCode(("V4 S%d A%d " + axis) % (cspeed2, quickacceleration))
    time.sleep(abs(cspeed2-cspeed1)/quickacceleration)
    print("Position +")
    m1.emitgCode("V5 " + axis + "1")
    m1.emitgCode("G91")
    m1.emitgCode("G0 " + axis + "300")
    m1.waitForMotionCompletion()
    time.sleep(3.0)
