# Testing the speed functions on Marlin using gCode and thin client
# System imports
import sys
import random
import time
import threading

# Custom imports
sys.path.append("..")
from MachineMotion import MachineMotion


m1 = MachineMotion("192.168.7.2", None)
m1.emitgCode("V5 Z2")

#while (1) :
#    speed = 6000.0
#    accel = 5.0
#
#    m1.emitgCode("V4 S" + str(speed) + " A" + str(accel) + " X")
#
#    print(m1.digitalRead(1,3))
#
#    while (m1.digitalRead(1,3)) :
#        time.sleep(0.2)
#
#    m1.emitgCode("V4 S" + str(-speed) + " A" + str(accel) + " X")
#
#    time.sleep(4.0)

def motor_x ():
    previous_speed = 0.0
    while (1) :
        speed = int(10000.0 * (2 * random.random()-1.0))
        accel = int(2500.0 * random.random() + 1000.0)
        m1.emitgCode("V4 S" + str(speed) + " A" + str(accel) + " X")

        time.sleep(abs((speed-previous_speed)) / accel + 1.0)
        previous_speed = speed

def motor_y ():
    previous_speed = 0.0
    while (1) :
        speed = int(10000.0 * (2 * random.random()-1.0))
        accel = int(2500.0 * random.random() + 1000.0)
        m1.emitgCode("V4 S" + str(speed) + " A" + str(accel) + " Y")

        time.sleep(abs((speed-previous_speed)) / accel + 1.0)
        previous_speed = speed

def motor_z ():
    previous_speed = 0.0
    while (1) :
        speed = int(10000.0 * (2 * random.random()-1.0))
        accel = int(2500.0 * random.random() + 1000.0)
        m1.emitgCode("V4 S" + str(speed) + " A" + str(accel) + " Z")

        time.sleep(abs((speed-previous_speed)) / accel + 1.0)
        previous_speed = speed

tx = threading.Thread(target=motor_x)
tx.daemon = True
tx.start()

ty = threading.Thread(target=motor_y)
ty.daemon = True
ty.start()

tz = threading.Thread(target=motor_z)
tz.daemon = True
tz.start()

while True:
    time.sleep(1)
