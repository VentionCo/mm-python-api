# Version 1.6.8

Date: September 24<sup>th</sup>, 2019

## Compatibility

### Interface Changes
- No Interface changes in this release

#### Obsoleted Interfaces
- none

#### New Interfaces
- setPosition
- emitCombinedAxisRelativeMove
- emitCombinedAxesAbsoluteMove

## Improvements:
- Added the multi-axis move commands
- Revised the entire API document
- Revised all examples and updated them to reflect all new changes

## Bug Fixes:
- Fixed bug that was present in the writeControlDevice function that was using the v2.1 Python version nomenclature in the MQTT topics.

# Version 1.6.7

Date: July 16<sup>th</sup>, 2019

## Improvements:
- Added support for Python3 and Python2.
- Fixed rounding errors in the configAxis function by using floats for incoming parameters

# Version: 1.6.6

Date:  July 4<sup>th</sup> 2019

## Bug Fixes:
- Fix distance of movement smaller then requested on linear axis.

## Improvements:
- All examples import statement are now version independant.

<br><br>
# Version: 1.6.5

Date:  June 4<sup>th</sup> 2019

## Bug Fixes:
- Fix Line Number mismatch with the help of the 'resend' message
- Fix application hang on termination 

## New Features:
- Support for the rotatory indexer with constants for mechanical gain.

## Improvements:
- Added more examples for each sensor port for the different control devices functions.
- Auto reconnect on connection loss
- Instead of starting a new thread each 0.1 seconds, we now start one thread at the beginning and keep it alive forever to receive messages from the server

