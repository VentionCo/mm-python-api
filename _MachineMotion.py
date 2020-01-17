# File name:            _MachineMotion.py
#                            #
# Author:               Francois Giguere                            #
# Note:                 Information about all the g-Code            #
#                       commands supported are available at         #
#                       the following location of the SDK:          #
#                       ./documentation                             #

# Import standard libraries
import json, time, threading, sys

# Import package dependent libraries
from socketIO_client import SocketIO, BaseNamespace
import paho.mqtt.client as mqtt

# Misc. Variables
motion_completed         = "false"
waiting_motion_status    = "false"
waiting_current_position = "false"

machineMotionRef = None
gCodeCallbackRef = None
lastSendTimeStamp = None

class CONTROL_DEVICE_SIGNALS:
    SIGNAL0 = "SIGNAL0"
    SIGNAL1 = "SIGNAL1"
    SIGNAL2 = "SIGNAL2"
    SIGNAL3 = "SIGNAL3"
    SIGNAL4 = "SIGNAL4"
    SIGNAL5 = "SIGNAL5"
    SIGNAL6 = "SIGNAL6"

class CONTROL_DEVICE_TYPE:
    IO_EXPANDER_GENERIC = "IO_EXPANDER_GENERIC"
    ENCODER             = "ENCODER"

class CONTROL_DEVICE_PORTS:
    SENSOR4 = "SENSOR4"
    SENSOR5 = "SENSOR5"
    SENSOR6 = "SENSOR6"

class AXIS_DIRECTION:
    positive = "positive"
    negative = "negative"
    normal = positive
    reverse = negative
    clockwise = positive
    counterclockwise = negative

class AXIS_NUMBER:
    DRIVE1 = 1
    DRIVE2 = 2
    DRIVE3 = 3

class UNITS_SPEED:
    mm_per_min = "mm per minute"
    mm_per_sec =  "mm per second"

class UNITS_ACCEL:
    mm_per_min_sqr = "mm per minute"
    mm_per_sec_sqr =  "mm per second"

class DEFAULT_IP_ADDRESS:
    usb_windows     = "192.168.7.2"
    usb_mac_linux   = "192.168.6.2"
    ethernet        = "192.168.0.2"

class NETWORK_MODE:
    static  = "static"
    dhcp    = "dhcp"

class MICRO_STEPS:
    ustep_full  = 1
    ustep_2     = 2
    ustep_4     = 4
    ustep_8     = 8
    ustep_16    = 16

class MECH_GAIN:
    timing_belt_150mm_turn          = 150
    legacy_timing_belt_200_mm_turn  = 200
    ballscrew_10mm_turn             = 10
    legacy_ballscrew_5_mm_turn      = 5
    indexer_deg_turn                = 85
    conveyor_mm_turn                = 157
    rack_pinion_mm_turn             = 157.08

class AUX_PORTS:
    aux_1 = 0
    aux_2 = 1
    aux_3 = 2

class ENCODER_TYPE:
    real_time = "realtime-position"
    stable = "stable-position"

HARDWARE_MIN_HOMING_FEEDRATE =251
HARDWARE_MAX_HOMING_FEEDRATE= 15999

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

    myMqttClient = None
    myIoExpanderAvailabilityState = [ False, False, False, False ]
    myEncoderRealtimePositions    = [ 0, 0, 0 ]
    myEncoderStablePositions    = [ 0, 0, 0 ]
    digitalInputs = {}

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

    class HomingSpeedOutOfBounds(Exception):
        pass

    # Class constructor
    def __init__(self, machineIp, gCodeCallback=None):
        global machineMotionRef
        global gCodeCallbackRef

        self.myConfiguration['machineIp'] = machineIp

        # MQTT
        self.myMqttClient = mqtt.Client()
        self.myMqttClient.on_connect = self.__onConnect
        self.myMqttClient.on_message = self.__onMessage
        self.myMqttClient.on_disconnect = self.__onDisconnect
        self.myMqttClient.connect(machineIp)
        self.myMqttClient.loop_start()

        machineMotionRef = self
        if(gCodeCallback):
            gCodeCallbackRef = gCodeCallback
        else:
            def emptyCallBack(data):
                pass
            gCodeCallbackRef = emptyCallBack

        self.__establishConnection(False)

        return

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

        return

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
        '''
        desc: Returns the current position of each axis.
        returnValue: A dictionary containing the current position of each axis.
        returnValueType: Dictionary
        note: This function returns the 'open loop' position of each axis. If your axis has an encoder, please use readEncoder.
        '''
        global waiting_current_position

        waiting_current_position = "true"
        self.myGCode.__emit__("M114")
        while self.isReady() != "true" and waiting_current_position == "true": pass

        return self.myGCode.currentPositions

    def emitStop(self):
        '''
        desc: Immediately stops all motion of all axes.
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
        desc: Initiates the homing sequence of all axes. All axes will home sequentially (Axis 1, then Axis 2, then Axis 3).
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
                desc: The axis to be homed.
                type: Number
        note: If configAxisDirection is set to "normal" on axis 1, axis 1 will home itself towards sensor 1A. If configAxisDirection is set to "reverse" on axis 1, axis 1 will home itself towards sensor 1B.
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
                desc: Units for speed. Can be switched to UNITS_SPEED.mm_per_min
                defaultValue: UNITS_SPEED.mm_per_sec
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
                desc: Units for speed. Can be switched to UNITS_ACCEL.mm_per_min_sqr
                defaultValue: UNITS_ACCEL.mm_per_sec_sqr
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
        desc: Moves multiple specified axes to their desired end locations synchronously.
        params:
            axes:
                desc: The axes which will perform the move commands. Ex - [1 ,3]
                type: List
            positions:
                desc: The desired end position of all axess movement. Ex - [50, 10]
                type: List
        exampleCodePath: emitCombinedAxesAbsoluteMove.py
        note: The current speed and acceleration settings are applied to the combined motion of the axes.
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

        # Set to relative motion mode 
        self.myGCode.__emit__("G91")
        while self.isReady() != "true": pass

        if direction == "positive":distance = "" + str(distance)
        elif direction  == "negative": distance = "-" + str(distance)

        # Transmit move command
        self.myGCode.__emit__("G0 " + self.myGCode.__getTrueAxis__(axis) + str(distance))
        while self.isReady() != "true": pass

        return


    def emitCombinedAxisRelativeMove(self, axes, directions, distances):
        '''
        desc: Moves the multiple specified axes the specified distances in the specified directions.
        params:
            axes:
                desc: The axes to move. Ex-[1,3]
                type: List of Integers
            directions:
                desc: The direction of travel of each specified axis. Ex - ["positive", "negative"]
                type: List of Strings
            distances:
                desc: The travel distances in mm. Ex - [10, 40]
                type: List of Numbers
        exampleCodePath: emitCombinedAxesRelativeMove.py
        note: The current speed and acceleration settings are applied to the combined motion of the axes.
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

        # Set to relative motion mode
        self.myGCode.__emit__("G91")
        while self.isReady() != "true": pass

        # Transmit move command
        command = "G0 "
        for axis, direction, distance in zip(axes, directions, distances):
            if direction == AXIS_DIRECTION.positive: distance = "" + str(distance)
            elif direction  == AXIS_DIRECTION.negative: distance = "-" + str(distance)
            command += self.myGCode.__getTrueAxis__(axis) + str(distance) + " "
        self.myGCode.__emit__(command)
        while self.isReady() != "true": pass

        return


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

    def configAxisDirection(self, axis, direction):
        '''
        desc: Configures a single axis to operate in either clockwise (normal) or counterclockwise (reverse) mode. Refer to the Automation System Diagram for the correct axis setting.
        params:
            axis:
                desc: The specified axis.
                type: Number
            direction:
                desc: A string of value either either 'Normal' or 'Reverse'. 'Normal' direction means the axis will home towards end stop sensor A and reverse will make the axis home towards end stop B.
                type: String
        note: For more details on how to properly set the axis direction, please see <a href="https://vention-demo.herokuapp.com/technical-documents/machine-motion-user-manual-123#actuator-hardware-configuration"> here </a>
        exampleCodePath: configAxisDirection.py

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
        desc: Pauses python program execution until machine has finished its current movement.
        exampleCodePath: waitForMotionCompletion.py

        '''
        global waiting_motion_status

        waiting_motion_status = "true"
        self.emitgCode("V0")
        while  self.isMotionCompleted() != "true": pass

    def configMachineMotionIp(self, mode, machineIp="", machineNetmask="", machineGateway=""):
        '''
        desc: Set up the required network information for the Machine Motion controller. The router can be configured in either DHCP mode or static mode.
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

    def configHomingSpeed(self, axes, speeds, units = UNITS_SPEED.mm_per_sec):
        '''
        desc: Sets homing speed for all 3 axes.
        params:
            axes:
                desc: A list of the axes to configure. ex - [1,2,3]
                type: List
            speeds:
                desc: A list of homing speeds to set for each axis. ex - [50, 50, 100]
                type: List
            units:
                desc: Units for speed. Can be switched to UNITS_SPEED.mm_per_min
                defaultValue: UNITS_SPEED.mm_per_sec
                type: String
        exampleCodePath: configHomingSpeed.py
        note: Once set, the homing speed will apply to all programs, including MachineLogic applications.
        '''
        try:
            axes = list(axes)
            speeds = list(speeds)
        except TypeError:
            axes = [axes]
            speeds = [speeds]

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



            if speed_mm_per_min < HARDWARE_MIN_HOMING_FEEDRATE:
                raise self.HomingSpeedOutOfBounds("Your desired homing speed of " + str(speed_mm_per_min) + "mm/min can not be less than " + str(HARDWARE_MIN_HOMING_FEEDRATE) + "mm/min (" + str(HARDWARE_MIN_HOMING_FEEDRATE/60) + "mm/sec).")
            if speed_mm_per_min > HARDWARE_MAX_HOMING_FEEDRATE:
                raise self.HomingSpeedOutOfBounds("Your desired homing speed of " + str(speed_mm_per_min) + "mm/min can not be greater than " + str(HARDWARE_MAX_HOMING_FEEDRATE) + "mm/min (" + str(HARDWARE_MAX_HOMING_FEEDRATE/60) + "mm/sec)")

            gCodeCommand = gCodeCommand + self.myGCode.__getTrueAxis__(axis) + str(speed_mm_per_min) + " "

        while self.isReady() == False: pass
        gCodeCommand = gCodeCommand.strip()
        self.emitgCode(gCodeCommand)

    def configMinMaxHomingSpeed(self, axes, minspeeds, maxspeeds, units = UNITS_SPEED.mm_per_sec):
        '''
        desc: Sets the minimum and maximum homing speeds for each axis.
        params:
            axes:
                desc: a list of the axes that require minimum and maximum homing speeds.
                type: List
            minspeeds:
                desc: the minimum speeds for each axis.
                type: List
            maxspeeds:
                desc: the maximum speeds for each axis, in the same order as the axes parameter
                type: List
        exampleCodePath: configHomingSpeed.py
        note: This function can be used to set safe limits on homing speed. Because homing speed is configured only through software aPI, this safeguards against developers accidently modifying homing speed to unsafe levels.
        '''
        gCodeCommand = "V1 "
        for idx, axis in enumerate(axes):

            if units == UNITS_SPEED.mm_per_sec:
                min_speed_mm_per_min = minspeeds[idx] * 60
                max_speed_mm_per_min = maxspeeds[idx] * 60
            elif units == UNITS_SPEED.mm_per_min:
                min_speed_mm_per_min = minspeeds[idx]
                max_speed_mm_per_min = maxspeeds[idx]

            if min_speed_mm_per_min < HARDWARE_MIN_HOMING_FEEDRATE:
                raise self.HomingSpeedOutOfBounds("Your desired homing speed of " + str(min_speed_mm_per_min) + "mm/min can not be less than " + str(HARDWARE_MIN_HOMING_FEEDRATE) + "mm/min (" + str(HARDWARE_MIN_HOMING_FEEDRATE/60) + "mm/sec).")
            if max_speed_mm_per_min > HARDWARE_MAX_HOMING_FEEDRATE:
                raise self.HomingSpeedOutOfBounds("Your desired homing speed of " + str(max_speed_mm_per_min) + "mm/min can not be greater than " + str(HARDWARE_MAX_HOMING_FEEDRATE) + "mm/min (" + str(HARDWARE_MAX_HOMING_FEEDRATE/60) + "mm/sec)")

            gCodeCommand = gCodeCommand + self.myGCode.__getTrueAxis__(axis) + str(min_speed_mm_per_min) + ":" + str(max_speed_mm_per_min) + " "

        while self.isReady() == False: pass
        gCodeCommand = gCodeCommand.strip()
        self.emitgCode(gCodeCommand)


    def configAxis(self, axis, uStep, mechGain):
        '''
        desc: Configures motion parameters for a single axis.
        params:
            axis:
                desc: The axis to configure.
                type: Number
            uStep:
                desc: The microstep setting of the axis.
                type: Number
            mechGain:
                desc: The distance moved by the actuator for every full rotation of the stepper motor, in mm/revolution.
                type: Number
        note: The uStep setting is hardcoded into the machinemotion controller through a DIP switch and is by default set to 8. The value here must match the value on the DIP Switch.
        exampleCodePath: configAxis.py

        '''
        self._restrictInputValue("axis", axis,  AXIS_NUMBER)
        self._restrictInputValue("uStep", uStep, MICRO_STEPS)

        uStep    = float(uStep)
        mechGain = float(mechGain)

        if(axis == 1):
            self.myAxis1_steps_mm = 200 * uStep / mechGain
            self.myGCode.__emit__("M92 " + self.myGCode.__getTrueAxis__(axis) + str(self.myAxis1_steps_mm))
        elif(axis == 2):
            self.myAxis2_steps_mm = 200 * uStep / mechGain
            self.myGCode.__emit__("M92 " + self.myGCode.__getTrueAxis__(axis) + str(self.myAxis2_steps_mm))
        elif(axis == 3):
            self.myAxis3_steps_mm = 200 * uStep / mechGain
            self.myGCode.__emit__("M92 " + self.myGCode.__getTrueAxis__(axis) + str(self.myAxis3_steps_mm))


    def saveData(self, key, data):
        '''
        desc: Saves/persists data within the MachineMotion Controller in key - data pairs.
        params:
            key:
                desc: A string that uniquely identifies the data to save for future retreival.
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
                desc: A Unique identifier representing the data to be retreived
                type: String
        exampleCodePath: getData_saveData.py
        returnValue: A dictionary containing the saved data.
        returnValueType: Dictionary
        '''

        getDataAvailable = threading.Event()
        dataTimedOut = threading.Event()

        def asyncGetData(key, callback):
            #Send the request to MachineMotion
            self.mySocket.emit('getData', key)
            # On reception of the data invoke the callback function.
            self.mySocket.on('getDataResponse', callback)

        def asyncCallback(data):
            self.asyncResult = data
            getDataAvailable.set()

        def threadTimeout():
           time.sleep(3)
           dataTimedOut.set()

        #timer here to force call asyncCallback on timeout #kill timer#
        # If this fails, return a key value pair - key is 'error' value is description why error failed
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
        note: For more information, please see the digital IO datasheet <a href="https://www.vention.io/technical-documents/digital-io-module-datasheet-70">here</a>
        returnValue: Dictionary with keys of format "Digital IO Network Id [id]" and values [id] where [id] is the network IDs of all connected digital IO modules.
        returnValueType: Dictionary
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


    def digitalRead(self, deviceNetworkId, pin):
        '''
        desc: Reads the state of a digital IO modules input pins.
        params:
            deviceNetworkId:
                desc: The IO Modules device network ID. It can be found printed on the product sticker on the back of the digital IO module.
                type: Integer
            pin:
                desc: The index of the input pin.
                type: Integer
        returnValue: Returns 1 if the input pin is 24V and returns 0 if the input pin is 0V.
        returnValueType: Integer
        exampleCodePath: digitalRead.py

        note: The pin labels on the digital IO module (pin 1, pin 2, pin 3, pin 4) correspond in software to (0, 1, 2, 3). Therefore, digitalRead(deviceNetworkId, 2)  will read the value on input pin 3.
        '''

        if ( not self.isIoExpanderInputIdValid( deviceNetworkId, pin ) ):
            logging.warning("DEBUG: unexpected digital-output parameters: device= " + str(device) + " pin= " + str(pin))
            return
        if (not hasattr(self, 'digitalInputs')):
            self.digitalInputs = {}
        if (not deviceNetworkId in self.digitalInputs):
            self.digitalInputs[deviceNetworkId] = {}
        if (not pin in self.digitalInputs[deviceNetworkId]):
            self.digitalInputs[deviceNetworkId][pin] = 0
        return self.digitalInputs[deviceNetworkId][pin]

    def digitalWrite(self, deviceNetworkId, pin, value):
        '''
        desc: Sets voltage on specified pin of digital IO output pin to either 24V or 0V.
        params:
            deviceNetworkId:
                desc: The IO Modules device network ID. It can be found printed on the product sticker on the back of the digital IO module.
                type: Integer
            pin:
                desc: The output pin number to write to.
                type: Integer
            value:
                desc: Writing 1 will set digial output to 24V, writing 0 will set digital output to 0V.
                type: Integer
        exampleCodePath: digitalWrite.py

        note: Output pins maximum sourcing current is 75 mA and the maximum sinking current is 100 mA. The pin labels on the digital IO module (pin 1, pin 2, pin 3, pin 4) correspond in software to (0, 1, 2, 3). Therefore, digitalWrite(deviceNetworkId, 2, 1)  will set output pin 3 to 24V.

        '''
        if (self.isIoExpanderOutputIdValid( deviceNetworkId, pin ) == False):
            print ( "DEBUG: unexpected digitalOutput parameters: device= " + str(deviceNetworkId) + " pin= " + str(pin) )
            return
        self.myMqttClient.publish('devices/io-expander/' + str(deviceNetworkId) + '/digital-output/' +  str(pin), '1' if value else '0')

    def emitDwell(self, milliseconds):
        '''
        desc: Pauses motion for a specified time. This function is non-blocking; your program may accomplish other tasks while the machine is dwelling.
        params:
            miliseconds:
                desc: The duration to wait in milliseconds.
                type: Integer
        note: The timer starts after all previous MachineMotion movement commands have finished execution.
        exampleCodePath: emitDwell.py
        '''
        self.myGCode.__emit__("G4 P"+str(milliseconds))
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
        returnValue: The current position of the encoder, in counts. The encoder has 3600 counts per revolution.
        returnValueType: Integer
        exampleCodePath: readEncoder.py
        note: The encoder position returned by this function may be delayed by up to 250 ms due to internal propogation delays.
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

        return


    #This function is left in for legacy, however it is not documented because it is the same functionality as readEncoder
    def readEncoderRealtimePosition(self, encoder):
        if (self.isEncoderIdValid( encoder ) == False):
            print ( "DEBUG: unexpected encoder identifier: encoderId= " + str(encoder) )
            return
        return self.myEncoderRealtimePositions[encoder]

    # ------------------------------------------------------------------------
    # Register to the MQTT broker on each connection.
    #
    # @param client   - The MQTT client identifier (us)
    # @param userData - The user data we have supply on registration (none)
    # @param flags    - Connection flags
    # @param rc       - The connection return code
    def __onConnect(self, client, userData, flags, rc):
        if rc == 0:
            self.myMqttClient.subscribe('devices/io-expander/+/available')
            self.myMqttClient.subscribe('devices/io-expander/+/digital-input/#')
            self.myMqttClient.subscribe('devices/encoder/+/realtime-position')

    # ------------------------------------------------------------------------
    # Update our internal state from the messages received from the MQTT broker
    #
    # @param client   - The MQTT client identifier (us)
    # @param userData - The user data we have supply on registration (none)
    # @param msg      - The MQTT message recieved
    def __onMessage(self, client, userData, msg):
        topicParts = msg.topic.split('/')
        deviceType = topicParts[1]
        device = int( topicParts[2] )
        if (deviceType == 'io-expander'):
            if (topicParts[3] == 'available'):
                availability = json.loads(msg.payload)
                if ( availability == True ):
                    self.myIoExpanderAvailabilityState[device-1] = True
                    return
                else:
                    self.myIoExpanderAvailabilityState[device-1] = False
                    return
            pin = int( topicParts[4] )
            if (self.isIoExpanderInputIdValid(device, pin) == False):
                return
            value  = int( msg.payload )
            if (not hasattr(self, 'digitalInputs')):
                self.digitalInputs = {}
            if (not device in self.digitalInputs):
                self.digitalInputs[device] = {}
            self.digitalInputs[device][pin]= value
            return
        if (deviceType == 'encoder'):
            position = float( msg.payload )
            self.myEncoderRealtimePositions[device] = position

    def __onDisconnect(self, client, userData, rc):
       print( "Disconnected with rtn code [%d]"% (rc) )

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

        return

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
