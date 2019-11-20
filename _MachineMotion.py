# File name:            _MachineMotion.py                           #
# Author:               Francois Giguere                            #
# Note:                 Information about all the g-Code            #
#                       commands supported are available at         #
#                       the following location of the SDK:          #
#                       ./documentation                             #

# Import standard libraries
import json, time, threading, sys

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

class DIRECTION:
    positive = "positive"
    negative = "negative"

class AXIS_NUMBER:
    DRIVE1 = 1
    DRIVE2 = 2
    DRIVE3 = 3

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
    mySocket = "notInitialized"
    myConfiguration = {"machineIp": "notInitialized", "machineGateway": "notInitialized", "machineNetmask": "notInitialized"}
    myGCode = "notInitialized"
    myGCode = "notInitialized"

    myMqttClient = None
    myIoExpanderAvailabilityState = [ False, False, False, False ]
    myEncoderRealtimePositions    = [ 0, 0, 0 ]

    myAxis1_steps_mm = "notInitialized"
    myAxis2_steps_mm = "notInitialized"
    myAxis3_steps_mm = "notInitialized"

    validPorts   = ["AUX1", "AUX2", "AUX3"]
    valid_u_step = [1, 2, 4, 8, 16]


    def isIoExpanderIdValid(self, id):
        '''
        desc: Returns true if the given id is valid for an IO Expander
        params:
            id: 
                desc: Device identifier <span style="color:red">revise</span>
                type: Integer
        '''
        if (id < 1 or id > 3):
            return False
        return True
        
    def isIoExpanderInputIdValid(self, deviceId, pinId):
        '''
        desc: Returns true if the given input pin identifier is valid for an IO Expander
        params:
            deviceId:
                desc: Device identifier
                type: Integer
            pinId:
                desc: Pin identifier
                type: Integer
        '''
                
        if (self.isIoExpanderIdValid( deviceId ) == False):
            return False
        if (pinId < 0 or pinId > 3):
            return False
        return True
        
    def isIoExpanderOutputIdValid(self, deviceId, pinId):
        '''
        desc: Returns True if the given output pin identifier is valid for an IO Expander.
        params:
            deviceId:
                desc: Device Identifier
                type: Integer
            pinId:
                desc: Pin Identifier
                type: Integer
        '''
        if (self.isIoExpanderIdValid( deviceId ) == False):
            return False
        if (pinId < 0 or pinId > 3):
            return False
        return True
        

    def isEncoderIdValid(self, id):
        '''
        desc: Returns True if the given id is valid for an encoder.
        params:
            id:
                desc: <span style="color:red"> What Id is this?</span> 
        '''
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
        global motion_completed

        motion_completed = "false"

        self.myGCode.__emit__("G28 " + self.myGCode.__getTrueAxis__(axis))

    def emitSpeed(self, mm_per_min):
        '''
        desc: Sets the global speed for all movement commands on all axes.
        params:
            mm_per_min:
                desc: The global max speed in mm/min.
                type: Number
        exampleCodePath: emitSpeed.py
        '''

        self.myGCode.__emit__("G0 F" +str(mm_per_min))
        while self.isReady() != "true": pass

    def emitAcceleration(self, mm_per_sec_sqr):
        '''
        desc: Sets the global acceleration for all movement commands on all axes.
        params:
            mm_per_sec_sqr:
                desc: The global acceleration in mm/s^2.
                type: Number
        exampleCodePath:  emitAcceleration.py
        '''

        self.myGCode.__emit__("M204 T" + str(mm_per_sec_sqr))
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
        if (not isinstance(axes, list) or not isinstance(positions, list)):
            raise TypeError("Axes and Postions must be lists")

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

        if (not isinstance(axes, list) or not isinstance(directions, list) or not isinstance(distances, list)):
            raise TypeError("All parameters must be lists")
        
        global motion_completed

        motion_completed = "false"

        # Temporarily set to relative motion mode
        self.myGCode.__emit__("G91")
        while self.isReady() != "true": pass

        try:

            # Transmit move command
            command = "G0 "
            for axis, direction, distance in zip(axes, directions, distances):
                if direction == "positive": distance = "" + str(distance)
                elif direction  == "negative": distance = "-" + str(distance)
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

    def isReady(self):
        '''
        desc: Returns true if the motion controller is ready to receive another command.
        '''
        return self.myGCode.__isReady__()

    def isMotionCompleted(self):
        '''
        desc: Returns true if all axes have completed their movement.
        '''
        global motion_completed
        return motion_completed

    def waitForMotionCompletion(self):
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

        u_step    = float(_u_step)
        mech_gain = float(_mech_gain)

        # validate that the uStep setting is valid
        if (self.valid_u_step.index(u_step) != -1):
            if(axis == 1):
                self.myAxis1_steps_mm = 200 * u_step / mech_gain
                self.myGCode.__emit__("M92 " + self.myGCode.__getTrueAxis__(axis) + str(self.myAxis1_steps_mm))
            elif(axis == 2):
                self.myAxis1_steps_mm = 200 * u_step / mech_gain
                self.myGCode.__emit__("M92 " + self.myGCode.__getTrueAxis__(axis) + str(self.myAxis1_steps_mm))
            elif(axis == 3):
                self.myAxis1_steps_mm = 200 * u_step / mech_gain
                self.myGCode.__emit__("M92 " + self.myGCode.__getTrueAxis__(axis) + str(self.myAxis1_steps_mm))
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
        exampleCodePath: saveData_getData.py
        '''

        # Create a new object and augment it with the key value.
        dataPack = {}
        dataPack["fileName"] = key;
        dataPack["data"] = data;

        # Send the request to MachineMotion
        self.mySocket.emit('saveData', json.dumps(dataPack))
        time.sleep(0.05)

    def getData(self, key, callback):
        '''
        desc: retreives saved/persisted data from the MachineMotion controller (in key-data pairs)
        params:
            key:
                desc: Uniquely identifies the data to be retreived
                type: String
            callback:
                desc: A function that is invoked when the asynchronous data is received. The function must take a single input parameter.
                type: Function
        exampleCodePath: saveData_getData.py
        '''

        #Send the request to MachineMotion

        self.mySocket.emit('getData', key)

        # On reception of the data invoke the callback function.
        self.mySocket.on('getDataResponse', callback)


    def isIoExpanderAvailable(self, device):
        '''
        desc: Returns True if the io-expander with the given id is available
        params:
            device:
                desc: The io-expander device identifier <span style="color:red">What is an example?</span>
                type: Integer
        '''
        return self.myIoExpanderAvailabilityState[ device-1 ]

    
    
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
        '''
        if (self.isIoExpanderInputIdValid( device, pin ) == False):
            print ( "DEBUG: unexpected digital-output parameters: device= " + str(device) + " pin= " + str(pin) )
            return
        if (not hasattr(self, 'digitalInputs')):
            self.digitalInputs = {}
        if (not device in self.digitalInputs):
            self.digitalInputs[device] = {}
        if (not pin in self.digitalInputs[device]):
            self.digitalInputs[device][pin] = 0
        return self.digitalInputs[device][pin]
        
    def digitalWrite(self, device, pin, value):
        '''
        desc: Sets voltage on specified pin of digital IO output pin to either High (5V) or Low (0V).
        params:
            device:
                desc: The device identifier to write to.
                type: Integer
            pin:
                desc: The pin number of the output device to write to.
                type: Integer
            value:
                desc: Writing '1' or HIGH will set digial output to 5V, writing 0 will set digital output to 0V.
                type: Integer
        Note: The max current that can be drawn from the output pins is <span style="color:red">x mA</span>
        '''
        if (self.isIoExpanderOutputIdValid( device, pin ) == False):
            print ( "DEBUG: unexpected digitalOutput parameters: device= " + str(device) + " pin= " + str(pin) )
            return
        self.myMqttClient.publish('devices/io-expander/' + str(device) + '/digital-output/' +  str(pin), '1' if value else '0')
            

    def readEncoder(self, encoder):
        '''
        desc: Returns the last received encoder position.
        params:
            encoder:
                desc: The identifier of the encoder to read
                type: Integer
        note: The encoder position returned by this function may be delayed by up to 250 ms due to internal propogation delays
        '''
        return self.readEncoderRealtimePosition( encoder )


    def readEncoderRealtimePosition(self, encoder):
        '''
        desc: Returns the last received encoder position.
        params:
            encoder:
                desc: The identifier of the encoder to read
                type: Integer
        note: The encoder position returned by this function may be delayed by up to 250 ms due to internal propogation delays
        '''
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
                availability = str( msg.payload ).lower()
                if ( availability == 'true' ):
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

    # Class constructor
    def __init__(self, gCodeCallback, machineIp):
        global machineMotionRef
        global gCodeCallbackRef

        self.myConfiguration['machineIp'] = machineIp

        # MQTT
        self.myMqttClient = mqtt.Client()
        self.myMqttClient.on_connect = self.__onConnect
        self.myMqttClient.on_message = self.__onMessage
        self.myMqttClient.on_disconnect = self.__onDisconnect
        self.myMqttClient.connect_async(machineIp)
        self.myMqttClient.loop_start()

        machineMotionRef = self
        gCodeCallbackRef = gCodeCallback

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
