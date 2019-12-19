# Testing the speed functions on Marlin using gCode and thin client
# System imports
import sys
import random
import time

# Custom imports
sys.path.append("..")
from MachineMotion import MachineMotion


m1 = MachineMotion(None, "192.168.7.2")
m1.emitgCode("V5 X2")

while (1) :
    speed = 6000.0
    accel = 5.0

    m1.emitgCode("V4 S" + str(speed) + " A" + str(accel))

    print(m1.digitalRead(1,3))

    while (m1.digitalRead(1,3)) :
        time.sleep(0.2)

    m1.emitgCode("V4 S" + str(-speed) + " A" + str(accel))

    time.sleep(4.0)

while (1) :
    speed = int(10000.0 * random.random() / 2.0)
    accel = int(10.0 * random.random() / 2.0 + 1.0)
    m1.emitgCode("V4 S" + str(speed) + " A" + str(accel))

    time.sleep(5.0)
