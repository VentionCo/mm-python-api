#!/usr/bin/python

# System import
import sys
# Custom imports
sys.path.append("..")

from MachineMotion import *

# Define a callback to process controller gCode responses (if desired)
def templateCallback(data):
   print ( "Controller gCode responses " + data )

mm = MachineMotion(templateCallback, "192.168.7.2")

#mm.move(0, 1, 10, 5, "absolute", "synchronous")

mm.configAxis(1, 8, 10)

# Motor 1, rotation 1
#mm.move(1, rotation = 1.0, speed = 10.0, accel = 10.0, reference = "absolute", type = "synchronous")

print("===Start move test===")
mm.myMqttClient.publish("===random_test/", "start===")

print("Rotate 10 rev; s = 10 m/s; a = 10 m/s; relative")
mm.move(1, 10, 10, 10.0, "absolute", "asynchronous")
mm.myMqttClient.publish("random_test/", "1")

time.sleep(1)

mm.triggerEstop()
print("trigger eStop")
time.sleep(2)

mm.releaseEstop()
print("release eStop")
time.sleep(2)

mm.resetSystem()
print("reset System")
time.sleep(2)

print("Rotate -10 rev; s = 10 m/s; a = 10 m/s; relative")
mm.move(1, 0, 10, 10.0, "absolute", "synchronous")
mm.myMqttClient.publish("random_test/", "2")

print("===End test===")
mm.myMqttClient.publish("===random_test/", "end===")
print("Check if motor is returned to absolute 0 position")
print("   ")
