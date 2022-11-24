Version 4.5

## Hardware Compatibility
Hardware version is available at the bottom of the ControlCenter page.
  - V2A3* 1D/4D
  - V2A4* 1D/4D
  - V2B0*  1D/4D
  - V2B1*  1D/4D
  - V2B2*  1D/4D
  - V2B3   1D/4D

  *: - These versions do not support path following. 


## Software Compatibility
Python API v4.5 is compatible with all software versions of Machine motion. However, some functions are only supported on newer versions. These functions are described below:

|  Function 	        |   2.2	|   2.3	|   2.4	|   2.5	|   2.6 |
|---	                |---	|---	|---	|---    |---    |
|loadPath   	        |   	|   	|   	|   	|✅     |
|startPath   	        |   	|   	|   	|   	|✅     |
|stopPath   	        |   	|   	|   	|   	|✅     |
|configActuator  	    |   	|   	|   	|   	|✅     |
|setAxisMaxSpeed   	    |   	|   	|✅     |✅     |✅     |
|setAxisMaxAcceleration |   	|   	|✅     |✅	  |✅     |
|getAxisMaxSpeed   	    |   	|   	|✅     |✅     |✅     |
|getAxisMaxAcceleration |   	|   	|✅     |✅	  |✅     |
|getActualSpeeds   	    |   	|   	|✅     |✅	  |✅     |
|stopAxis          	    |   	|   	|✅     |✅     |✅     |



## Additions

  + Add new classes for use with path following:
    + `DIGITAL_OUTPUT_STATE`: Defines deviceId, port and value a DIO module must have to trigger a tool action
    + `TOOL`: Mapping of a tool number and list of digital output states to define how a tool is activated and stopped.
  + Add path following functions:
    + `configPathMode`: Associates g-code axes with Vention drives, and tools with digital outputs
    + `startPath`: Sends a g-code path to the motion server to be executed
    + `stopPath`: Abrubtly stops a path
    + `getPathStatus`: Fetches relevant information on the current loaded path
  + Add path following example `pathFollowing.py`
  + Add new classes for Configuration Centralization:
    + `DriveConfigParams`: Defines the direction and motor size of a given drive
    + `AcutatorConfigParams`: Defines the various characteristics of a Vention actuator (e.g type, brake presence, gearbox, etc.)
    + `AXIS_TYPE`: Class of strings that define the available axis types for configuration
    + `GEARBOX`: Defines supported gearbox ratios for configuration
  + Add new function for Configuration Centralization:
    + `configActuator`: Uses the above new classes to configure a Vention actuator. This function makes requests to an intermediate server (execution engine) so that changes can be tracked in ControlCenter
  + Add new configuration example `configActuator.py`
  + Examples that previously included a configuration no longer do so. Instead, comments documenting the intended configuration have been added.
  + Support telescopic column
  + Support timing belt conveyor

For a complete API reference, see: [our documentation](vention.io)