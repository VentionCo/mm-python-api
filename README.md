# mm-python-api
MachineMotion Python API

# How-to Guide: MachineMotion Python SDK

<div style="text-align: center;"><img src="https://s3.amazonaws.com/ventioncms/vention_images/images/000/001/021/large/cover_python_guide.png?1550698357" width="80%" /></div>

<p>&nbsp;</p>

## Introduction

This guide will cover the setup and use of Vention’s MachineMotion™ Python Software Development Kit (SDK). After reading this guide, you will be ready to deploy custom motion and control applications using Vention’s MachineMotion controller. Before you begin, we recommended reading the <a href="https://www.vention.io/technical_documents/machine_motion_docs/vention_machine_motion_user_guide" target="_blank">MachineMotion Quick Start Guide</a> to get familiar with the technology.

## Typical System Overview

Many systems are built by centralizing application-level software on a host computer. The software interacts with various devices (such as robotic devices, sensors, proprietary products, and data acquisition equipment) and delivers the required application behavior (see Figure 1).

<p style="text-align:center;" ><img src="https://s3.amazonaws.com/ventioncms/vention_images/images/000/001/027/large/auto_HTG0006_typicalApplication.png?1550763014" width="65%" height="65%"></p>

<center>
<p style="text-align: center;"><span style="color: #808080; font-size: 11pt;"><em>Figure 1: Typical system configuration</em></p>
</center>

Using MachineMotion with Python is ideal for these types of applications, especially where an easy to deploy motion control system is necessary.

## Installation

### Windows

To set up the MachineMotion Python library:  

- Download the latest
<a href="https://s3.amazonaws.com/ventionblobs/sdk/machineMotionPythonApi_v1.6.2.zip" target="_blank">Python SDK 1.6.2</a>

- Unzip the content on your computer. This location will be your workspace.

- Install
<a href="https://www.python.org/download/releases/2.7/" target="_blank">Python 2.7</a> 

*++Note for Windows users++: Make sure to add Python.exe to the PATH environment variable as shown in *Figure 2*.*

<p style="text-align:center;" ><img src="https://s3.amazonaws.com/ventioncms/vention_images/images/000/001/026/large/auto_HTG0006_pythonInstPathInstruction.png?1550763013" width="45%" height="45%"></p>

<p style="text-align: center;"><span style="color: #808080; font-size: 11pt;"><em>Figure 2: Make sure to select "Add python.exe to path" if installing on Windows.</em></p>

- Open the command prompt (for Windows) or the terminal (for Mac or Linux users) and run the following installations  

  ```console
  pip install -U socketIO-client
  ```  
  
  ```console
  pip install -U pathlib
  ```

- The MachineMotion Python library is now ready to use. Programs can be created and ran from the workspace folder.

## Connectivity Setup

MachineMotion has two communication ports, one labeled USB and one labeled ETHERNET. Both use IP connectivity and have their own unique IP addresses, (see *Figure 3*).

</br>

<p style="text-align:center;" ><img src="https://s3.amazonaws.com/ventioncms/vention_images/images/000/001/025/large/auto_HTG0006_machineMotionFrontPanel.png?1550763012" width="50%" height="50%"></p>

<p style="text-align: center;"><span style="color: #808080; font-size: 11pt;"><em>Figure 3: MachineMotion front panel.</em></p>

The IP address associated with the USB port is static (192.168.7.2 for Windows; 192.168.6.2 for Mac and Linux). It cannot be configured or modified. The USB port should be used for direct computer-to-MachineMotion connectivity.

The IP address associated with the ETHERNET port can be modified to suit your network requirements. Refer to the <a href="https://www.vention.io/" target="_blank">How-to Guide: MachineMotion Network Setup</a> for more details.

## Configuring the network and axes 

When creating a Python program to control the MachineMotion controller, the first step is always to create a MachineMotion instance. This will establish communication with the actual controller and expose different functions that can be used to send commands.

After creating the MachineMotion instance, you must configure the network and axis. The functions to perform these steps are covered in this section.

---
### MachineMotion(callback, ip)

Creates a MachineMotion instance and establishes the TCP/IP communication. This function is a constructor.

#### callback {def callbackName(data):}  

> Handle in which incoming messages from the controller can be processed. The data are passed to the callback as a string argument.

#### ip {string}

> IP address of the MachineMotion controller.

#### return value {MachineMotion}
> Instance created by the constructor.

#### Example

```python
from _MachineMotion import *

# Define a callback to process controller gCode responses
def templateCallback(data):
   print "Controller gCode responses " + data

machine_motion_example = MachineMotion(templateCallback, DEFAULT_IP_ADDRESS.usb_windows)

print "Controller connected"
```

#### Output
```
Controller gCode responses MachineMotion Session Start
Controller gCode responses echo:N0 M110 N0*125
Controller gCode responses ok
Controller gCode responses echo:N1 M111 S247*97
Controller gCode responses echo:DEBUG:ECHO,INFO,ERRORS,COMMUNICATION
Controller gCode responses ok
Controller connected
```

---
### configMachineMotionIp(mode, ip, netmask, gateway)

Configures the IP address of the controller Ethernet interface.

#### mode {NETWORK_MODE}
> IP configures the network management profile as either static or DHCP.

#### ip {String}
> Desired static IP address to assign to the MachineMotion controller. Format is "nnn.nnn.nnn.nnnn", where n are numbers.

#### netmask {String}
> Network netmask. Format is "nnn.nnn.nnn.nnnn", where n are numbers.

#### gateway {String}
> IP address of the network gateway. Format is "nnn.nnn.nnn.nnnn", where n are numbers.
    
#### return value
> none

####  Example 1

```python
from _MachineMotion import *

# Define a callback to process controller gCode responses (if desired)
def templateCallback(data):
   print "Controller gCode responses " + data

machine_motion_example = MachineMotion(templateCallback, DEFAULT_IP_ADDRESS.usb_windows)

machine_motion_example = machine_motion_example.configMachineMotionIp(NETWORK_MODE.static, "192.168.0.2", "255.255.255.0", "192.168.0.1")

print "--> Controller connected & ethernet interface configured (static)"
```

#### Output 1
```
Controller gCode responses MachineMotion Session Start
Controller gCode responses echo:N0 M110 N0*125
Controller gCode responses ok
Controller gCode responses echo:N1 M111 S247*97
Controller gCode responses echo:DEBUG:ECHO,INFO,ERRORS,COMMUNICATION
Controller gCode responses ok
--> Controller connected & ethernet interface configured (static)
```

#### Example 2

```python
from _MachineMotion import *

# Define a callback to process controller gCode responses (if desired)
def templateCallback(data):
   print "Controller gCode responses " + data

machine_motion_example = MachineMotion(templateCallback, DEFAULT_IP_ADDRESS.usb_windows)

machine_motion_example = machine_motion_example.configMachineMotionIp(NETWORK_MODE.dhcp, "", "", "")

print "--> Controller connected & ethernet interface configured (dhcp)"
```

#### Output 2
```
Controller gCode responses MachineMotion Session Start
Controller gCode responses echo:N0 M110 N0*125
Controller gCode responses ok
Controller gCode responses echo:N1 M111 S247*97
Controller gCode responses echo:DEBUG:ECHO,INFO,ERRORS,COMMUNICATION
Controller gCode responses ok
--> Controller connected & ethernet interface configured (dhcp)
```
---
### configAxis(axis, u_step, mech_gain)

Configure the axis' mechanical gain and micro-step settings to ensure accurate motion.

#### axis {Number}
> Axis to configure

u_step {MICRO_STEPS}
> Micro-step setting

#### mech_gain {MECH_GAIN}
> Mechanical gain of the axis in mm per turn.

#### return value
> None.

#### Example

```python
from _MachineMotion import *

# Define a callback to process controller gCode responses (if desired)
def templateCallback(data):
   print "Controller gCode responses " + data

machine_motion_example = MachineMotion(templateCallback, DEFAULT_IP_ADDRESS.usb_windows)

# Configure the axis number one, 8 uSteps and 150 mm / turn for a timing belt
machine_motion_example = machine_motion_example.configAxis(1, MICRO_STEPS.ustep_8, MECH_GAIN.timing_belt_150mm_turn)

print "--> Controller axis 1 configured"
```

#### Output
```
Controller gCode responses MachineMotion Session Start
Controller gCode responses echo:N0 M110 N0*125
Controller gCode responses ok
Controller gCode responses echo:N1 M111 S247*97
Controller gCode responses echo:DEBUG:ECHO,INFO,ERRORS,COMMUNICATION
Controller gCode responses ok
Controller gCode responses echo:N2 M92 X10*99
Controller gCode responses ok
--> Controller axis 1 configured
```
---
### saveData(key, data)

> Save a key-value pair on the controller.

#### key {String}
> Key to identify the data.

#### data {Dictionary}
> Dictionary containing the data to save.

#### return value
> None.

#### Exampledfd

```python
from _MachineMotion import *

# Define a callback to process controller gCode responses (if desired)
def templateCallback(data):
   print "Controller gCode responses " + data

machine_motion_example = MachineMotion(templateCallback, DEFAULT_IP_ADDRESS.usb_windows)

# Saving a string on the controller
machine_motion_example = machine_motion_example.saveData("data_1", "save_this_string_on_the_controller")

print "--> Data sent on controller"
```

---
### getData(key, callback)

Retrieve a key-value pair that was saved on the controller.

#### key {String}
> key is a string that identifies the data to retrieve.


#### callback {def callbackName(data):}
> Function to invoke once the data is available. The data will be passed to the callback as an argument—specifically, as a serialized JSON string.

#### Example

```python
from _MachineMotion import *

# Define a callback to process controller gCode responses (if desired)
def templateCallback(data):
   print "Controller gCode responses " + data

# Define a callback to print the data retrieved using the getData function
def printGetDataResult(data):
   print "--> Retrieved data = " + data

machine_motion_example = MachineMotion(templateCallback, DEFAULT_IP_ADDRESS.usb_windows)

# Saving a string on the controller
machine_motion_example.saveData("data_1", "save_this_string_on_the_controller")


machine_motion_example.getData("data_1", printGetDataResult)
```

#### Output
```
Controller gCode responses MachineMotion Session Start
Controller gCode responses echo:N0 M110 N0*125
Controller gCode responses ok
Controller gCode responses echo:N1 M111 S247*97
Controller gCode responses echo:DEBUG:ECHO,INFO,ERRORS,COMMUNICATION
Controller gCode responses ok
--> Retrieved data = {"data": "save_this_string_on_the_controller", "fileName": "data_1"}
```

## Motion Functions

---
### isReady()

Blocking function that waits for the MachineMotion controller to ackowledge the command before continuing code execution. This is a code flow control function.

#### return value
> None.

#### Example

```python
from _MachineMotion import *

# Define a callback to process controller gCode responses (if desired)
def templateCallback(data):
   print "Controller gCode responses " + data

machine_motion_example = MachineMotion(templateCallback, DEFAULT_IP_ADDRESS.usb_windows)

# Homing axis 1
machine_motion_example.emitHome(1)
# Wait for the message to be acknowledged by the motion controller
while machine_motion_example.isReady() != "true": pass

print "--> This line executes after the motion controller has acknowledged receipt of the command."

```

#### Output

```
Controller gCode responses MachineMotion Session Start
Controller gCode responses echo:N0 M110 N0*125
Controller gCode responses ok
Controller gCode responses echo:N1 M111 S247*97
Controller gCode responses echo:DEBUG:ECHO,INFO,ERRORS,COMMUNICATION
Controller gCode responses ok
Controller gCode responses echo:N2 G28 X*105
Controller gCode responses X:0.00 Y:0.00 Z:0.00 E:0.00 Count X: 0 Y:0 Z:0
Controller gCode responses ok
--> This line executes after the motion controller has acknowledged the reception of the command.
```

---
### waitForMotionCompletion()

Blocking function that prevents program execution until the last motion has been completed. Until the machine has not finished its final movement, the code will not be executed.

#### return value
> None.

#### Example

```python
from _MachineMotion import *

# Define a callback to process controller gCode responses (if desired)
def templateCallback(data):
   print "Controller gCode responses " + data

machine_motion_example = MachineMotion(templateCallback, DEFAULT_IP_ADDRESS.usb_windows)

# Homing axis 1
machine_motion_example.emitHome(1)
# Wait for the message to be acknowledged by the motion controller
while machine_motion_example.isReady() != "true": pass
machine_motion_example.waitForMotionCompletion()

print "--> This line executes after the motion controller has acknowledged the reception of the command."

```

#### Output
```
Controller gCode responses MachineMotion Session Start
Controller gCode responses echo:N0 M110 N0*125
Controller gCode responses ok
Controller gCode responses echo:N1 M111 S247*97
Controller gCode responses echo:DEBUG:ECHO,INFO,ERRORS,COMMUNICATION
Controller gCode responses ok
Controller gCode responses echo:N2 G28 X*105
Controller gCode responses X:0.00 Y:0.00 Z:0.00 E:0.00 Count X: 0 Y:0 Z:0
Controller gCode responses ok
Controller gCode responses echo:N3 V0*59
A motion status was requested
move is in progress
Controller gCode responses Motion Status = COMPLETED
Controller gCode responses ok
Controller gCode responses echo:N4 V0*60
A motion status was requested
Move was completed
Controller gCode responses Motion Status = COMPLETED
--> This line executes after the motion controller has acknowledged receipt of the command.
Controller gCode responses ok
```

---
### emitStop()

Immediately stops motion on all axes.

#### return value
> none


#### Example

```python
from _MachineMotion import *

# Define a callback to process controller gCode responses (if desired)
def templateCallback(data):
   print "Controller gCode responses " + data

machine_motion_example = MachineMotion(templateCallback, DEFAULT_IP_ADDRESS.usb_windows)

# Send a stop command to the machine (this works even if the machine has not started moving yet)
machine_motion_example.emitStop()

print "--> Machine Stopped"

```

#### Output
```
Controller gCode responses MachineMotion Session Start
Controller gCode responses echo:N0 M110 N0*125
Controller gCode responses ok
Controller gCode responses echo:N1 M111 S247*97
Controller gCode responses echo:DEBUG:ECHO,INFO,ERRORS,COMMUNICATION
Controller gCode responses ok
Controller gCode responses echo:N2 M410*36
Controller gCode responses ok
--> Machine Stopped
```

---
### emitHomeAll()

Moves all carriages to their home location sequentially, axis 1 to axis 3.

#### return value
> none

#### Example

```python
from _MachineMotion import *

# Define a callback to process controller gCode responses (if desired)
def templateCallback(data):
   print "Controller gCode responses " + data

machine_motion_example = MachineMotion(templateCallback, DEFAULT_IP_ADDRESS.usb_windows)

# Homing all the axes of the controller sequentially
machine_motion_example.emitHomeAll()
machine_motion_example.waitForMotionCompletion()

print "--> All axes are now at home position."

```

---
### emitHome(axis)

Moves the carriage of the corresponding axis to its home location.


#### axis {AXIS_NUMBER}
> Axis to move to home location

#### return value
> none

#### Example

```python
from _MachineMotion import *

# Define a callback to process controller gCode responses (if desired)
def templateCallback(data):
   print "Controller gCode responses " + data

machine_motion_example = MachineMotion(templateCallback, DEFAULT_IP_ADDRESS.usb_windows)

# Homing axis 1
machine_motion_example.emitHome(1)
machine_motion_example.waitForMotionCompletion()

print "--> Axis 1 is now at home position."

```

#### Output
```
Controller gCode responses MachineMotion Session Start
Controller gCode responses echo:N0 M110 N0*125
Controller gCode responses ok
Controller gCode responses echo:N1 M111 S247*97
Controller gCode responses echo:DEBUG:ECHO,INFO,ERRORS,COMMUNICATION
Controller gCode responses ok
Controller gCode responses echo:N2 G28 X*105
Controller gCode responses X:0.00 Y:0.00 Z:0.00 E:0.00 Count X: 0 Y:0 Z:0
Controller gCode responses ok
Controller gCode responses echo:N3 V0*59
A motion status was requested
Movement is in progress
Controller gCode responses Motion Status = COMPLETED
Controller gCode responses ok
Controller gCode responses echo:N4 V0*60
A motion status was requested
Move was completed
Controller gCode responses Motion Status = COMPLETED
--> Axis 1 is now at home position.
Controller gCode responses ok
```

---
### emitSpeed(mmPerMin)

Configures the travel speed. Travel speed applies to combined axis moves and single axis moves.

#### mmPerMin {Number}
> Motion speed in mm per minute

#### return value
> none

#### Example

```python
from _MachineMotion import *

# Define a callback to process controller gCode responses (if desired)
def templateCallback(data):
   print "Controller gCode responses " + data

machine_motion_example = MachineMotion(templateCallback, DEFAULT_IP_ADDRESS.usb_windows)

# Configuring the travel speed to 10,000 mm / min
machine_motion_example.emitSpeed(10000)

print "--> Machine moves are not set to 10 000 mm / min"

```

---
### emitAcceleration(mmPerSecSqr)

Configures travel acceleration. Travel acceleration applies to combined axis moves and single axis moves.

#### mmPerSecSqr {Number}
> Motion speed in mm per minute

#### return value
> none

#### Example

```python
from _MachineMotion import *

# Define a callback to process controller gCode responses (if desired)
def templateCallback(data):
   print "Controller gCode responses " + data

machine_motion_example = MachineMotion(templateCallback, DEFAULT_IP_ADDRESS.usb_windows)

# Configuring the travel speed to 1000 mm / second^2
machine_motion_example.emitAcceleration(1000)

print "--> Machine moves are not set to accelerate @ 1000 mm / second^2"

```

#### Output
```
Controller gCode responses MachineMotion Session Start
Controller gCode responses echo:N0 M110 N0*125
Controller gCode responses ok
Controller gCode responses echo:N1 M111 S247*97
Controller gCode responses echo:DEBUG:ECHO,INFO,ERRORS,COMMUNICATION
Controller gCode responses ok
Controller gCode responses echo:N2 M204 T1000*82
Controller gCode responses Setting Travel Acceleration: 1000.00
Controller gCode responses ok
--> Machine moves are not set to accelerate @ 1000 mm / second^2
```

---
### emitAbsoluteMove(axis, position)

Configures the travel acceleration. Travel acceleration applies to combined axis moves and single axis moves.

#### axis {AXIS_NUMBER}
> Axis to move to home location

#### position {String}
> Position of the carriage

#### return value
> none

#### Example

```python
from _MachineMotion import *

# Define a callback to process controller gCode responses (if desired)
def templateCallback(data):
   print "Controller gCode responses " + data

machine_motion_example = MachineMotion(templateCallback, DEFAULT_IP_ADDRESS.usb_windows)

# Configuring the travel speed to 10 000 mm / min
machine_motion_example.emitSpeed(10000)

# Configuring the travel speed to 1000 mm / second^2
machine_motion_example.emitAcceleration(1000)

# Homing axis 1
machine_motion_example.emitHome(1)
machine_motion_example.waitForMotionCompletion()

# Move axis 1 to position "100 mm"
machine_motion_example.emitAbsoluteMove(1, 100)
machine_motion_example.waitForMotionCompletion()

print "--> Example completed."

```

#### Output
```
Controller gCode responses MachineMotion Session Start
Controller gCode responses echo:N0 M110 N0*125
Controller gCode responses ok
Controller gCode responses echo:N1 M111 S247*97
Controller gCode responses echo:DEBUG:ECHO,INFO,ERRORS,COMMUNICATION
Controller gCode responses ok
Controller gCode responses echo:N2 G0 F10000*124
Controller gCode responses ok
Controller gCode responses echo:N3 M204 T1000*83
Controller gCode responses Setting Travel Acceleration: 1000.00
Controller gCode responses ok
Controller gCode responses echo:N4 G28 X*111
Controller gCode responses echo:busy:processing
Controller gCode responses X:0.00 Y:0.00 Z:0.00 E:0.00 Count X: 0 Y:0 Z:0
Controller gCode responses ok
Controller gCode responses echo:N5 G90*21
Controller gCode responses ok
Controller gCode responses echo:N6 G0 X100*102
Controller gCode responses ok
--> Example completed.
```

---
### emitRelativeMove (axis, direction, distance)

Moves the gantry to a position relative to its current location.

#### axis {AXIS_NUMBER}
> Axis to be moved

#### direction {String}
> Motion direction

#### distance {Number}
> Distance to move in mm

#### return value
> none

#### Example

```python
from _MachineMotion import *

# Define a callback to process controller gCode responses (if desired)
def templateCallback(data):
   print "Controller gCode responses " + data

machine_motion_example = MachineMotion(templateCallback, DEFAULT_IP_ADDRESS.usb_windows)

# Configuring the travel speed to 10 000 mm / min
machine_motion_example.emitSpeed(10000)

# Configuring the travel speed to 1000 mm / second^2
machine_motion_example.emitAcceleration(1000)

# Homing axis 1
machine_motion_example.emitHome(1)

# Move axis 1 to position 100 mm
machine_motion_example.emitAbsoluteMove(1, 100)
machine_motion_example.waitForMotionCompletion()

# Move axis 1 by an increment of negative 100 mm
machine_motion_example.emitRelativeMove(1, "negative", 100)
machine_motion_example.waitForMotionCompletion()

print "--> Example completed."

```

#### Output
```
Controller gCode responses MachineMotion Session Start
Controller gCode responses echo:N0 M110 N0*125
Controller gCode responses ok
Controller gCode responses echo:N1 M111 S247*97
Controller gCode responses echo:DEBUG:ECHO,INFO,ERRORS,COMMUNICATION
Controller gCode responses ok
Controller gCode responses echo:N2 G0 F10000*124
Controller gCode responses ok
Controller gCode responses echo:N3 M204 T1000*83
Controller gCode responses Setting Travel Acceleration: 1000.00
Controller gCode responses ok
Controller gCode responses echo:N4 G28 X*111
Controller gCode responses X:0.00 Y:0.00 Z:0.00 E:0.00 Count X: 0 Y:0 Z:0
Controller gCode responses ok
Controller gCode responses echo:N5 G90*21
Controller gCode responses ok
Controller gCode responses echo:N6 G0 X100*102
Controller gCode responses ok
Controller gCode responses echo:N7 G91*22
Controller gCode responses ok
Controller gCode responses echo:N8 G0 X-100*69
--> Example completed.
Controller gCode responses ok
```

---
### emitgCode(gCode)

Sends a direct G-Code string command. See the G-Code Commands section for more details.

#### gCode {String}
> G-Code command to send to controller

#### return value
> none

#### Example

```python
from _MachineMotion import *

# Define a callback to process controller gCode responses (if desired)
def templateCallback(data):
   print "Controller gCode responses " + data

machine_motion_example = MachineMotion(templateCallback, DEFAULT_IP_ADDRESS.usb_windows)

# Configuring travel speed to 10 000 mm / min
machine_motion_example.emitSpeed(10000)

# Configuring travel speed to 1000 mm / second^2
machine_motion_example.emitAcceleration(1000)

# Homing axis 1
machine_motion_example.emitHome(1)
machine_motion_example.waitForMotionCompletion()

# Use the G0 command to move both axis 1 and two by 500mm at a travel speed of 10 000 mm / minute
machine_motion_example.emitgCode("G0 X500 Y500 F10000")
machine_motion_example.waitForMotionCompletion()

print "--> Example completed."

```

#### Output
```
Controller gCode responses MachineMotion Session Start
Controller gCode responses echo:N0 M110 N0*125
Controller gCode responses ok
Controller gCode responses echo:N1 M111 S247*97
Controller gCode responses echo:DEBUG:ECHO,INFO,ERRORS,COMMUNICATION
Controller gCode responses ok
Controller gCode responses echo:N2 G0 F10000*124
Controller gCode responses ok
Controller gCode responses echo:N3 M204 T1000*83
Controller gCode responses Setting Travel Acceleration: 1000.00
Controller gCode responses ok
Controller gCode responses echo:N4 G28 X*111
Controller gCode responses echo:busy: processing
Controller gCode responses X:0.00 Y:3000.00 Z:0.00 E:0.00 Count X: 0 Y:24000 Z:0
Controller gCode responses ok
Controller gCode responses echo:N5 V0*61
Controller gCode responses Motion Status = COMPLETED
Controller gCode responses ok
Controller gCode responses echo:N6 V0*62
Controller gCode responses Motion Status = COMPLETED
Controller gCode responses ok
Controller gCode responses echo:N7 G0 X50 Y50 F10000*120
Controller gCode responses ok
Controller gCode responses echo:N8 V0*48
Controller gCode responses Motion Status = IN_PROGRESS
Controller gCode responses ok
Controller gCode responses echo:N9 V0*49
Controller gCode responses Motion Status = IN_PROGRESS
Controller gCode responses ok
Controller gCode responses echo:N10 V0*9
Controller gCode responses Motion Status = IN_PROGRESS
Controller gCode responses ok
Controller gCode responses echo:N11 V0*8
Controller gCode responses Motion Status = IN_PROGRESS
Controller gCode responses ok
Controller gCode responses echo:N12 V0*11
Controller gCode responses Motion Status = IN_PROGRESS
Controller gCode responses ok
Controller gCode responses echo:N13 V0*10
Controller gCode responses Motion Status = COMPLETED
--> Example completed.
Controller gCode responses ok
```

## Control Device Functions

Functions that exchange data with the MachineMotion controller (no movement involved).

---
### attachControlDevice(port, device, callback)

Configures a control device on a specific MachineMotion port.

#### port {CONTROL_DEVICE_PORTS}
> Port on which the device is connected

#### device {CONTROL_DEVICE_TYPE}
> Type of device connected

#### callback {def callbackName(data):}
> Function to invoke once the data is available. The data will be passed to the callback as an argument (a serialized JSON string, specifically).

#### return value
> none

#### callback argument {String}
> Status message

#### Example

```python
from _MachineMotion import *

# Define a callback to process controller gCode responses (if desired)
def templateCallback(data):
   print "Controller gCode responses " + data
   
# Define a callback to invoke when a control device is attached to the controller
def attachControlDeviceCallback(data):
    print "Attach control device callback: " + data      

machine_motion_example = MachineMotion(templateCallback, DEFAULT_IP_ADDRESS.usb_windows)

# Attach a control device (in this case, an encoder) to the MachineMotion controller.
machine_motion_controller.attachControlDevice("SENSOR4","ENCODER", attachControlDeviceCallback)

```

---
### detachControlDevice(port, callback)

Deconfigure a control device on a specific MachineMotion port.

#### port {CONTROL_DEVICE_PORTS}
> Port at which the device is connected

#### callback {def callbackName(data):}
> Function to invoke once the data is available. The data will be passed to the callback as an argument (a serialized JSON string).

#### return value
> none

#### callback argument {String}
> Status message 

#### Example

```python
from _MachineMotion import *

# Define a callback to process controller gCode responses (if desired)
def templateCallback(data):
   print "Controller gCode responses " + data
   
# Define a callback to invoke when a control device is attached to the controller
def attachControlDeviceCallback(data):
    print "Attach control device callback: " + data   

# Define a callback to invoke when a control device is detached from the controller    
def detachControlDeviceCallback(data):
    print "Detach control device callback: " + data     

machine_motion_example = MachineMotion(templateCallback, DEFAULT_IP_ADDRESS.usb_windows)

# Attach a control device (an encoder in this case) to the MachineMotion controller.
machine_motion_controller.attachControlDevice("SENSOR4","ENCODER", attachControlDeviceCallback)

# Some other code here ...

# Detach (deconfigure) a control device that was previously attached to the MachineMotion controller.
machine_motion_controller.detachControlDevice("SENSOR4", detachControlDeviceCallback)

```

---
### readControlDevice(port, signal, callback)

Read a given signal on a control device on a specific MachineMotion port.

#### port {CONTROL_DEVICE_PORTS}
> Port on which the device is connected

#### signal {CONTROL_DEVICE_SIGNALS}
> Signal to read on the device

#### callback {def callbackName(data):}
> Function to invoke once the data is available. The data will be passed to the callback as an argument (a serialized JSON string).

#### return value
> none

#### callback argument {serialized JSON String}
> { port:   "port",
    signal: "signal",
    value:  "value read",
    error:  "error message“}

#### Example

```python
from _MachineMotion import *

# Define a callback to process controller gCode responses (if desired)
def templateCallback(data):
   print "Controller gCode responses " + data
   
# Define a callback to invoke when a control device is attached to the controller
def attachControlDeviceCallback(data):
    print "Attach control device callback: " + data   

# Define a callback to invoke when a control device is detached from the controller    
def detachControlDeviceCallback(data):
    print "Detach control device callback: " + data     

# Define a callback to invoke when a control device is read    
def readControlDeviceCallback(data):
    print "Read control device callback: " + data      

machine_motion_example = MachineMotion(templateCallback, DEFAULT_IP_ADDRESS.usb_windows)

# Attach a control device (in this case, and encoder) to the MachineMotion controller.
machine_motion_controller.attachControlDevice("SENSOR4","ENCODER", attachControlDeviceCallback)

count = 0

for count in range (0, 100):

    # Read the signal of a control device. SIGNAL0 of the encoder returns the relative position in turns. The encoder resets its position to 0 at power-on. Position is given in turns.
    machine_motion_controller.readControlDevice("SENSOR4", "SIGNAL0", readControlDeviceCallback)

    time.sleep(1)

# Detach (deconfigure) a control device that was previously attached to the MachineMotion controller.
machine_motion_controller.detachControlDevice("SENSOR4", detachControlDeviceCallback)

```

---
### writeControlDevice(port, signal, callback)

Deconfigures a control device at a specific MachineMotion port.

#### port {CONTROL_DEVICE_PORTS}
> Port at which the device is connected

#### signal {CONTROL_DEVICE_SIGNALS}
> Signal to read on the device

#### callback argument {JSON formatted String}
> { port: "port",
    signal: "signal",
    value: "value read",
    error: "error message“}

#### Example

```python
from _MachineMotion import *

# Define a callback to process controller gCode responses (if desired)
def templateCallback(data):
   print "Controller gCode responses " + data
   
# Define a callback to invoke when a control device is attached to the controller
def attachControlDeviceCallback(data):
    print "Attach control device callback: " + data   

# Define a callback to invoke when a control device is detached from the controller    
def detachControlDeviceCallback(data):
    print "Detach control device callback: " + data    
    
# Define a callback to invoke when a control device is read    
def readControlDeviceCallback(data):
    print "Read control device callback: " + data   

# Define a callback to invoke when a control device is written
def writeControlDeviceCallback(data):
    print "Write control device callback: " + data 

machine_motion_example = MachineMotion(templateCallback, DEFAULT_IP_ADDRESS.usb_windows)

# Attach a control device (in this case, an encoder) to the MachineMotion controller.
machine_motion_controller.attachControlDevice("SENSOR4","IO_EXPANDER_GENERIC", attachControlDeviceCallback)

count = 0

for count in range (0, 100):

    # Read the signal of a control device. SIGNAL0 of the IO expander, which returns True or False depending on the state of the IO.
    machine_motion_controller.readControlDevice("SENSOR4", "SIGNAL0", readControlDeviceCallback)

    time.sleep(1)
    
    # Write the signal of a control device (here, SIGNAL0 of the IO expander).
    machine_motion_controller.writeControlDevice("SENSOR4", "SIGNAL0", writeControlDeviceCallback)    
    
    time.sleep(1)

# Detach (deconfigure) a control device that was previously attached to the MachineMotion controller.
machine_motion_controller.detachControlDevice("SENSOR4", detachControlDeviceCallback)

```


## Executing Python Programs

- Open the command prompt (for Windows) or terminal (for Mac and Linux).

- Browse to the directory where you program is saved. 

- Execute your program.
    ```bash 
    python yourProgram.py
    ```

- The console or terminal will display various status messages while the program runs.

- To stop the execution of the program, press CRTL + c

## G-Code

### Sending G-Code

G-Code is a text based protocol that controls the motion of multi axis machines. The API presented in the previous section employs it to communicate motion-related commands to the MachineMotion controller

More advanced users might wish to use commands that are available via the G-Code protocol. The emitgCode **(gCode)** function presented in _Table 6_ can be used.

### G-Code Reference

The MachineMotion Python Library Package contains a list of G-Code commands available for advanced users. You can also download it here: <a href="https://www.vention.io/" target="_blank">G-Code Reference Functions</a>.

Below, we've listed some handy G-Code commands that can be utilized via the emitgCode function.

#### Configuration Functions

<div class="markdown-body" style="font-family:Larsseit; display: table;">

| **G-Code Function ID** | **Description** | 
| --- | :--- |
| M201 | Set Max Acceleration |
| M203 | Set Max Feedrate |
| M204 | Set Acceleration |
| G0 & G1 | Set Feedrate (Travel Speed) |

</div>

<p style="text-align: center;"><span style="color: #808080; font-size: 11pt;"><em>Table 1: G-Code Configuration Functions</em></p>

#### Control Functions

<div class="markdown-body" style="font-family:Larsseit; display: table;">

| **G-Code Function ID** | **Description** | 
| --- | :--- |
| G90 | Set Absolute Motion |
| G91 | Set Relative Motion |
| G0  | Linear Move |
| G28 | Home |

</div>

<p style="text-align: center;"><span style="color: #808080; font-size: 11pt;"><em>Table 2: G-Code Control Functions</em></p>

#### Communication Functions

<div class="markdown-body" style="font-family:Larsseit; display: table;">

| **G-Code Function ID** | **Description** | 
| --- | :--- |
| M114 | Get Current Position |
| M119 | GEt EndStop States |

</div>

<p style="text-align: center;"><span style="color: #808080; font-size: 11pt;"><em>Table 3: G-Code Communication Functions</em></p>

**Note on Axis Mapping**

Note that when using direct G-Code commands, the axis name mapping in *Table 4* applies.

<div class="markdown-body" style="font-family:Larsseit; display: table;">

| **G-Code Axis Name** | **MachineMotion Axis Name** | 
| :---: | :---: |
| X | 1 |  
| Y | 2 | 
| z | 3 | 

</div>

<p style="text-align: center;"><span style="color: #808080; font-size: 11pt;"><em>Table 4: G-Code to MachineMotion Axis Mapping.</em></p>
