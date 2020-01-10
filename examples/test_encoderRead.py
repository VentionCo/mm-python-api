#!/usr/bin/python

# System import
import sys
import time
# Custom imports
sys.path.append("..")

from MachineMotion import *

# Define a callback to process controller gCode responses (if desired)
def templateCallback(data):
   print ( "Controller gCode responses " + data )

mm = MachineMotion(None, "192.168.7.2")

time.sleep(1)

print("===Start test===")
print(" ")
print("Realtime position of encoder 0:  " + str(mm.myMqttClient.subscribe('devices/encoder/0/realtime-position')))
print("Realtime position of encoder 1:  " + str(mm.myMqttClient.subscribe('devices/encoder/1/realtime-position')))
print("Realtime position of encoder 2:  " + str(mm.myMqttClient.subscribe('devices/encoder/2/realtime-position')))
print("1: " + str(mm.readEncoder(2)))
print("2: " + str(mm.readEncoder(2)))
print("3: " + str(mm.readEncoder(2)))

time.sleep(1)

print("4: " + str(mm.readEncoder(2)))

print(" ")
print("===End test===")
