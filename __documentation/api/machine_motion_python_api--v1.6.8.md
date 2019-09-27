# MachineMotion Python API

## Configuration Functions

When creating a Python program to control the MachineMotion controller, the first step is always to create a MachineMotion objcet. This will establish communication with the actual controller and expose different functions that can be used to send commands.

After creating the MachineMotion instance, you must configure its axes. The functions to perform these steps are covered in this section.

---
### MachineMotion(callback, ip)

Creates a MachineMotion instance and establishes the TCP/IP communication. This function is a constructor.

#### callback {def callbackName(data):}  
> Handle in which incoming messages from the controller can be processed. The data passed to the callback is of String type.

#### ip {string}

> IP address of the MachineMotion controller.

#### return value {MachineMotion}
> Instance created by the constructor.

#### Reference Example
> example--MachineMotion.py

```python
from _MachineMotion_1_6_8 import *

# Define a callback to process controller gCode responses if desired. This is mostly used for debugging purposes.
def debug(data):
    pass

print ("Application Message: MachineMotion Program Starting \n")

mm = MachineMotion(debug, DEFAULT_IP_ADDRESS.usb_windows)
print ("Application Message: MachineMotion Controller Connected \n")

print ("Application Message: Program terminating ... \n")
time.sleep(1)
sys.exit(0)

```
---
### configMachineMotionIp(mode, ip, netmask, gateway)
> Configures the IP address of the controller Ethernet interface.

#### mode {NETWORK_MODE}
> IP configures the network management profile as either static or dhcp.

#### ip {String}
> Desired static IP address to assign to the MachineMotion controller. Format is "nnn.nnn.nnn.nnnn", where n are numbers.

#### netmask {String}
> Network netmask. Format is "nnn.nnn.nnn.nnnn", where n are numbers.

#### gateway {String}
> IP address of the network gateway. Format is "nnn.nnn.nnn.nnnn", where n are numbers.
    
#### return value
> none

####  Reference Example
> example--configMachineMotionIp.py

```python
from _MachineMotion_1_6_8 import *

# Define a callback to process controller gCode responses if desired. This is mostly used for debugging purposes.
def debug(data):
    pass

print ("Application Message: MachineMotion Program Starting \n")

mm = MachineMotion(debug, DEFAULT_IP_ADDRESS.usb_windows)
print ("Application Message: MachineMotion Controller Connected \n")

# Setting the ETHERNET port of the controller in static mode
mm.configMachineMotionIp(NETWORK_MODE.static, "192.168.0.2", "255.255.255.0", "192.168.0.1")
print ("Application Message: Ethernet Port Configured \n")

print ("Application Message: Program terminating ... \n")
time.sleep(1)
sys.exit(0)
```

#### Reference Example
> example--configMachineMotionIp_2.py

```python
from _MachineMotion_1_6_8 import *

# Define a callback to process controller gCode responses if desired. This is mostly used for debugging purposes.
def debug(data):
    pass

print ("Application Message: MachineMotion Program Starting \n")

mm = MachineMotion(debug, DEFAULT_IP_ADDRESS.usb_windows)
print ("Application Message: MachineMotion Controller Connected \n")

# Setting the ETHERNET port of the controller in dhcp mode
mm.configMachineMotionIp(NETWORK_MODE.dhcp, "", "", "")
print ("Application Message: Ethernet Port Configured \n")

print ("Application Message: Program terminating ... \n")
time.sleep(1)
sys.exit(0)
```

---
### configAxis(axis, u_step, mech_gain)
> Configure the axis' mechanical gain and micro-step settings to ensure accurate motion.

#### axis {Number}
> Axis to configure

#### u_step {MICRO_STEPS}
> Micro-step setting

#### mech_gain {MECH_GAIN}
> Mechanical gain of the axis in mm per turn.

#### return value
> None

#### Reference Example
> example--configAxis.py

```python
from _MachineMotion_1_6_8 import *

# Define a callback to process controller gCode responses if desired. This is mostly used for debugging purposes.
def debug(data):
    pass

print ("Application Message: MachineMotion Program Starting \n")

mm = MachineMotion(debug, DEFAULT_IP_ADDRESS.usb_windows)
print ("Application Message: MachineMotion Controller Connected \n")

# Configure the axis number 1, 8 uSteps and 150 mm / turn for a timing belt
mm.configAxis(1, MICRO_STEPS.ustep_8, MECH_GAIN.timing_belt_150mm_turn)
print ("Application Message: MachineMotion axis 1 configured \n")

print ("Application Message: Program terminating ... \n")
time.sleep(1)
sys.exit(0)
```

---
### setPosition(axis, position)
> Function to force set the position of the motion controller for one specific axis

#### axis {Number}
> Axis to configure

#### position {Number}
> Position to set the axis to


#### return value
> none

#### Reference Example
> example--setPosition.py

```python
from _MachineMotion_1_6_8 import *

# Define a callback to process controller gCode responses if desired. This is mostly used for debugging purposes.
def debug(data):
    pass

print ("Application Message: MachineMotion Program Starting \n")

mm = MachineMotion(debug, DEFAULT_IP_ADDRESS.usb_windows)
print ("Application Message: MachineMotion Controller Connected \n")

# Configure the axis number 1, 8 uSteps and 150 mm / turn for a timing belt
mm.configAxis(1, MICRO_STEPS.ustep_8, MECH_GAIN.timing_belt_150mm_turn)
print ("Application Message: MachineMotion axis 1 configured \n")

# Instead of homing we set the position to 100, so we can move the axis in the reverse direction right after power-on.
mm.setPosition(1, 100)
print ("Application Message: Position set to 100 mm on axis 1\n")

mm.moveRelative(1, "negative", 50)
print ("Application Message: Moving in the negative direction ... \n")

mm.waitForMotionCompletion()
print ("Application Message: Motion completed \n")

print ("Application Message: Program terminating ... \n")
time.sleep(1)
sys.exit(0)
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

#### Reference Example
> example--saveData_getData.py

```python
from _MachineMotion_1_6_8 import *

# Define a callback to process controller gCode responses if desired. This is mostly used for debugging purposes.
def debug(data):
    pass
    
print ("Application Message: MachineMotion Program Starting \n")
    
# Define a callback to print the data retrieved using the getData function
def printGetDataResult(data):

    dictionary = json.loads(data)

    print ( "Application Message: Retrieved file name = " + dictionary["fileName"] + "\n" )
    
    print ( "Application Message: Retrieved data = " + dictionary["data"]  + "\n")

mm = MachineMotion(debug, DEFAULT_IP_ADDRESS.usb_windows)
print ("Application Message: MachineMotion Controller Connected \n")

# Saving a string on the controller
mm.saveData("data_1", "save_this_string_on_the_controller")

print ("Application Message: Data saved \n")

# Reading a string from the controller
mm.getData("data_1", printGetDataResult)

print ("Application Message: Program terminating ... \n")
time.sleep(1)
sys.exit(0)
```
---
### getData(key, callback)
> Retrieve a key-value pair that was saved on the controller.

#### key {String}
> key is a string that identifies the data to retrieve.


#### callback {def callbackName(data):}
> Function to invoke once the data is available. The data will be passed to the callback as an argument—specifically, as a serialized JSON string.

#### Reference Example
> example--saveData_getData.py

```python
from _MachineMotion_1_6_8 import *

# Define a callback to process controller gCode responses if desired. This is mostly used for debugging purposes.
def debug(data):
    pass
    
print ("Application Message: MachineMotion Program Starting \n")
    
# Define a callback to print the data retrieved using the getData function
def printGetDataResult(data):

    dictionary = json.loads(data)

    print ( "Application Message: Retrieved file name = " + dictionary["fileName"] + "\n" )
    
    print ( "Application Message: Retrieved data = " + dictionary["data"]  + "\n")

mm = MachineMotion(debug, DEFAULT_IP_ADDRESS.usb_windows)
print ("Application Message: MachineMotion Controller Connected \n")

# Saving a string on the controller
mm.saveData("data_1", "save_this_string_on_the_controller")

print ("Application Message: Data saved \n")

# Reading a string from the controller
mm.getData("data_1", printGetDataResult)

print ("Application Message: Program terminating ... \n")
time.sleep(1)
sys.exit(0)
```

## Motion Functions

---
### waitForMotionCompletion()
> Blocking function that prevents program execution until last motion has completed. Until the machine has not finished its final movement, the code will not be executed.

#### return value
> none

#### Reference Example
> example--waitForMotionCompletion.py

```python
from _MachineMotion_1_6_8 import *

# Define a callback to process controller gCode responses if desired. This is mostly used for debugging purposes.
def debug(data):
    pass
    
print ("Application Message: MachineMotion Program Starting \n")

mm = MachineMotion(debug, DEFAULT_IP_ADDRESS.usb_windows)
print ("Application Message: MachineMotion Controller Connected \n")

# Homing axis one
mm.emitHome(1)
print ("Application Message: Axis 1 is at home \n")

# Move the axis one to position 100 mm
mm.emitAbsoluteMove(1, 100)
print ("Application Message: Motion on-going ... \n")

# This function call waits for the motion to be completed before returning
mm.waitForMotionCompletion()
print ("Application Message: Motion has completed \n")

print ("Application Message: Program terminating \n")
time.sleep(1)
sys.exit(0)
```

---
### emitStop()
 > Immediately stops motion on all axes.

#### return value
> none


#### Reference Example
> example--emitStop.py

```python
from _MachineMotion_1_6_8 import *

import datetime

# Define a callback to process controller gCode responses if desired. This is mostly used for debugging purposes.
def debug(data):
    pass

print ("Application Message: MachineMotion Program Starting \n")
    
mm = MachineMotion(debug, DEFAULT_IP_ADDRESS.usb_windows)
print ("Application Message: MachineMotion Controller Connected \n")

# Configure the axis number 1, 8 uSteps and 150 mm / turn for a timing belt
mm.configAxis(1, MICRO_STEPS.ustep_8, 150)
print ("Application Message: MachineMotion axis 1 configured \n")

# Homing axis 1
mm.emitHome(1)
print ("Application Message: Axis 1 at home \n")

# Configuring the travel speed to 100 mm / minute
mm.emitSpeed(100)
print ("Application Message: Speed configured \n")

# Move the axis one to position 100 mm
mm.emitRelativeMove(1, "positive", 100)
print ("Application Message: Move on-going ... \n")

time.sleep(2)
print ("Application Message: Waiting for 2 seconds ... \n")

# Instruct the controller to stop all motion immediately
mm.emitStop()
print ("Application Message: Motion stopped! \n")

print ("Application Message: Program terminating ... \n")
time.sleep(1)
sys.exit(0)
```

---
### emitHomeAll()
> Moves all carriages to their home location sequentially, axis 1 to axis 3. This is a blocking function and will return only on completion of the operation on the machine.

#### return value
> none

#### Reference Example
> _example--emitHomeAll.py

```python
from _MachineMotion_1_6_8 import *

# Define a callback to process controller gCode responses if desired. This is mostly used for debugging purposes.
def debug(data):
    pass

print ("Application Message: MachineMotion Program Starting \n")

mm = MachineMotion(debug, DEFAULT_IP_ADDRESS.usb_windows)
print ("Application Message: MachineMotion Controller Connected \n")

# Configure the axis number 1, 8 uSteps and 150 mm / turn for a timing belt
mm.configAxis(1, MICRO_STEPS.ustep_8, MECH_GAIN.timing_belt_150mm_turn)
print ("Application Message: Axis 1 configured \n")

# Configure the axis number 2, 8 uSteps and 150 mm / turn for a timing belt
mm.configAxis(2, MICRO_STEPS.ustep_8, MECH_GAIN.timing_belt_150mm_turn)
print ("Application Message: Axis 2 configured \n")

# Configure the axis number 3, 8 uSteps and 150 mm / turn for a timing belt
mm.configAxis(3, MICRO_STEPS.ustep_8, MECH_GAIN.timing_belt_150mm_turn)
print ("Application Message: Axis 3 configured \n")

# Homing all the axes of the controller sequentially
mm.emitHomeAll()
print ("Application Message: All axes are at home \n")

print ("Application Message: Program terminating ... \n")
time.sleep(1)
sys.exit(0)
```

---
### emitHome(axis)

Moves the carriage of the corresponding axis to its home location. This is a blocking function and will return only on completion of the operation on the machine.


#### axis {AXIS_NUMBER}
> Axis to move to home location

#### return value
> none

#### Reference Example
> example--emitHome.py

```python
from _MachineMotion_1_6_8 import *

# Define a callback to process controller gCode responses if desired. This is mostly used for debugging purposes.
def debug(data):
    pass

print ("Application Message: MachineMotion Program Starting \n")

mm = MachineMotion(debug, DEFAULT_IP_ADDRESS.usb_windows)
print ("Application Message: MachineMotion Controller Connected \n")

# Configure the axis number 1, 8 uSteps and 150 mm / turn for a timing belt
mm.configAxis(1, MICRO_STEPS.ustep_8, MECH_GAIN.timing_belt_150mm_turn)
print ("Application Message: Axis 1 configured \n")

# Homing axis 1
mm.emitHome(1)
print ("Application Message: Axis 1 at home \n")

print ("Application Message: Program terminating ... \n")
time.sleep(1)
sys.exit(0)
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
from _MachineMotion_1_6_8 import *

# Define a callback to process controller gCode responses if desired. This is mostly used for debugging purposes.
def debug(data):
    pass

print ("Application Message: MachineMotion Program Starting \n")

mm = MachineMotion(debug, DEFAULT_IP_ADDRESS.usb_windows)
print ("Application Message: MachineMotion Controller Connected \n")

# Configuring the travel speed to 1000 mm / minute
mm.emitSpeed(1000)
print ("Application Message: Speed configured \n")

print ("Application Message: Program terminating ... \n")
time.sleep(1)
sys.exit(0)
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
from _MachineMotion_1_6_8 import *

# Define a callback to process controller gCode responses if desired. This is mostly used for debugging purposes.
def debug(data):
    pass

print ("Application Message: MachineMotion Program Starting \n")

mm = MachineMotion(debug, DEFAULT_IP_ADDRESS.usb_windows)
print ("Application Message: MachineMotion Controller Connected \n")

# Configure the axis number 1, 8 uSteps and 150 mm / turn for a timing belt
mm.configAxis(1, MICRO_STEPS.ustep_8, MECH_GAIN.timing_belt_150mm_turn)
print ("Application Message: MachineMotion Axis 1 Configured \n")

# Configuring the travel acceleration to 100 mm / second^2
mm.emitAcceleration(100)
print ("Application Message: Acceleration configured \n")

print ("Application Message: Program terminating ... \n")
time.sleep(1)
sys.exit(0)
```

---
### emitAbsoluteMove(axis, position)

> Sends an absolute move command to the MachineMotion controller

#### axis {AXIS_NUMBER}
> Axis to move to home location

#### position {String}
> Position of the carriage

#### return value
> none

#### Reference Example
> example--emitAbsoluteMove.py

```python
from _MachineMotion_1_6_8 import *

# Define a callback to process controller gCode responses if desired. This is mostly used for debugging purposes.
def debug(data):
    pass

print ("Application Message: MachineMotion Program Starting \n")

mm = MachineMotion(debug, DEFAULT_IP_ADDRESS.usb_windows)
print ("Application Message: MachineMotion Controller Connected \n")

# Configure the axis number 1, 8 uSteps and 150 mm / turn for a timing belt
mm.configAxis(1, MICRO_STEPS.ustep_8, MECH_GAIN.timing_belt_150mm_turn)
print ("Application Message: MachineMotion Axis 1 Configured \n")

# Configuring the travel speed to 10000 mm / min
mm.emitSpeed(10000)
print ("Application Message: Speed configured \n")

# Configuring the travel speed to 1000 mm / second^2
mm.emitAcceleration(1000)
print ("Application Message: Acceleration configured \n")

# Homing axis 1
mm.emitHome(1)
print ("Application Message: Axis 1 is at home \n")

# Move the axis 1 to position 100 mm
mm.emitAbsoluteMove(1, 100)
print ("Application Message: Motion on-going ... \n")

mm.waitForMotionCompletion()
print ("Application Message: Motion completed \n")

print ("Application Message: Program terminating ... \n")
time.sleep(1)
sys.exit(0)
```

---
### emitCombinedAbsoluteMove(axes, positions)

> Send an absolute move command to the MachineMotion controller. Moves multiple axis simultaneously.

#### axes {array of numbers}
> Axes to move

#### positions {array of numbers}
> Position to move the axes to

#### return value
> none

#### Reference Example
> example--emitCombinedAbsoluteMove.py

```python
from _MachineMotion_1_6_8 import *

# Define a callback to process controller gCode responses if desired. This is mostly used for debugging purposes.
def debug(data):
    pass

print ("Application Message: MachineMotion Program Starting \n")

mm = MachineMotion(debug, DEFAULT_IP_ADDRESS.usb_windows)
print ("Application Message: MachineMotion Controller Connected \n")

# Configure the axis number 1, 8 uSteps and 150 mm / turn for a timing belt
mm.configAxis(1, MICRO_STEPS.ustep_8, MECH_GAIN.timing_belt_150mm_turn)
print ("Application Message: MachineMotion Axis 1 Configured \n")

# Configuring the travel speed to 10000 mm / min
mm.emitSpeed(10000)
print ("Application Message: Speed configured \n")

# Configuring the travel speed to 1000 mm / second^2
mm.emitAcceleration(1000)
print ("Application Message: Acceleration configured \n")

# Homing axis 1
mm.emitHome(1)
print ("Application Message: Axis 1 is at home \n")

# Move the axis 1 to position 100 mm
mm.emitCombinedAbsoluteMove([1, 2, 3], [100, 200, 100])
print ("Application Message: Motion on-going ... \n")

mm.waitForMotionCompletion()
print ("Application Message: Motion completed \n")

print ("Application Message: Program terminating ... \n")
time.sleep(1)
sys.exit(0)
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
from _MachineMotion_1_6_8 import *

# Define a callback to process controller gCode responses if desired. This is mostly used for debugging purposes.
def debug(data):
    pass

print ("Application Message: MachineMotion Program Starting \n")

mm = MachineMotion(debug, DEFAULT_IP_ADDRESS.usb_windows)
print ("Application Message: MachineMotion Controller Connected \n")

# Configure the axis number 1, 8 uSteps and 150 mm / turn for a timing belt
mm.configAxis(1, MICRO_STEPS.ustep_8, MECH_GAIN.timing_belt_150mm_turn)
print ("Application Message: MachineMotion Axis 1 Configured \n")

# Configuring the travel speed to 10000 mm / min
mm.emitSpeed(10000)
print ("Application Message: Speed configured \n")

# Configuring the travel speed to 1000 mm / second^2
mm.emitAcceleration(1000)
print ("Application Message: Acceleration configured \n")

# Homing axis 1
mm.emitHome(1)
print ("Application Message: Axis 1 at home \n")

# Move the axis one to position 100 mm
mm.emitRelativeMove(1, "positive", 100)
print ("Application Message: Move on-going ... \n")

mm.waitForMotionCompletion()
print ("Application Message: Motion completed \n")

print ("Application Message: Program terminating ... \n")
time.sleep(1)
sys.exit(0)
```

---
### emitCombinedAxisRelativeMove(axes, directions, distances)

> Send a relative move command to the MachineMotion controller. Moves multiple axis simultaneously.

#### axes {array of numbers}
> Axes to move

#### directions {list of strings of value equal to "positive" or "negative"}
> Motion direction for each axis

#### distances {array of numbers}
> Distances to move for each axis

#### return value
> none

#### Reference Example
> example--emitCombinedRelativeMove.py

```python
from _MachineMotion_1_6_8 import *

# Define a callback to process controller gCode responses if desired. This is mostly used for debugging purposes.
def debug(data):
    pass

print ("Application Message: MachineMotion Program Starting \n")

mm = MachineMotion(debug, DEFAULT_IP_ADDRESS.usb_windows)
print ("Application Message: MachineMotion Controller Connected \n")

# Configure the axis number 1, 8 uSteps and 150 mm / turn for a timing belt
mm.configAxis(1, MICRO_STEPS.ustep_8, MECH_GAIN.timing_belt_150mm_turn)
print ("Application Message: MachineMotion Axis 1 Configured \n")

# Configuring the travel speed to 10000 mm / min
mm.emitSpeed(10000)
print ("Application Message: Speed configured \n")

# Configuring the travel speed to 1000 mm / second^2
mm.emitAcceleration(1000)
print ("Application Message: Acceleration configured \n")

# Homing axis 1
mm.emitHome(1)
print ("Application Message: Axis 1 at home \n")

# Move the axis one to position 100 mm
mm.emitCombinedRelativeMove([1,2,3], ["positive","positive","positive"], [100, 200, 300])
print ("Application Message: Multi-axis move on-going ... \n")

mm.waitForMotionCompletion()
print ("Application Message: Motion completed \n")

print ("Application Message: Program terminating ... \n")
time.sleep(1)
sys.exit(0)
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
from _MachineMotion_1_6_8 import *

# Define a callback to process controller gCode responses if desired. This is mostly used for debugging purposes.
def debug(data):
    pass

print ("Application Message: MachineMotion Program Starting \n")

mm = MachineMotion(debug, DEFAULT_IP_ADDRESS.usb_windows)
print ("Application Message: MachineMotion Controller Connected \n")

# Configure the axis number 1, 8 uSteps and 150 mm / turn for a timing belt
mm.configAxis(1, MICRO_STEPS.ustep_8, MECH_GAIN.timing_belt_150mm_turn)
print ("Application Message: MachineMotion axis 1 configured \n")

# Configure the axis number 2, 8 uSteps and 150 mm / turn for a timing belt
mm.configAxis(2, MICRO_STEPS.ustep_8, MECH_GAIN.timing_belt_150mm_turn)
print ("Application Message: MachineMotion axis 2 configured \n")

# Configuring the travel speed to 10000 mm / min
mm.emitSpeed(10000)
print ("Application Message: Speed configured \n")

# Configuring the travel speed to 1000 mm / second^2
mm.emitAcceleration(1000)
print ("Application Message: Acceleration Configured \n")

# Homing axis 1
mm.emitHome(1)
print ("Application Message: Axis 1 at home \n")

# Homing axis 2
mm.emitHome(2)
print ("Application Message: Axis 2 at home \n")

# Use the G0 command to move both axis 1 and 2 by 50mm at a travel speed of 10000 mm / minute
mm.emitgCode("G0 X50 Y50 F10000")
print ("Application Message: Motion on-going ... \n")

mm.waitForMotionCompletion()
print ("Application Message: Motion completed \n")

print ("Application Message: Program terminating ... \n")
time.sleep(1)
sys.exit(0)
```

## Control Device Functions

Functions that exchange data with the MachineMotion controller (no movement involved).

#### Important Notes: Digital IO Module

##### Address vs Port 

<div class="markdown-body" style="font-family:Larsseit; display: table;">

| **Digital IO Module Address** | **Port to Utilize** | 
| :---: | :---: |
| 1 | SENSOR4 |
| 2 | SENSOR5 |
| 3 | SENSOR6 |

</div>

##### Inputs vs Signal

<div class="markdown-body" style="font-family:Larsseit; display: table;">

| **Input Number to Read** | **Signal to Utilize** | 
| :---: | :---: |
| 1 | SIGNAL4 |
| 2 | SENSOR5 |
| 3 | SENSOR6 |
| 4 | SENSOR7 |

</div>

##### Outputs vs Signal

<div class="markdown-body" style="font-family:Larsseit; display: table;">

| **Output Number to Write** | **Signal to Utilize** | 
| :---: | :---: |
| 1 | SIGNAL0 |
| 2 | SENSOR1 |
| 3 | SENSOR2 |
| 4 | SENSOR3 |

</div>

#### Important Notes: Encoders

##### Port Selection

If your controller's blue front panel ports are labelled SENSOR4,SENSOR5, SENSOR6, simply use the port that the encoder is connected to.

If your controller's blue front panel ports are labelled AUX1, AUX2, AUX3 use the port mapping below.

<div class="markdown-body" style="font-family:Larsseit; display: table;">

| **Output Number to Write** | **Signal to Utilize** | 
| :---: | :---: |
| AUX1 | SENSOR4 |
| AUX2 | SENSOR5 |
| AUX3 | SENSOR6 |

</div>

When reading an encoder position value use SIGNAL0.

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

#### Reference Example (Encoder)
> example--readControlDevice--writeControlDevice--encoder.py

```python
from _MachineMotion_1_6_8 import *

# Define a callback to process controller gCode responses if desired. This is mostly used for debugging purposes.
def debug(data):
    pass
   
# Define a callback to invoke when a control device is attached to the controller
def attachCallback(data):
    print ("Application Message: attachCallback invoked. Message received = " + json.loads(data)["message"] + " \n");

# Define a callback to invoke when a control device is detached from the controller    
def detachCallback(data):
    print ("Application Message: detachCallback invoked. Message received = " + json.loads(data)["message"] + " \n");

# Define a callback to invoke when a control device is read    
def readCallback(data):    
    print ( "Application Message: readCallback invoked. Message received = " + data + " \n" )
    
print ("Application Message: MachineMotion Program Starting \n")

# Creating a MachineMotion instance
mm = MachineMotion(debug, DEFAULT_IP_ADDRESS.usb_windows)
print ("Application Message: MachineMotion Controller Connected \n")

# Attach a control device (in this case an encoder) to the MachineMotion controller.
# Encoder connected to port "SENSOR4" (now labelled "AUX1" on new controllers)
mm.attachControlDevice("SENSOR4",CONTROL_DEVICE_TYPE.ENCODER, attachCallback)
print ("Application Message: Encoder attached \n")

def readPosition():
    # SIGNAL0 corresponds to the number of rotations
    mm.readControlDevice("SENSOR4", "SIGNAL0", readCallback)
    time.sleep(0.1)

# Configuring the travel speed to 600 mm / min
mm.emitSpeed(600)
print ("Application Message: Speed configured \n")

# Configuring the travel speed to 1000 mm / second^2
mm.emitAcceleration(1000)
print ("Application Message: Acceleration configured \n")

# Homing axis 1
mm.emitHome(1)
print ("Application Message: Axis 1 at home \n")

time.sleep(0.5)

readPosition()

# Move the axis one to position 100 mm
mm.emitRelativeMove(1, "positive", 100)
print ("Application Message: Move on-going ... \n")

count = 0

for count in range (0, 10):

    readPosition()
    
    time.sleep(1)

# Detach (deconfigure) a control device that was previously attached to the MachineMotion controller.
mm.detachControlDevice("SENSOR4", detachCallback)

print ("Application Message: Program terminating ... \n")
time.sleep(1)
sys.exit(0)
```

#### Reference Example (Digital IO Module)
> example--readControlDevice--writeControlDevice--digital_io_module.py

```python
from _MachineMotion_1_6_8 import *

# Define a callback to process controller gCode responses if desired. This is mostly used for debugging purposes.
def debug(data):
    pass
   
# Define a callback to invoke when a control device is attached to the controller
def attachCallback(data):
    print ("Application Message: attachCallback invoked. Message received = " + json.loads(data)["message"] + " \n");

# Define a callback to invoke when a control device is detached from the controller    
def detachCallback(data):
    print ("Application Message: detachCallback invoked. Message received = " + json.loads(data)["message"] + " \n");

# Define a callback to invoke when a control device is read    
def readCallback(data):    
    print ( "Application Message: readCallback invoked. Message received = " + data + " \n" )

# Define a callback to invoke when a control device is written    
def writeCallback(data):
    print ( "Application Message: writeCallback invoked. Message received = " + data + " \n" )

print ("Application Message: MachineMotion Program Starting \n")

# Creating a MachineMotion instance
mm = MachineMotion(debug, DEFAULT_IP_ADDRESS.usb_windows)
print ("Application Message: MachineMotion Controller Connected \n")

# Attach a control device (in this case a digital IO module) to the MachineMotion controller
# Digital IO Module connected to port "SENSOR4" which corresponds to address 1
mm.attachControlDevice("SENSOR4",CONTROL_DEVICE_TYPE.IO_EXPANDER_GENERIC, attachCallback)
print ("Application Message: Digital IO Module configured \n")

count = 0

def readInputs():
    # Read a control device (in this case a digital IO module)
    # Port "SENSOR4" corresponds to address 1
    # SIGNAL4 corresponds to INPUT1
    mm.readControlDevice("SENSOR4", "SIGNAL4", readCallback)
    time.sleep(0.1)

    # SIGNAL5 corresponds to INPUT2
    mm.readControlDevice("SENSOR4", "SIGNAL5", readCallback)
    time.sleep(0.1)

    # SIGNAL6 corresponds to INPUT3
    mm.readControlDevice("SENSOR4", "SIGNAL6", readCallback)
    time.sleep(0.1)
    
    # SIGNAL7 corresponds to INPUT4
    mm.readControlDevice("SENSOR4", "SIGNAL7", readCallback)
    time.sleep(0.1)

def readOutputs():
    # Read a control device (in this case a digital IO module)
    # Port "SENSOR4" corresponds to address 1
    # SIGNAL4 corresponds to INPUT1
    mm.readControlDevice("SENSOR4", "SIGNAL0", readCallback)
    time.sleep(0.1)

    # SIGNAL5 corresponds to INPUT2
    mm.readControlDevice("SENSOR4", "SIGNAL1", readCallback)
    time.sleep(0.1)

    # SIGNAL6 corresponds to INPUT3
    mm.readControlDevice("SENSOR4", "SIGNAL2", readCallback)
    time.sleep(0.1)
    
    # SIGNAL7 corresponds to INPUT4
    mm.readControlDevice("SENSOR4", "SIGNAL3", readCallback)
    time.sleep(0.1)

def writeOutputs():

    # SIGNAL0 corresponds to OUTPUT1
    mm.writeControlDevice("SENSOR4", "SIGNAL0", False, writeCallback)
    
    # SIGNAL1 corresponds to OUTPUT2
    mm.writeControlDevice("SENSOR4", "SIGNAL1", False, writeCallback)
    
    # SIGNAL2 corresponds to OUTPUT3
    mm.writeControlDevice("SENSOR4", "SIGNAL2", False, writeCallback)
    
    # SIGNAL3 corresponds to OUTPUT4
    mm.writeControlDevice("SENSOR4", "SIGNAL3", False, writeCallback)
    
    time.sleep(1)
    
    # SIGNAL0 corresponds to OUTPUT1
    mm.writeControlDevice("SENSOR4", "SIGNAL0", True, writeCallback)
    
    # SIGNAL1 corresponds to OUTPUT2
    mm.writeControlDevice("SENSOR4", "SIGNAL1", True, writeCallback)
    
    # SIGNAL2 corresponds to OUTPUT3
    mm.writeControlDevice("SENSOR4", "SIGNAL2", True, writeCallback)
    
    # SIGNAL3 corresponds to OUTPUT4
    mm.writeControlDevice("SENSOR4", "SIGNAL3", True, writeCallback)

for count in range (0, 5):

    readInputs()
    
    time.sleep(2)
    
    readOutputs()
    
    time.sleep(2)
    
    writeOutputs()
    
    time.sleep(2)

# Detach (deconfigure) a control device that was previously attached to the MachineMotion controller.
mm.detachControlDevice("SENSOR4", detachCallback)

print ("Application Message: Program terminating ... \n")
time.sleep(1)
sys.exit(0)
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

#### Reference Example (Encoder)
> example--readControlDevice--writeControlDevice--encoder.py *(see example for the readControlDevice function above)*

#### Example (Digital IO Module)
> example--readControlDevice--writeControlDevice--digital_io_module.py *(see example for the readControlDevice function above)*

## Executing Python Programs

- To execute a MachineMotion Python program, the library file *_MachineMotion_1_6_8.py* must be located in the same folder as your program.   

- Open the command prompt (for Windows) or terminal (for Mac and Linux).

- Browse to the directory where you program is saved with the library file

- Execute your program.
    ```bash 
    python yourProgram.py
    ```

- The console or terminal will display various status messages while the program runs.

- To stop the execution of the program you can always press CRTL + c

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
