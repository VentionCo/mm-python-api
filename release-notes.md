# Version 4.0
Date: April 19<sup>th</sup>, 2021

**New features:**
- The Python API now supports Python 3.7. 
- The Python API now supports the new functionalities of MachineMotion2, and maintains MachineMotion1 support.
    - You should now instantiate your MachineMotion object with a hardware version, using the `MACHINEMOTION_HW_VERSIONS` class.
    - The compatibility of all functions between MachineMotion1 and MachineMotion2 can be found in the `compatibility` section of each function description.
    - All example files have been updated and organized into MachineMotion1 and MachineMotion2 specific folders.
- We also provide some wrappers and examples for multi-drive axes with MachineMotion2, as defined in `multiDriveExtension.py`:
    - configServoMulti
    - configStepperMulti
    - emitRelativeMoveMulti
    - emitAbsoluteMoveMulti
    - emitHomeMulti
    - getActualPositionsMulti
    - setPositionMulti
    - emitSpeedMulti
    - emitAccelerationMulti
The example file is called `multiDriveAxis.py`.

**New functions:**
- configServo (configuration of servo motors in closed-loop for MachineMotion2)
- configStepper (configuration of motors in open-loop for MachineMotion2)
- getDesiredPositions
- getActualPositions
- emitCombinedAxisRelativeMove

**Minor updates and bug fixes:**
- The emergency stop related functions now have a return value representing the success of the operation (`triggerEstop`, `releaseEstop` and `resetSystem`).
- The gain of the `roller_conveyor_mm_turn` in the `MECH_GAIN` class now has been fixed with one more decimal.
- The electric cylinder's gain is supported in that class, under the name `electric_cylinder_mm_turn`.
- Updated restrictions for all functions, to better support MachineMotion1 and MachineMotion2 versions.

**Deprecated functions:**
- getCurrentPositions (use getDesiredPositions or getActualPositions instead)
- emitCombinedAxisRelativeMove (use emitCombinedAxesRelativeMove instead)
- emitDwell
- configMinMaxHomingSpeed (please use configHomingSpeed)
- configMachineMotionIp (please use the ControlCenter to configure the Ethernet ports of the MachineMotion)
- saveData
- getData
