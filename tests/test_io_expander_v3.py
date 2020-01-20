#!/usr/bin/python

# System imports
import sys
# Custom imports
sys.path.append("..")

from MachineMotion import *

from random import *

# Define a callback to process controller gCode responses (if desired)
def templateCallback(data):
 print ( "Controller gCode responses " + data )

mm = MachineMotion("192.168.7.2", templateCallback)
time.sleep(1)

# Input device
# TODO: make class/struct
input_device = 1
input_pin = 0
input_state = 0

# Output device
# TODO: make class/struct
output_device = 2
output_pin = 0
output_state = 0

count = 0
checkFail_count = 0

# Error flag
# TODO: improve? remove if possible
error = False

# Initliaze all inputs to 0 (from device 1)
for x in range(3):
    mm.digitalWrite(input_device, x, 0)

time.sleep(5)
print("1: All inputs initialized to 0")

# Status Check
# Read input from device 2
print("Status Check:")
print("pin 0: " + str(mm.digitalRead(2, 0)))
print("pin 1: " + str(mm.digitalRead(2, 1)))
print("pin 2: " + str(mm.digitalRead(2, 2)))
print("pin 3: " + str(mm.digitalRead(2, 3)))
print("---------------------")
print("2: Status Check Done")

#print("Device: 1, pin 0, value: " + str(value) )
#print("Device :2, pin 0, value: " + str(value2) )

# Test if publication of topic is possible
#mm.myMqttClient.publish('devices/io-expander/' + str(device) + '/digital-output/' +  str(pin), '1' if value else '0', retain=True)

print("Start blink")
print("-------------------")

while(count < 100):

  count+=1
  # Write true to a random pin on device 1
  random_pin = randint(0,3)
  mm.digitalWrite(1, random_pin, 1)
  time.sleep(0.5)

  # check signal on device 2
  signalRead = mm.digitalRead(2, random_pin)
  print("Device 1, pin_" + str(random_pin) + ": 1 & Device 2, pin_" + str(random_pin) + ": " + str(signalRead) + "  count: " + str(count))
  if (signalRead != 1):
    checkFail_count+=float(1)
    time.sleep(10)

  # set state back to 0
  mm.digitalWrite(1, random_pin, 0)
  time.sleep(0.5)

fail_percentage = (checkFail_count/count) * 100
print(fail_percentage)
print("--------------")
print("Log: count: " + str(count) + " & checkFail count: " + str(checkFail_count) + " & checkFail percentage: " + str(fail_percentage) + "%")
print("End blink")

# Read value
#value = machine_motion_example.digitalRead(device, 0)
#print("Device = 1, pin = 0, value " + str(value) )
