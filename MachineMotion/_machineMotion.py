#!/usr/bin/env python
# File name:            _MachineMotion.py                           #
# Author:               Francois Giguere                            #
# Note:                 Information about all the g-Code            #
#                       commands supported are available at         #
#                       the following location of the SDK:          #
#                       ./documentation                             #

# from __future__ import absolute_import, division, print_function, unicode_literals
# from builtins import *

# Import standard libraries
import json, time, threading, sys
from ._constants import *

# Import package dependent libraries
from pathlib import Path
from socketIO_client import SocketIO, BaseNamespace
import paho.mqtt.client as mqtt

# Misc. Variables
motion_completed         = "false"
waiting_motion_status    = "false"
waiting_current_position = "false"

machineMotionRef = None
gCodeCallbackRef = None
lastSendTimeStamp = None



def fastMotionStatusCallback(data, mm):
    global motion_completed
    global waiting_motion_status

    # Was a motion status request received
    if data.find("Motion Status") != -1:
        # print "A motion status was requested"
        if data.find("Motion Status = COMPLETED") != -1 and waiting_motion_status == "true":
            # print "Move was completed"
            motion_completed = "true"
            waiting_motion_status = "false"
        else:
            # print "move is in progress"
            motion_completed = "false"
            waiting_motion_status = "true"
            mm.__emit__("V0")

#
# Class that handles all gCode related communications
# @status
#
class GCode:
    mySocket = "unassigned"
    ackReceived = "false"
    waiting_motion_status = "false"
    motion_completed = "false"
    lineNumber = 1
    lastPacket = {"data": "null", "lineNumber": "null"}
    gCodeErrors = {"checksum": "Error:checksum mismatch, Last Line: ", "lineNumber": "Error:Line Number is not Last Line Number+1, Last Line: "}
    userCallback = None
    currentPositions = {
        1 : None,
        2 : None,
        3 : None
    }

    #
    # Class constructor
    # PRIVATE
    # @param socket --- Description: The GCode class requires a socket object to communicate with the controller. The socket object is passed at construction time.
    # @status
    #
    def __init__(self, socket):
        # Passing in the socket instance at construction
        self.mySocket = socket

    #
    # Function that indicates if the GCode communication port is ready to send another command.
    # @status
    #
    def __isReady__(self):
        return self.ackReceived

    #
    # Function that indicates if the the last move has completed
    # @status
    #
    def __isMotionCompleted__(self):
        global motion_completed
        return motion_completed

    #
    # Function to add the transport layer over a raw gCode packet.
    # PRIVATE
    # @param string --- Description: The GCode command to send.
    # @status
    #
    def __addTransLayer__(self, string):
        # Save the last packet sent
        self.lastPacket = {"data": string, "lineNumber": self.lineNumber}

        # Add the line number to the packet
        string = "N" + str(self.lineNumber) + " " + string

        # Increment the line number
        self.lineNumber = self.lineNumber + 1

        cs = 0

        # Calculate the checksum
        for i in range (0, len(string)):
            cs = cs ^ ord(string[i])

        # Returns the completed packet with checksum and line number
        return string + "*" + str(cs);

    #
    # Upon reception of an error message, this function extract the line number in the communication at which the error occured.
    # PRIVATE
    # @param string --- Description: The error message from the controller.
    # @status
    #
    def __extractLineNumberInError__(self, message):
        if message.find(self.gCodeErrors['checksum']) != -1:
            lineNumberBaseIndex = len(self.gCodeErrors['checksum']) - 1
            return int(message[lineNumberBaseIndex:])
        elif message.find(self.gCodeErrors['lineNumber']) != -1:
            lineNumberBaseIndex = len(self.gCodeErrors['lineNumber']) - 1
            return int(message[lineNumberBaseIndex:])

    #
    # Upon reception of a resend message, this function extract the line number in the message.
    # PRIVATE
    # @param string --- Description: The error message from the controller.
    # @status
    #
    def __extractLineNumberInResend__(self, message):
        lineNumberBaseIndex = len('Resend: ') - 1
        return int(message[lineNumberBaseIndex:])

    #
    # Function to reset the current line number in the communication.
    # PRIVATE
    # @param line --- Description: The new line number.
    # @status
    #
    def __setLineNumber__(self, line):
        self.lineNumber = line
        self.__emit__("M110 N" + str(line))

    #
    # Function to map API axis labels to motion controller axis labels
    # PRIVATE
    # @param axis --- Description: The API axis label.
    # @status
    #
    def __getTrueAxis__(self, axis):
        if axis == 1: return "X"
        elif axis == 2: return "Y"
        elif axis == 3: return "Z"
        else: return "Axis Error"

    #
    # Function that packages the data in a JSON object and sends to the MachineMotion server over a socket connection.
    # PRIVATE
    # @param axis --- Description: The API axis label.
    # @status
    #
    def __send__(self, cmd, data):
        global lastSendTimeStamp

        # Add the transport layer data
        data['value'] = self.__addTransLayer__(data['value'])

        # Serialize the dictionary in json format
        packet = json.dumps(data)

        # Reset the GCode status
        self.ackReceived = "false"

        lastSendTimeStamp = time.time()

        # Sending
        self.mySocket.emit(cmd, packet)

    #
    # Function to send a raw G-Code ASCII command
    # @param gCode --- Description: gCode is string representing the G-Code command to send to the controller. Type: string.
    # @status
    #
    def __emit__(self, gCode):

        # # When a G-Code command is sent, it is assumed that it is a motion command and the move_completed attriute is set to "false". The user has to used
        # # the isMotionCompleted() function to verify if the motion is completed.
        # if(gCode != "V0"):
            # self.motion_completed = "false"

        # Object to transmit data
        gCodeCmd = {"command": "gCode", "value": gCode}

        self.__send__('gCodeCmd', gCodeCmd)

        time.sleep(0.05)

    @staticmethod
    def __userCallback__(data): return

    #
    # Function that executes upon reception of messages from the motion controller. The user configured callback in ran after this function.
    # PUBLIC
    # @param data --- Description: The data sent by the motion controller. Type: string.
    # @status
    #
    def __rxCallback__(self, data):

        global waiting_motion_status
        global waiting_current_position
        global lastSendTimeStamp

        # print "DEBUG---Last command sent: " + str(self.lastPacket)
        # print "DEBUG---Last received data: " + data

        # Look if the echo of the last command was found in the incoming data
        if (data.find(self.lastPacket['data'])) != -1:
            # The last command was acknowledged
            self.ackReceived =  "true"
            # print "DEBUG---Received ack for packet " + str(self.lastPacket['data']) + ", line = " + str(self.lastPacket['lineNumber']) + "\n"
            #self.lastPacket = {"data": "null", "lineNumber": "null"}
        # Special ack for homing
        elif data.find('X:0.00') != -1 and self.lastPacket['data'].find('G28') != -1:
            # The last command was acknowledged
            self.ackReceived =  "true"
            # print "DEBUG---Received ack for homing"
            #self.lastPacket = {"data": "null", "lineNumber": "null"}
        # Special ack for homing
        elif data.find('DEBUG') != -1 and self.lastPacket['data'].find('M111') != -1:
            # The last command was acknowledged
            self.ackReceived =  "true"
            # print "DEBUG---Received ack for debug setup" + "\n"
            #self.lastPacket = {"data": "null", "lineNumber": "null"}
        # Look if errors were received
        elif (data.find('Error:') != -1):
            # print "DEBUG--Error received from controller. Last line correct line was " + str(self.__extractLineNumberInError__(data))
            # print "DEBUG--Error received from controller. Last line number sent " + str(self.lastPacket['lineNumber'])

            if (self.__extractLineNumberInError__(data) == (int(self.lastPacket['lineNumber']) - 1)):
                # print "DEBUG--Error received on line " + str(self.__extractLineNumberInError__(data))
                self.lastPacket = {"data": self.lastPacket['data'], "lineNumber": int(self.__extractLineNumberInError__(data))+1}
                self.ackReceived = "false"
                self.__emit__(self.lastPacket['data'])
        elif (data.find('Resend:') != -1):
            self.lineNumber = self.__extractLineNumberInResend__(data)

        if data.find('Count X:') != -1:
            # print 'Current position : ' + data

            self.currentPositions[1] = float(data[data.find('X')+2:(data.find('Y')-1)])
            self.currentPositions[2] = float(data[data.find('Y')+2:(data.find('Z')-1)])
            self.currentPositions[3] = float(data[data.find('Z')+2:(data.find('E')-1)])

            waiting_current_position = "false"

        fastMotionStatusCallback(data, self)

        self.__userCallback__(data)



    # Private function
    class ListenToSocket(threading.Thread):
        def __init__(self, gCode):
            self.gcode = gCode
            threading.Thread.__init__(self)
        def run(self):
            global lastSendTimeStamp

            self.gcode.mySocket.on('machineMotionAck', self.gcode.__rxCallback__)
            while True:
                if (self.gcode.mySocket.connected and self.gcode.ackReceived == 'false' and (lastSendTimeStamp is not None) and (time.time() - lastSendTimeStamp > 5)):
                    # Trigger a reconnection
                    self.gcode.mySocket.disconnect()
                    self.gcode.mySocket.connect('', True)
                self.gcode.mySocket.wait(1)

    def __keepSocketAlive__(self):
        thread = GCode.ListenToSocket(self)
        thread.daemon = True # Stops this thread if main one exits
        thread.start()

    # Private function
    def __setUserCallback__(self, userCallback):

        # Save the user function to call on incoming messages locally
        self.__userCallback__ = userCallback

        # Start the periodic process that fetches the sockets that were received by the OS
        self.__keepSocketAlive__()

#
# Class that encapsulates code that waits for a certain socket topic to be received
# @status
#
class WaitForSocketTopic:

    response_received = False
    mySocket = None
    myTopic = None

    # Function redefined by the user
    @staticmethod
    def _user_callback_(data): return

    # Wrapper to invoke the user defined function and manage the completion flag
    def _callback_(self, data):
        self.response_received = True
        self._user_callback_(data)

    def set_user_callback(self, callback):
        self._user_callback_ = callback

    def wait_for_response(self, socket, topic, callback):
        self.response_received = False

        self.mySocket = socket
        self.myTopic = topic
        self._user_callback_ = callback

        while self.response_received == False:
            self.mySocket.on(self.myTopic, self._callback_)
            self.mySocket.wait(seconds = 0.1)

#
# Class used to encapsulate the MachineMotion controller
# @status
#
class MachineMotion:
    # Class variables
    mySocket = None
    myConfiguration = {"machineIp": None, "machineGateway": None, "machineNetmask": None}
    myGCode = None

    mqttEncoderClient = None
    mqttIOClient = None

    digitalInputs = [[0 for numModules in range(6)] for pins in range(4)] 
    myIoExpanderAvailabilityState = [ False, False, False, False ]
    myEncoderRealtimePositions    = [ 0, 0, 0 ]
    myEncoderStablePositions    = [ 0, 0, 0 ]

    myAxis1_steps_mm = None
    myAxis2_steps_mm = None
    myAxis3_steps_mm = None

    myAxis1_direction = None
    myAxis2_direction = None
    myAxis3_direction = None

    validPorts   = ["AUX1", "AUX2", "AUX3"]
    valid_u_step = [1, 2, 4, 8, 16]

    asyncResult = None

    #Boolean Flags
    enableDebugMessages = False

    #Takes tuples of parameter variables and the class they belong to.
    #If the parameter does not belong to the class, it raises a descriptive error. 
    def _restrictInputValue(self, argName, argValue, argClass):
      
        validParams = [i for i in argClass.__dict__.keys() if i[:1] != '_']
        validValues = [argClass.__dict__[i] for i in validParams]

        if argValue in validValues:
            pass
        else:
            class InvalidInput(Exception):
                pass
            errorMessage = "An invalid selection was made. Given parameter '" + str(argName) + "' must be one of the following values:"
            for param in validParams:
                errorMessage = errorMessage + "\n" + argClass.__name__ + "." + param + " (" + str(argClass.__dict__[param]) +")"
            raise InvalidInput(errorMessage)

    def _restrictInputToSubset(self, argName, argValue, argClass):
      
        validParams = [i for i in argClass.__dict__.keys() if i[:1] != '_']
        validValues = [argClass.__dict__[i] for i in validParams]

        if set(argValue).issubset(set(validValues)):
            pass
        else:
            class InvalidInput(Exception):
                pass
            errorMessage = "An invalid selection was made. Given parameter '" + str(argName) + "' must be one of the following values:"
            for param in validParams:
                errorMessage = errorMessage + "\n" + argClass.__name__ + "." + param + " (" + str(argClass.__dict__[param]) +")"
            raise InvalidInput(errorMessage)



    def isIoExpanderIdValid(self, id):
        if (id < 1 or id > 3):
            return False
        return True
        
    def isIoExpanderInputIdValid(self, deviceId, pinId):
                
        if (self.isIoExpanderIdValid( deviceId ) == False):
            return False
        if (pinId < 0 or pinId > 3):
            return False
        return True
        
    def isIoExpanderOutputIdValid(self, deviceId, pinId):
        if (self.isIoExpanderIdValid( deviceId ) == False):
            return False
        if (pinId < 0 or pinId > 3):
            return False
        return True
        

    def isEncoderIdValid(self, id):
        if id >= 0 and id <= 3:
            return True
        return False


    def getCurrentPositions(self):
        global waiting_current_position

        waiting_current_position = "true"
        self.myGCode.__emit__("M114")
        while self.isReady() != "true" and waiting_current_position == "true": pass

        return self.myGCode.currentPositions

    def emitStop(self):
        '''
        desc: Immediately stops all motion of all axes
        note: This function is a hard stop. It is not a controlled stop and consequently does not decelerate smoothly to a stop. Additionally, this function is not intended to serve as an emergency stop since this stop mechanism does not have safety ratings.
        exampleCodePath: emitStop.py
        '''
        global motion_completed

        motion_completed = "false"

        self.myGCode.__emit__("M410")

        # Wait and send a dummy packet to insure that other commands after the emit stop are not flushed.
        time.sleep(0.500)
        self.myGCode.__emit__("G91")
        while self.isReady() != "true": pass
        self.myGCode.__emit__("G0 X0")
        while self.isReady() != "true": pass

    def emitHomeAll(self):
        '''
        desc: Initiates the homing sequence of all axes. All axes will home sequentially (Axis 1, 2 then 3).
        exampleCodePath: emitHomeAll.py
        '''

        global motion_completed

        motion_completed = "false"

        self.myGCode.__emit__("G28")

    def emitHome(self, axis):
        '''
        desc: Initiates the homing sequence for the specified axis.
        params: 
            axis:
                desc: The number of the axis that you would like to home.
                type: Number
        note: If setAxisDirection is set to "normal" on axis 1, axis 1 will home itself towards sensor 1A. If setAxisDirection is set to "reverse" on axis 1, axis 1 will home itself towards sensor 1B.
        exampleCodePath: emitHome.py
        '''
        self._restrictInputValue("axis", axis, AXIS_NUMBER)

        global motion_completed

        motion_completed = "false"

        self.myGCode.__emit__("G28 " + self.myGCode.__getTrueAxis__(axis))

    def emitSpeed(self, speed, units = UNITS_SPEED.mm_per_sec):
        '''
        desc: Sets the global speed for all movement commands on all axes.
        params:
            speed:
                desc: The global max speed in mm/min.
                type: Number
            units:
                desc: Either `UNITS_SPEED.mm_per_min` or `UNITS_SPEED.mm_per_sec`.
                type: String
        exampleCodePath: emitSpeed.py
        '''

        self._restrictInputValue("units", units, UNITS_SPEED)

        if units == UNITS_SPEED.mm_per_min:
            speed_mm_per_min = speed
        elif units == UNITS_SPEED.mm_per_sec: 
            speed_mm_per_min = 60*speed
        
           
        self.myGCode.__emit__("G0 F" + str(speed_mm_per_min))
        while self.isReady() != "true": pass

    def emitAcceleration(self, acceleration, units=UNITS_ACCEL.mm_per_sec_sqr):
        '''
        desc: Sets the global acceleration for all movement commands on all axes.
        params:
            mm_per_sec_sqr:
                desc: The global acceleration in mm/s^2.
                type: Number
            units:
                desc: Either `UNITS.mm_per_min_sqr` or `UNITS_ACCEL.mm_per_sec_sqr`
                type: String
        exampleCodePath:  emitAcceleration.py
        '''

        self._restrictInputValue("units", units, UNITS_ACCEL)

        if units == UNITS_ACCEL.mm_per_sec_sqr:
            accel_mm_per_sec_sqr = acceleration
        elif units == UNITS_ACCEL.mm_per_min_sqr: 
            accel_mm_per_sec_sqr = acceleration/3600

        self.myGCode.__emit__("M204 T" + str(accel_mm_per_sec_sqr))
        while self.isReady() != "true": pass

    def emitAbsoluteMove(self, axis, position):
        '''
        desc: Moves the specified axis to a desired end location.
        params: 
            axis: 
                desc: The axis which will perform the absolute move command.
                type: Number
            position:
                desc: The desired end position of the axis movement.
                type: Number
        exampleCodePath: emitAbsoluteMove.py
        '''
        self._restrictInputValue("axis", axis, AXIS_NUMBER)
        global motion_completed

        motion_completed = "false"

        # Set to absolute motion mode
        self.myGCode.__emit__("G90")
        while self.isReady() != "true": pass

        # Transmit move command
        self.myGCode.__emit__("G0 " + self.myGCode.__getTrueAxis__(axis) + str(position))
        while self.isReady() != "true": pass

    def emitCombinedAxesAbsoluteMove(self, axes, positions):
        '''
        desc: Moves multiple specified axes to their desired end locations.
        params:
            axes:
                desc: The axes which will perform the move commands. Ex - [1 ,3]
                type: List
            positions:
                desc: The desired end position of all axess movement. Ex - [50, 10]
                type: List
        exampleCodePath: emitCombinedAxesAbsoluteMove.py
        '''

        try: 
            axes = list(axes)
            positions = list(positions)
        except TypeError:
            raise TypeError("Axes and Postions must be either lists or convertible to lists")

        for axis in axes:
            self._restrictInputValue("axis", axis, AXIS_NUMBER)

        global motion_completed

        motion_completed = "false"

        # Set to absolute motion mode
        self.myGCode.__emit__("G90")
        while self.isReady() != "true": pass

        # Transmit move command
        command = "G0 "
        for axis, position in zip(axes, positions):
            command += self.myGCode.__getTrueAxis__(axis) + str(position) + " "
        self.myGCode.__emit__(command)
        while self.isReady() != "true": pass

    def emitRelativeMove(self, axis, direction, distance):
        '''
        desc: Moves the specified axis the specified distance in the specified direction.
        params:
            axis:
                desc: The axis to move.
                type: Integer
            direction:
                desc: The direction of travel. Ex - "positive" or "negative" 
                type: String
            distance:
                desc: The travel distance in mm.
                type: Number
        exampleCodePath: emitRelativeMove.py
        '''

        self._restrictInputValue("axis",axis, AXIS_NUMBER)
        self._restrictInputValue("direction", direction, AXIS_DIRECTION)

        global motion_completed

        motion_completed = "false"

        # Set to relative motion mode temporarily
        try:
            self.myGCode.__emit__("G91")
            while self.isReady() != "true": pass

            if direction == "positive":distance = "" + str(distance)
            elif direction  == "negative": distance = "-" + str(distance)

            # Transmit move command
            self.myGCode.__emit__("G0 " + self.myGCode.__getTrueAxis__(axis) + str(distance))
            while self.isReady() != "true": pass
        finally:
            self.myGCode.__emit__("G90")
            while self.isReady() != "true": pass

    def emitCombinedAxisRelativeMove(self, axes, directions, distances):
        '''
        desc: Moves the multiple specified axes the specified distances in the specified directions.
        params:
            axes:
                desc: The axes to move. Ex-[1,3]
                type: List
            direction:
                desc: The direction of travel of each specified axis. Ex - ["positive", "negative"] 
                type: String
            distance:
                desc: The travel distances in mm. Ex - [10, 40]
                type: List
        exampleCodePath: emitCombinedAxesRelativeMove.py
        '''

        try: 
            axes = list(axes)
            directions = list(directions)
            distances = list(distances)
        except TypeError:
            raise TypeError("Axes, positions and distances must be either lists or convertible to lists")

        for axis in axes:
            self._restrictInputValue("axis", axis, AXIS_NUMBER)
        for direction in directions:
            self._restrictInputValue("direction", direction, AXIS_DIRECTION)
        
        global motion_completed

        motion_completed = "false"

        # Temporarily set to relative motion mode
        self.myGCode.__emit__("G91")
        while self.isReady() != "true": pass

        try:

            # Transmit move command
            command = "G0 "
            for axis, direction, distance in zip(axes, directions, distances):
                if direction == AXIS_DIRECTION.positive: distance = "" + str(distance)
                elif direction  == AXIS_DIRECTION.negative: distance = "-" + str(distance)
                command += self.myGCode.__getTrueAxis__(axis) + str(distance) + " "
            self.myGCode.__emit__(command)
            while self.isReady() != "true": pass
        
        finally:
            self.myGCode.__emit__("G91")
            while self.isReady() != "true": pass
        
    def setPosition(self, axis, position):
        '''
        desc: Override the current position of the specified axis to a new value.
        params:
            axis:
                desc: Overrides the position on this axis.
                type: Number
            position:
                desc: The new position value in mm.
                type: Number
        exampleCodePath: setPosition.py
        '''
        self._restrictInputValue("axis", axis, AXIS_NUMBER)

        # Transmit move command
        self.myGCode.__emit__("G92 " + self.myGCode.__getTrueAxis__(axis) + str(position))
        while self.isReady() != "true": pass

    def emitgCode(self, gCode):
        '''
        desc: Executes raw gCode on the controller.
        params:
            gCode:
                desc: The g-code that will be passed directly to the controller.
                type: string
        note: All movement commands sent to the controller are by default in mm. 
        exampleCodePath: emitgCode.py
        '''
        global motion_completed

        motion_completed = "false"

        self.myGCode.__emit__(gCode)

    def emitSetAxisDirection(self, axis, direction):
        '''
        desc: Reversing the axis direction reverses the location of the home sensor and reverses the positive motion direction. In Normal direction, the Home sensor is xA, in Reverse the Home sensor is xB.
        params:
            axis:
                desc: The specified axis.
                type: Number
            direction:
                desc: A string of value either either 'Normal' or 'Reverse'. 'Normal' direction means the axis will home towards end stop sensor A and reverse will make the axis home towards end stop B. Ex - "Reverse"
                type: String
        note: For more details on how to properly set the axis direction, please see <a href="https://vention-demo.herokuapp.com/technical-documents/machine-motion-user-manual-123#actuator-hardware-configuration"> here </a>
        exampleCodePath: emitSetAxisDirection.py
        '''
    
        self._restrictInputValue("axis", axis, AXIS_NUMBER)
        self._restrictInputValue("direction", direction, AXIS_DIRECTION)
            
        if(axis == 1):
            self.myAxis1_direction = direction
            if(direction == AXIS_DIRECTION.normal):
                self.myGCode.__emit__("M92 " + self.myGCode.__getTrueAxis__(axis) + str(self.myAxis1_steps_mm))
            elif (direction == AXIS_DIRECTION.reverse):
                self.myGCode.__emit__("M92 " + self.myGCode.__getTrueAxis__(axis) + "-" + str(self.myAxis1_steps_mm))
        elif(axis == 2):
            if(direction == AXIS_DIRECTION.normal):
                self.myGCode.__emit__("M92 " + self.myGCode.__getTrueAxis__(axis) + str(self.myAxis2_steps_mm))
            elif (direction == AXIS_DIRECTION.reverse):
                self.myGCode.__emit__("M92 " + self.myGCode.__getTrueAxis__(axis) + "-" + str(self.myAxis2_steps_mm))
        elif(axis == 3):
            if(direction == AXIS_DIRECTION.normal):
                self.myGCode.__emit__("M92 " + self.myGCode.__getTrueAxis__(axis) + str(self.myAxis3_steps_mm))
            elif (direction == AXIS_DIRECTION.reverse):
                self.myGCode.__emit__("M92 " + self.myGCode.__getTrueAxis__(axis) + "-" + str(self.myAxis3_steps_mm))

    #This function should be private in future releases.
    def isReady(self):
        return self.myGCode.__isReady__()

    def isMotionCompleted(self):
        global motion_completed
        return motion_completed

    def waitForMotionCompletion(self):
        '''
        desc: Pauses Execution until machine has finished its current movement.
        exampleCodePath: waitForMotionCompletion.py
        '''
        global waiting_motion_status

        waiting_motion_status = "true"
        self.emitgCode("V0")
        while  self.isMotionCompleted() != "true": pass

    def configMachineMotionIp(self, mode, machineIp="", machineNetmask="", machineGateway=""):
        '''
        desc: Set up the required network information for the Machine Motion controller. The router can be configured in either DHCP mode or 
        params:
            mode:
                desc: Sets Network Mode to either DHCP or static addressing. Either <code>NETWORK_MODE.static</code> or <code>NETWORK_MODE.dhcp</code>
                type: Constant
            machineIp: 
                desc: The static IP Address given to the controller. (Required if mode = <code>NETWORK_MODE.static</code>)
                type: String
            machineNetmask:
                desc: The netmask IP Address given to the controller. (Required if mode = <code>NETWORK_MODE.static</code>)
                type: String
            machineGateway:
                desc: The gateway IP Address given to the controller. (Required if mode = <code>NETWORK_MODE.static</code>)
                type: String
        Note: All strings expect the format "XXX.XXX.XXX.XXX". To connect the controller to the internet, the gateway IP should be the same IP as your LAN router.
        exampleCodePath: configMachineMotionIp.py
        '''

        if(mode == NETWORK_MODE.static):
            if '' in [machineIp, machineNetmask, machineGateway]:
               print("NETWORK ERROR: machineIp, machineNetmask and machineGateway cannot be left blank in static mode")
               quit()

        # Create a new object and augment it with the key value.    
        self.myConfiguration["mode"] = mode
        self.myConfiguration["machineIp"] = machineIp
        self.myConfiguration["machineNetmask"] = machineNetmask
        self.myConfiguration["machineGateway"] = machineGateway

        self.mySocket.emit('configIp', json.dumps(self.myConfiguration))
        time.sleep(1)

    def setHomingSpeed(self, axes, speeds, units = UNITS_SPEED.mm_per_sec):
        '''
        desc: Sets homing speed for all 3 axes
        params: 
            axes:
                desc: The axes to configure
                type: List
            speeds:
                desc: The speeds for each axes
                type: List
        note: Once set, the homing speed will apply to all programs, including MachineLogic
        '''
        try:
            axes = list(axes)
            speeds = list(speeds)
        except TypeError:
            axes = [axes]
            speeds = [speeds]

        self._restrictInputToSubset("axes",axes,AXIS_NUMBER)
        if len(axes) != len(speeds):
            class InputsError(Exception):
                pass
            raise InputsError("axes and speeds must be of same length")

        gCodeCommand = "V2 "
        for idx, axis in enumerate(axes):

            if units == UNITS_SPEED.mm_per_sec:
                speed_mm_per_min = speeds[idx] * 60
            elif units == UNITS_SPEED.mm_per_min:
                speed_mm_per_min = speeds[idx]

            gCodeCommand = gCodeCommand + self.myGCode.__getTrueAxis__(axis) + str(speed_mm_per_min) + " "
        
        while self.isReady() == False: pass
        gCodeCommand = gCodeCommand.strip()
        self.emitgCode(gCodeCommand)

    def setMinMaxHomingSpeed(self, axes, minspeeds, maxspeeds, units = UNITS_SPEED.mm_per_sec):
        '''
        desc: Sets the minimum and maximum homing speeds for each axis
        params:
            axes: 
                desc: a list of the axis that require minimum and maximum homing speeds
                type: List
            minspeeds:
                desc: the minimum speeds for each axis, in the same order as the axes parameter
                type: List
            maxspeeds:
                desc: the maximum speeds for each axis, in the same order as the axes parameter
                type: List
        note: Once set, the homing speed minimum and maximum values will apply to all programs, including MachineLogic
        '''
        gCodeCommand = "V1 "
        for idx, axis in enumerate(axes):

            if units == UNITS_SPEED.mm_per_sec:
                min_speed_mm_per_min = minspeeds[idx] * 60
                max_speed_mm_per_min = maxspeeds[idx] * 60
            elif units == UNITS_SPEED.mm_per_min:
                min_speed_mm_per_min = minspeeds[idx]
                max_speed_mm_per_min = maxspeeds[idx]

            gCodeCommand = gCodeCommand + self.myGCode.__getTrueAxis__(axis) + str(min_speed_mm_per_min) + ":" + str(max_speed_mm_per_min) + " "
        
        while self.isReady() == False: pass
        gCodeCommand = gCodeCommand.strip()
        self.emitgCode(gCodeCommand)


    def configAxis(self, axis, _u_step, _mech_gain):
        '''
        desc: Initializes parameters for proper axis control.
        params:
            axis:
                desc: The axis to configure.
                type: Number
            _u_step:
                desc: The number of microsteps taken by the stepper motor. Must be either 1, 2, 5, 8 or 16.
                type: Number
            _mech_gain: 
                desc: The distance moved by the actuator for every full rotation of the stepper motor, in mm/revolution.
                type: Number
        note: The uStep setting is hardcoded into the machinemotion controller through a DIP switch and is by default set to 8. The value here must match the value on the DIP Switch. 
        exampleCodePath: configAxis.py
        '''
        self._restrictInputValue("axis", axis,  AXIS_NUMBER)
        self._restrictInputValue("_u_step", _u_step, MICRO_STEPS)

        u_step    = float(_u_step)
        mech_gain = float(_mech_gain)

        # validate that the uStep setting is valid
        if (self.valid_u_step.index(u_step) != -1):
            if(axis == 1):
                self.myAxis1_steps_mm = 200 * u_step / mech_gain
                self.myGCode.__emit__("M92 " + self.myGCode.__getTrueAxis__(axis) + str(self.myAxis1_steps_mm))
            elif(axis == 2):
                self.myAxis2_steps_mm = 200 * u_step / mech_gain
                self.myGCode.__emit__("M92 " + self.myGCode.__getTrueAxis__(axis) + str(self.myAxis2_steps_mm))
            elif(axis == 3):
                self.myAxis3_steps_mm = 200 * u_step / mech_gain
                self.myGCode.__emit__("M92 " + self.myGCode.__getTrueAxis__(axis) + str(self.myAxis3_steps_mm))
            else:
                pass
                # print "Argument error, {configAxis(self, axis, u_step, mech_gain)}, {axis} argument is invalid"

        else:
            pass
            # print "Argument error, {configAxis(self, axis, u_step, mech_gain)}, {u_step} argument is invalid"

    def saveData(self, key, data):
        '''
        desc: Saves/persists data within the MachineMotion Controller in key - data pairs.
        params:
            key:
                desc: A string the uniquely identifies the data to save for future retreival
                type: String
            data:
                desc: The data to save to the machine. The data must be convertible to JSON format.
                type: String
        note: The Data continues to exist even when the controller is shut off. However, writing to a previously used key will override the previous value.
        exampleCodePath: getData_saveData.py
        '''

        # Create a new object and augment it with the key value.
        dataPack = {}
        dataPack["fileName"] = key
        dataPack["data"] = data

        # Send the request to MachineMotion
        self.mySocket.emit('saveData', json.dumps(dataPack))
        time.sleep(0.05)

    def getData(self, key):
        '''
        desc: Retreives saved/persisted data from the MachineMotion controller (in key-data pairs). If the controller takes more than 3 seconds to return data, the function will return with a value of "Error - getData took too long" under the given key.
        params:
            key:
                desc: Uniquely identifies the data to be retreived
                type: String
        exampleCodePath: getData_saveData.py
        '''

        getDataAvailable = threading.Event()
        dataTimedOut = threading.Event()

        def asyncGetData(key, callback):
            #Send the request to MachineMotion
            self.mySocket.emit('getData', key)
            # On reception of the data invoke the callback function.
            self.mySocket.on('getDataResponse', callback)

            #timer here to force call asyncCallback on timeout #kill timer# 
            # If this fails, return a key value pair - key is 'error' value is description why error failed
            

        def asyncCallback(data):
            self.asyncResult = data
            getDataAvailable.set()

        def threadTimeout():
           time.sleep(3)
           dataTimedOut.set()


        getDataThread = threading.Thread(target = asyncGetData, args=(key, asyncCallback,))
        timeoutThread = threading.Thread(target = threadTimeout)
        
        getDataThread.start()
        timeoutThread.start()
        while True:
            if getDataAvailable.isSet():
                getDataResult = json.loads("".join(self.asyncResult))
                return getDataResult
            elif dataTimedOut.isSet():
                getDataResult = json.loads('{"data":"Error - getData took too long"}')
                return getDataResult

    def isIoExpanderAvailable(self, device):
        return self.myIoExpanderAvailabilityState[ device-1 ]

    def detectIOModules(self):
        '''
        desc: Returns a dictionary containing all detected IO Modules.
        note: For more information, please see the digital IO datasheet <a href="#" style="color:red">here</a>
        exampleCodePath: digitalRead.py
        '''
        class NoIOModulesFound(Exception):
            pass

        foundIOModules = {}
        numIOModules = 0

        for ioDeviceID in range(0,3):
            if self.isIoExpanderAvailable(ioDeviceID):
                foundIOModules["Digital IO Network Id " + str(ioDeviceID)] = ioDeviceID
                numIOModules = numIOModules + 1

        if numIOModules == 0:
            raise NoIOModulesFound("Application Error: No IO Modules found. Please verify the connection between Digital IO and MachineMotion.")
        else:
            return foundIOModules
    
       
    def digitalRead(self, device, pin):
        '''
        desc: Returns the value (<span style="color:red"> HIGH/LOW? </span>) of the given device and pin.
        params:
            device:
                desc: The device identifier to read from (1, 2, 3) <span style="color:red">Is this AUX1, AUX2, AUX3?</span>
                type: Integer
            pin:
                desc: The pin index to read from [0,1,2,3]
                type: Integer
        exampleCodePath: digitalRead.py
        '''

        return self.digitalInputs[device][pin]
        
    def digitalWrite(self, device, pin, value):
        '''
        desc: Sets voltage on specified pin of digital IO output pin to either High (24V) or Low (0V).
        params:
            device:
                desc: The device identifier to write to.
                type: Integer
            pin:
                desc: The pin number of the output device to write to.
                type: Integer
            value:
                desc: Writing '1' or HIGH will set digial output to 24V, writing 0 will set digital output to 0V.
                type: Integer
        exampleCodePath: digitalWrite.py
        Note: The max current that can be drawn from the output pins is <span style="color:red">x mA</span>
        '''
        if (self.isIoExpanderOutputIdValid( device, pin ) == False):
            print ( "DEBUG: unexpected digitalOutput parameters: device= " + str(device) + " pin= " + str(pin) )
            return
        self.mqttIOClient.publish('devices/io-expander/' + str(device) + '/digital-output/' +  str(pin), '1' if value else '0')
    
    def emitDwell(self, milli):
        '''
        desc: Pauses motion for a specified time. This function is non-blocking; your program may accomplish other tasks while the machine is dwelling.
        params:
            milli:
                desc: The amount of time to pause MachineMotion movement.
                type: Integer
        note: The timer starts after all previous MachineMotion movement commands have finished execution.
        exampleCodePath: emitDwell.py
        '''
        self.myGCode.__emit__("G4 P"+str(milli))
        while self.isReady() != "true": pass

    def readEncoder(self, encoder, readingType="realTime"):
        '''
        desc: Returns the last received encoder position in counts.
        params:
            encoder:
                desc: The identifier of the encoder to read
                type: Integer
            readingType:
                desc: Either 'real time' or 'stable'. In 'real time' mode, readEncoder will return the most recently received encoder information. In 'stable' mode, readEncoder will update its return value only after the encoder output has stabilized around a specific value, such as when the axis has stopped motion.
                type: String 
        exampleCodePath: readEncoder.py
        note: The encoder position returned by this function may be delayed by up to 250 ms due to internal propogation delays
        '''
        self._restrictInputValue("readingType", readingType, ENCODER_TYPE)

        if (self.isEncoderIdValid( encoder ) == False):
            print ( "DEBUG: unexpected encoder identifier: encoderId= " + str(encoder) )
            return

        if readingType == ENCODER_TYPE.real_time:
            self.myEncoderStablePositions
            return self.myEncoderRealtimePositions[encoder]
        elif readingType == ENCODER_TYPE.stable:
            return self.myEncoderStablePositions[encoder]

    def readEncoderDistance(self, encoder, readingType="realTime", axis = None):
        '''
        desc: Returns the last received encoder position in mm.
        params:
            encoder:
                desc: The identifier of the encoder to read
                type: Integer
            readingType:
                desc: Either 'real time' or 'stable'. In 'real time' mode, readEncoder will return the most recently received encoder information. In 'stable' mode, readEncoder will update its return value only after the encoder output has stabilized around a specific value, such as when the axis has stopped motion.
                type: String 
        exampleCodePath: readEncoder.py
        note: The encoder position returned by this function may be delayed by up to 250 ms due to internal propogation delays
        '''
        
        self._restrictInputValue("axis", axis, AXIS_NUMBER)
        self._restrictInputValue("readingType", readingType, ENCODER_TYPE)
        try:
            if(readingType == ENCODER_TYPE.real_time):
                if axis == AXIS_NUMBER.DRIVE1 :
                    return self.myEncoderRealtimePositions[encoder]/self.myAxis1_steps_mm
                elif axis == AXIS_NUMBER.DRIVE2:
                    return self.myEncoderRealtimePositions[encoder]/self.myAxis2_steps_mm
                elif axis == AXIS_NUMBER.DRIVE3:
                    return self.myEncoderRealtimePositions[encoder]/self.myAxis3_steps_mm
            elif (readingType == ENCODER_TYPE.stable):
                if axis == AXIS_NUMBER.DRIVE1 :
                    return self.myEncoderStablePositions[encoder]/self.myAxis1_steps_mm
                elif axis == AXIS_NUMBER.DRIVE2:
                    return self.myEncoderStablePositions[encoder]/self.myAxis2_steps_mm
                elif axis == AXIS_NUMBER.DRIVE3:
                    return self.myEncoderStablePositions[encoder]/self.myAxis3_steps_mm
        except TypeError:
            raise TypeError("ConfigAxis must be called prior to readEncoderDistance")
    


    #This function is left in for legacy, however it is not documented because it is the same functionality as readEncoder
    def readEncoderRealtimePosition(self, encoder):
        if (self.isEncoderIdValid( encoder ) == False):
            print ( "DEBUG: unexpected encoder identifier: encoderId= " + str(encoder) )
            return
        return self.myEncoderRealtimePositions[encoder]
        



    def __establishConnection(self, isReconnection):
        global gCodeCallbackRef

        # Create the web socket
        self.mySocket = SocketIO(self.myConfiguration['machineIp'], 8888, MySocketCallbacks)
        self.myGCode = GCode(self.mySocket)

        # Send a command to initialize the MachineMotion system
        configCmd = {"parameter": "init", "value": "sysInit"}
        packet = json.dumps(configCmd)
        self.mySocket.emit('sysInit', packet)

        # Give 5 seconds to the MachineMotion system to initialize the hardware
        time.sleep(5)

        # Set the callback to the user specified function. This callback is used to process incoming messages from the machineMotion controller
        self.myGCode.__setUserCallback__(gCodeCallbackRef)

        # Set the line number to initialize the communication
        self.myGCode.__setLineNumber__(0)
        while self.isReady() != "true": pass

        #Set the debug level of the motionController to "247" to enable echo on all commands. Refer to http://marlinfw.org/docs/gcode/M111.html for more details.
        self.emitgCode("M111 S247")
        while self.isReady() != "true": pass

   
    
    #------- Encoder client ------
    def mqttEncoderConnect(self, client, userData, flags, rc):
        if rc == 0:
            self.mqttEncoderClient.subscribe('devices/encoder/+/realtime-position')
            self.mqttEncoderClient.subscribe('devices/encoder/+/stable-position')
    
    def mqttEncoderMessage(self, client, userData, msg):
        
        position = float(msg.payload.decode('utf-8'))
        device = int(msg.topic.split("/")[2])
        if "realtime-position" in str(msg.topic):
            self.myEncoderRealtimePositions[device] = position
            return
        elif "stable-position" in str(msg.topic):
            self.myEncoderStablePositions[device] = position
            return

    def mqttEncoderDisconnect(self, client, userData, msg):
        self.mqttEncoderClient.unsubscribe('devices/encoder/+/realtime-position')
        self.mqttEncoderClient.unsubscribe('devices/encoder/+/stable-position')
        print( "Encoder disconnected with rtn code [%d]"% (rc) )

    #-----DIGITAL IO CLIENT------
        # ------------------------------------------------------------------------
    # Register to the MQTT broker on each connection.
    #
    # @param client   - The MQTT client identifier (us)
    # @param userData - The user data we have supply on registration (none)
    # @param flags    - Connection flags
    # @param rc       - The connection return code
    def mqttIOConnect(self, client, userData, flags, rc):
        if rc == 0:
            self.mqttIOClient.subscribe('devices/io-expander/+/available')
            self.mqttIOClient.subscribe('devices/io-expander/+/digital-input/#')


    # ------------------------------------------------------------------------
    # Update our internal state from the messages received from the MQTT broker
    #
    # @param client   - The MQTT client identifier (us)
    # @param userData - The user data we have supply on registration (none)
    # @param msg      - The MQTT message recieved
    def mqttIOMessage(self, client, userData, msg):
        device = int(msg.topic.split("/")[2])
        if "available" in str(msg.topic):
            # availability = str( msg.payload ).lower()
            availability = msg.payload.decode('utf-8')
            if availability == 'true':
                self.myIoExpanderAvailabilityState[device-1] = True
                return
            else:
                self.myIoExpanderAvailabilityState[device-1] = False
                return
        elif "digital-input" in str(msg.topic):
            pin = int(msg.topic.split("/")[4])
            value = int(msg.payload)
            self.digitalInputs[device][pin]= value
            return
       


    def mqttIODisconnect(self, client, userData, rc):
       print( "IO Disconnected with rtn code [%d]"% (rc) )

    # Class constructor
    def __init__(self, machineIp, gCodeCallback=None):
        global machineMotionRef
        global gCodeCallbackRef

        self.myConfiguration['machineIp'] = machineIp

        #MQTT for Digital IO
        self.mqttIOClient = mqtt.Client()
        self.mqttIOClient.on_connect = self.mqttIOConnect
        self.mqttIOClient.on_message = self.mqttIOMessage
        self.mqttIOClient.on_disconnect = self.mqttIODisconnect
        self.mqttIOClient.connect_async(machineIp)
        self.mqttIOClient.loop_start()
        
        #MQTT for Encoder
        self.mqttEncoderClient = mqtt.Client()
        self.mqttEncoderClient.on_connect = self.mqttEncoderConnect
        self.mqttEncoderClient.on_message = self.mqttEncoderMessage
        self.mqttEncoderClient.on_disconnect = self.mqttEncoderDisconnect
        self.mqttEncoderClient.connect_async(machineIp)
        self.mqttEncoderClient.loop_start()



        machineMotionRef = self
        if(gCodeCallback):
            gCodeCallbackRef = gCodeCallback
        else:
            def emptyCallBack(data):
                pass
            gCodeCallbackRef = emptyCallBack

        self.__establishConnection(False)

class MySocketCallbacks(BaseNamespace):

    def on_connect(self):
        print('[SocketIO Connected]')

    def on_reconnect(self):
        print('[SocketIO Reconnected]')
        global lastSendTimeStamp
        global machineMotionRef

        lastSendTimeStamp = time.time()
        machineMotionRef.myGCode.__setLineNumber__(1)

    def on_disconnect(self):
        print('[SocketIO Disconnected]')
