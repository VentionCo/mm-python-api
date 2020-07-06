import sys
import random
from MachineMotion import *

#Declare parameters for combined absolute move
speed = 500
acceleration = 1000
axesToMove = [1,2,3]
positions = [-500, -500, -500]
direction = ["positive", "positive", "positive"]
mechGain = MECH_GAIN.timing_belt_150mm_turn
randTime = 0

# Define a callback to process controller gCode responses (if desired)
def templateCallback(data):
   print ( "Controller gCode responses " + data )

mm = MachineMotion(DEFAULT_IP_ADDRESS.usb_windows, gCodeCallback = templateCallback)

def eStop(mm):

    def goHomeCallback(mm):
        print("Recover from eStop: go Home All")
        mm.emitHomeAll()

    # mm.bindeStopEvent(goHomeCallback(mm))

    mm.triggerEstop()
    print("--> eStop triggered")

    mm.releaseEstop()
    print("--> eStop released")

    mm.resetSystem()
    print("--> System resetted")
    time.sleep(3)

#When starting a program, one must remove the software stop before moving
print("--> Removing software stop")
mm.releaseEstop()
print("--> Resetting system")
mm.resetSystem()

mm.emitSpeed(speed)
mm.emitAcceleration(acceleration)
for i in axesToMove:
    mm.configAxis(i, MICRO_STEPS.ustep_8, mechGain)
    mm.configHomingSpeed(i, 250)
mm.emitHomeAll()

while(1):

    # Random vars ~
    # Random timer for eStop
    randTime = random.uniform(0.0, 2.0)
    # Random speed & accel
    speed = random.randint(200, 750)
    acceleration = random.randint(500, 1500)
    mm.emitSpeed(speed)
    mm.emitAcceleration(acceleration)
    print("     Speed: " + str(speed) + "  & Acceleration: " + str(acceleration))

    print("/// Start of Loop")
    print("All Axes Moving Home Sequentially")
    mm.emitHomeAll()
    mm.waitForMotionCompletion()
    print("All Axes homed.")

    # 1: Combined Move (without eStop)
    print("/// G0 X500 Y500 Z500")
    mm.emitgCode("G0 X500 Y500 Z500")
    mm.waitForMotionCompletion()

    print("All Axes Moving Home Sequentially")
    # mm.emitHomeAll()
    mm.emitgCode("G0 X-500 Y-500 Z-500")
    # mm.emitCombinedAxisRelativeMove(axesToMove, direction, positions)
    mm.waitForMotionCompletion()
    print("All Axes homed.")

    # 2: Combined Move with eStop
    print("/// G0 X500 Y500 Z500 with eStop with random trigger time of " + str(randTime))
    print("     Speed: " + str(speed) + "  & Acceleration: " + str(acceleration))

    mm.emitgCode("G0 X500 Y500 Z500")
    # Trigger eStop: 0.8 to stop motion at mid point
    time.sleep(randTime)
    eStop(mm)
    mm.waitForMotionCompletion()

    print("All Axes Moving Home Sequentially")
    # mm.emitHomeAll()
    mm.emitgCode("G0 X-500 Y-500 Z-500")
    #mm.emitCombinedAxisRelativeMove(axesToMove, direction, positions)
    mm.waitForMotionCompletion()
    print("All Axes homed.")
    print("/// End of Loop")

    time.sleep(5)

