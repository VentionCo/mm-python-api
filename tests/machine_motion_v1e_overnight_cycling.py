#!/usr/bin/python

# System imports
import sys
# Custom imports
sys.path.append("..")

from MachineMotion import *
# Define a callback to process controller gCode responses (if desired)
def templateCallback(data):
   print ( "Controller gCode responses " + data )

mm = MachineMotion(DEFAULT_IP_ADDRESS.usb_windows, templateCallback)

mm.configAxis(1, MICRO_STEPS.ustep_8, MECH_GAIN.timing_belt_150mm_turn)
mm.configAxis(2, MICRO_STEPS.ustep_8, MECH_GAIN.timing_belt_150mm_turn)
mm.configAxis(3, MICRO_STEPS.ustep_8, MECH_GAIN.timing_belt_150mm_turn)

# Configuring the travel speed to 10 000 mm / min
mm.emitSpeed(100000)

# Configuring the travel speed to 1000 mm / second^2
mm.emitAcceleration(10000)

# Homing axis one
mm.emitHomeAll()
mm.waitForMotionCompletion()

i = 0

for i in range (0, 100000):
    
    
    mm.emitSpeed(100000)
    mm.emitAcceleration(10000)

    x = 0
    for x in range (0, 3):
        mm.emitgCode("G0 X500 Y500 Z500")
        mm.emitgCode("G0 X10 Y10 Z10")    
    mm.waitForMotionCompletion()

    mm.emitSpeed(100000)
    mm.emitAcceleration(5000)
    mm.emitAbsoluteMove(1, 500)
    mm.emitAbsoluteMove(2, 500)
    mm.emitAbsoluteMove(3, 500)
    mm.emitAbsoluteMove(1, 10)
    mm.emitAbsoluteMove(2, 10)
    mm.emitAbsoluteMove(3, 10)    
    
    mm.waitForMotionCompletion()
    
    mm.emitHomeAll()
    mm.waitForMotionCompletion()

print ( "--> Example completed." )
