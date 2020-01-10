# System imports
import sys
# Custom imports
sys.path.append("..")

from MachineMotion import *

from random import *

# Define a callback to process controller gCode responses (if desired)
def templateCallback(data):
 print ( "Controller gCode responses " + data )

print(" mm.isReady() : " +  str(mm.isReady()))

mm = MachineMotion(templateCallback, "192.168.7.2")
print(" mm.isReady() : " +  str(mm.isReady()))

while mm.isReady() != True : pass

print(" mm.isReady() : " +  str(mm.isReady()))

