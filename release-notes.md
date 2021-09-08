## Python API Version 4.2
Date: September 8<sup>th</sup> 2021

Python API supports Python 3.7.3 and older. Python-API v4.2 has been updated to support the following:

  - For Linux and Mac machines, it is now possible to install the Python api system-wide. To update or install a Python API version, navigate to the folder with the new Python API and run:
   
    `make install`
  - Simplified declaration of a new MachineMotion object. Creation of a MachineMotionv2 can be done as follows:

    `mm = MachineMotionV2()`
    
    `mm = MachineMotionV2OneDrive()`
  - Push Button and Power Switch modules are now supported.
  - Axes containing multiple drives can be configured and controlled as one.
  - Combined moves with the 4th drive are now allowed.
  - Enclosed ball screw is now supported.
  - Some function names have been changed to reflect MachineLogic naming. The old names are deprecated, but will still work. These functions are:
     - emitSpeed -> setSpeed
     - emitAcceleration -> setAcceleration
     - emitRelativeMove -> moveRelative
     - emitAbsoluteMove -> moveToPosition
     - emitCombinedAxesRelativeMove -> moveRelativeCombined
     - emitCombinedAxesAbsoluteMove -> moveToPositionCombined
     - emitContinuousMove -> moveContinuous
     - emitHome -> moveToHome
     - emitHomeAll -> moveToHomeAll
   - There is no directions field in moveRelative, moveRelativeCombined. Simply put a positive or negative distance to set the direction of movement.
   - moveToHome is not a blocking function. To block a script while homing, simply add a waitForMotionCompletion when desired.

## Known Issues
  - If using the python API to control motors, you must first configure your actuators with the python API. Failure to do so can result in unexpected behaviour. 
