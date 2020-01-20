#!/usr/bin/python
import random
import threading
import time
import sys

sys.path.append("..")

from MachineMotion import *

# Define a callback to process controller gCode responses (if desired)
def debug(data): pass

mm = MachineMotion("localhost", debug)
avg_perf_M119 = {"count": 0, "total": 0}
avg_perf_M115 = {"count": 0, "total": 0}
avg_perf_M114 = {"count": 0, "total": 0}

def move(mm):
    while True:
      pos = random.randint(10, 3000) - 1500
      print ("moving to %s" % pos)
      mm.emitgCode("G0 X%s" % pos)
      mm.waitForMotionCompletion()
      time.sleep(random.random() * 2)

def getEndstops(mm):
    while True:
      t0 = time.time()
      mm.emitgCode("M119")
      t1 = time.time()
      elapsed = 1000.0 * (t1 - t0)
      avg_perf_M119["count"] += 1
      avg_perf_M119["total"] += elapsed
      print ("M119 performed in %s ms (avg= %s)" % (elapsed, avg_perf_M119["total"] / avg_perf_M119["count"]))
      time.sleep(0.5)

def getFirmwareInfo(mm):
    while True:
      t0 = time.time()
      mm.emitgCode("M115")
      t1 = time.time()
      elapsed = 1000.0 * (t1 - t0)
      avg_perf_M115["count"] += 1
      avg_perf_M115["total"] += elapsed
      print ("M115 performed in %s ms (avg= %s)" % (elapsed, avg_perf_M115["total"] / avg_perf_M115["count"]))
      #time.sleep(0.1)


def getPositions(mm):
    while True:
      t0 = time.time()
      v = mm.emitgCode("M114")
      t1 = time.time()
      elapsed = 1000.0 * (t1 - t0)
      avg_perf_M114["count"] += 1
      avg_perf_M114["total"] += elapsed
      print ("M114 performed in %s ms (avg= %s): %s" % (elapsed, avg_perf_M114["total"] / avg_perf_M114["count"], v))
      #time.sleep(0.1)

# Configure the axis number one, 8 uSteps and 150 mm / turn for a timing belt
#mm.configAxis(1, MICRO_STEPS.ustep_8, 100)
#print ( "--> Controller axis 1 configured")

t1 = threading.Thread(target=move, args=(mm,))
t1.daemon = True
t1.start()
t2 = threading.Thread(target=getEndstops, args=(mm,))
t2.daemon = True
t2.start()
t3 = threading.Thread(target=getFirmwareInfo, args=(mm,))
t3.daemon = True
t3.start()
t4 = threading.Thread(target=getFirmwareInfo, args=(mm,))
t4.daemon = True
t4.start()
t5 = threading.Thread(target=getPositions, args=(mm,))
t5.daemon = True
t5.start()

while True:
    time.sleep(1)

# TODO:
# - time each request
# - provide a stat
# - no logging as much as possible
