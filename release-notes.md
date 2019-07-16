# Version 1.6.7

Date: July 16<sup>th</sup>, 2019

## Improvements:
- Added support for Python3 and Python2.


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

