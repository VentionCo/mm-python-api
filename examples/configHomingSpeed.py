import sys
sys.path.insert(1,"C:\\Users\\Jack\\Documents\\Vention\\Repos\\2.2\\py22\\mm-python-api\\_MachineMotion.py")
sys.path.insert(1,"C:\\Users\\Jack\\Documents\\Vention\\Repos\\2.2\\py22\\mm-python-api\\")
from _MachineMotion import *

mm = MachineMotion(DEFAULT_IP_ADDRESS.usb_windows)

axes = [1,2,3]    
axis =3                                #The axis that you'd like to move
speeds = [25,25,25]                                 #The max speed you'd like to move at
acceleration = 10                          #The constant acceleration and decceleration value for the move

mm.emitSpeed(15)
mm.emitAcceleration(10)
mm.emitAbsoluteMove(3, 40)
mm.emitCombinedAxesAbsoluteMove([1,2], [50,50])
mm.configAxis(3, 8, 17)

print("Moving to position = 100")
mm.emitAbsoluteMove(axis, 100)
mm.waitForMotionCompletion()
mm.configHomingSpeed(axes, speeds)
mm.waitForMotionCompletion()
mm.emitHome(axis)
mm.waitForMotionCompletion()


