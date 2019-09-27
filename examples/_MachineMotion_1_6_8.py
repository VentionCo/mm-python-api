# File name:            _MachineMotion_1_6_5.py                     #
# Version:              1.6.5                                       #
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
motion_completed = "false"
waiting_motion_status = "false"

display_connection_debug_messages = False
display_motion_controller_raw_messages = False

machineMotionRef = None
gCodeCallbackRef = None
lastSendTimeStamp = None

# Control device signal names on controllers that have hardware version of v1B0 or more recent
class CONTROL_DEVICE_SIGNALS_V1B0_plus:
    OUTPUT1 = "SIGNAL0"
    OUTPUT2 = "SIGNAL1"
    OUTPUT3 = "SIGNAL2"
    OUTPUT4 = "SIGNAL3"
    INPUT1 = "SIGNAL4"
    INPUT2 = "SIGNAL5"
    INPUT3 = "SIGNAL6"
    INPUT4 = "SIGNAL7"
# Control device signal names on controllers that have hardware version older than v1B0
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
    ENCODER           = "ENCODER"

# Port names on controllers that have hardware version of v1B0 or more recent
class CONTROL_DEVICE_PORTS_V1B0_plus:
    AUX1 = "SENSOR4"
    AUX2 = "SENSOR5"
    AUX3 = "SENSOR6"
    
# Port names on controllers that have hardware version older than v1B0-    
class CONTROL_DEVICE_PORTS:
    SENSOR4 = "SENSOR4"
    SENSOR5 = "SENSOR5"
    SENSOR6 = "SENSOR6"
    
class DIGITAL_IO_MODULE_ADDRESS:
    ADDRESS1 = "SENSOR4"
    ADDRESS2 = "SENSOR5"
    ADDRESS3 = "SENSOR6"

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
    rack_pinion_mm_turn             = 157.08

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

    #
    # Class constructor
    # PRIVATE
    # @param socket --- Description: The GCode class requires a socket object to communicate with the controller. The socket object is passed at contruction time.
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
        global lastSendTimeStamp
        
        if(display_motion_controller_raw_messages) : print ("Motion Controller Message: " + data + " \n")

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

    myAxis1_steps_mm = "notInitialized"
    myAxis2_steps_mm = "notInitialized"
    myAxis3_steps_mm = "notInitialized"

    validPorts   = ["SENSOR4", "SENSOR5", "SENSOR6"]
    validDevices = ["IO_EXPANDER_GENERIC", "ENCODER"]
    validSignals = ["SIGNAL4", "SIGNAL5", "SIGNAL6", "SIGNAL7", "SIGNAL0", "SIGNAL1", "SIGNAL2", "SIGNAL3"]

    portInputs = dict.fromkeys(validPorts, 0)
    signalMasks = dict.fromkeys(validSignals, 0)
    for i, v in enumerate(validSignals) :
        signalMasks[v] = 1 << i

    valid_u_step = [1, 2, 4, 8, 16]

    attach_control_device_socket_response   = WaitForSocketTopic()
    read_control_device_socket_response     = WaitForSocketTopic()
    write_control_device_socket_response    = WaitForSocketTopic()
    detach_control_device_socket_response   = WaitForSocketTopic()
    attachedDevices = {}

    def __isPortValid(self, portName):
        if portName in self.validPorts:
            return True

        print ( "ERROR: Port name " + portName + " is invalid. Try 'SENSOR4', 'SENSOR5' or 'SENSOR6'." )

        sys.exit()

    def __isDeviceValid(self, deviceName):
        if deviceName in self.validDevices:
            return True

        print ( "ERROR: Device name " + deviceName + " is invalid. Try 'ENCODER' or 'IO_EXPANDER_GENERIC'." )

        sys.exit()

    def __isSignalValid(self, signalName):
        if signalName in self.validSignals:
            return True

        print ( "ERROR: Signal name " + signalName + " is invalid. Try 'SIGNAL0', 'SIGNAL1', 'SIGNAL2', 'SIGNAL3', 'SIGNAL4', 'SIGNAL5' or 'SIGNAL6'." )

        sys.exit()

    #
    # Function that will immediately stop all motion of all the axes
    # @status
    #
    def emitStop(self):
        global motion_completed

        motion_completed = "false"

        self.myGCode.__emit__("M410")

        # Wait and send a dummy packet to insure that other commands after the emit stop are not flushed.
        time.sleep(0.500)
        self.myGCode.__emit__("G0 X0")
        while self.isReady() != "true": pass

    #
    # Function that will initiate the homing sequence of all axes. The sequence will home all axes using the endstop signals
    # @status
    #
    def emitHomeAll(self):
        global motion_completed

        motion_completed = "false"

        self.myGCode.__emit__("G28")
        while self.isReady() != "true": pass

    #
    # Function that will initiate the homing sequence for the axis specified. The sequence will home the axis using the endstops signals.
    # @param axis --- Description: "axis" is the axis number that will be set to home location.  --- Type: number.
    # @status
    #
    def emitHome(self, axis):
        global motion_completed

        motion_completed = "false"

        self.myGCode.__emit__("G28 " + self.myGCode.__getTrueAxis__(axis))
        while self.isReady() != "true": pass

    #
    # Function to send a displacement speed configuration command
    # @param mm_per_min --- Description: mm_per_mim is the displacement speed in mm/min --- Type: number.
    # @status
    #
    def emitSpeed(self, mm_per_min):
        self.myGCode.__emit__("G0 F" +str(mm_per_min))
        while self.isReady() != "true": pass

    #
    # Function to send a displacement acceleration configuration command
    # @param mm_per_sec_sqr --- Description: mm_per_sec_sqr is the displacement acceleration in mm/sec^2 --- Type: number.
    # @status
    #
    def emitAcceleration(self, mm_per_sec_sqr):
        self.myGCode.__emit__("M204 T" + str(mm_per_sec_sqr))
        while self.isReady() != "true": pass

    #
    # Function to send an absolute move command to the MachineMotion controller
    # @param axis --- Description: axis is the axis on which the command will be applied. --- Type: string or number.
    # @param position --- Description: position is the position from its home location where the axis will go. --- Type: string or number.
    # @status
    #
    def emitAbsoluteMove(self, axis, position):
        global motion_completed

        motion_completed = "false"

        # Set to absolute motion mode
        self.myGCode.__emit__("G90")
        while self.isReady() != "true": pass

        # Transmit move command
        self.myGCode.__emit__("G0 " + self.myGCode.__getTrueAxis__(axis) + str(position))
        while self.isReady() != "true": pass
        
            #
    # Function to send an absolute move command to the MachineMotion controller. This command can move more than one axis simultaneously
    # @param axes --- Description: axes are the axes on which the command will be applied. Example : [1, 2, 3] --- Type: list of strings or numbers.
    # @param positions --- Description: positions are the positions from their home location where the axes will go. --- Type: list of strings or numbers.
    # @status
    #
    def emitCombinedAxesAbsoluteMove(self, axes, positions):
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

    #
    # Function to send a relative move command to the MachineMotion controller
    # @param axis --- Description: axis is the axis on which the command will be applied. --- Type: int or string.
    # @param direction --- Description: direction is the direction in which the relative move will be conducted. --- Type: string of value equal to "positive" or "negative"
    # @param distance is the distance of the relative move.
    # @status
    #
    def emitRelativeMove(self, axis, direction, distance):
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
        
    #
    # Function to send a relative move command to the MachineMotion controller
    # @param axes --- Description: axes are the axes on which the command will be applied. Example : [1, 2, 3] --- Type: list of strings or numbers.
    # @param directions --- Description: direction are the directions in which the relative moves will be conducted. --- Type: list of strings of value equal to "positive" or "negative"
    # @param distances are the distances of the relative moves --- Type: list of strings or numbers.
    # @status
    #
    def emitCombinedAxisRelativeMove(self, axes, directions, distances):
        if (not isinstance(axes, list) or not isinstance(directions, list) or isinstance(distances, list)):
            raise TypeError("Axes and Postions must be lists")
        
        global motion_completed

        motion_completed = "false"

        # Set to relative motion mode
        self.myGCode.__emit__("G91")
        while self.isReady() != "true": pass

        # Transmit move command
        command = "G0 "
        for axis, direction, distance in zip(axes, directions, distances):
            if direction == "positive": distance = "" + str(distance)
            elif direction  == "negative": distance = "-" + str(distance)
            command += self.myGCode.__getTrueAxis__(axis) + str(distance) + " "
        self.myGCode.__emit__(command)
        while self.isReady() != "true": pass
        
    #
    # Function to force set the position of the motion controller for one specific axis.
    # @param axis --- Description: axis is the axis on which the command will be applied. --- Type: string or number.
    # @param position --- Description: position is the position to set the axis to --- Type: string or number.
    # @status
    #
    def setPosition(self, axis, position):
        # Transmit move command
        self.myGCode.__emit__("G92 " + self.myGCode.__getTrueAxis__(axis) + str(position))
        while self.isReady() != "true": pass

    #
    # Function to send a raw G-Code ASCII command
    # @param gCode --- Description: gCode is string representing the G-Code command to send to the controller. Type: string.
    # @status
    #
    def emitgCode(self, gCode):
        global motion_completed

        motion_completed = "false"

        self.myGCode.__emit__(gCode)

    #
    # Function that indicates if the GCode communication port is ready to send another command.
    # @status
    #
    def isReady(self):
        return self.myGCode.__isReady__()

    #
    # Function that indicates if the the last move has completed
    # @status
    #
    def isMotionCompleted(self):
        global motion_completed
        return motion_completed

    def waitForMotionCompletion(self):
        self.emitgCode("V0")
        while  self.isMotionCompleted() != "true": pass

    #
    # Function to setup the static IP and the router gateway of the MachineMotion controller
    # @param machineIp --- Description: desired static ip address to assign to the MachineMotion controller. --- Type: string (xxx.xxx.xxx.xxxx) where x are numbers.
    # @param gatewayIP --- Description: ip address of the LAN router. Setting a proper gateway ip addreess enables MachineMotion to access the internet for downloads --- Type: string (xxx.xxx.xxx.xxxx) where x are numbers.
    # @note:           --- For the MachineMotion to access the Internet after an configIp() call, the MachineMotion device must be rebooted.
    # @status
    #
    def configMachineMotionIp(self, mode, machineIp, machineNetmask, machineGateway):

        # Create a new object and augment it with the key value.
        self.myConfiguration["mode"] = mode
        self.myConfiguration["machineIp"] = machineIp
        self.myConfiguration["machineNetmask"] = machineNetmask
        self.myConfiguration["machineGateway"] = machineGateway


        self.mySocket.emit('configIp', json.dumps(self.myConfiguration))

        time.sleep(1)

    #
    # Function to configure the axis motion.
    # @param axis       --- Description: The axis number.                           --- Type: number [1, 2, 3]
    # @param _u_step    --- Description: uStep setting.                             --- Type: number either [1, 2, 4, 8, 16]
    # @param _mech_gain --- Description: Mechanical gain of the axis in mm / turn.  --- Type: number
    # @status
    #
    def configAxis(self, axis, _u_step, _mech_gain):
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
    #
    # Function to save/persist data in the MachineMotion Controller (key - data pair)
    # @param key --- Description: key is a string that identifies the data to save for future retrieval. --- Type: string or number.
    # @param data --- Description: data is a dictionary containing the data to save. --- Type: dictionary.
    # @status
    #
    def saveData(self, key, data):
        # Create a new object and augment it with the key value.
        dataPack = {}
        dataPack["fileName"] = key;
        dataPack["data"] = data;

        # Send the request to MachineMotion
        self.mySocket.emit('saveData', json.dumps(dataPack))
        time.sleep(0.05)

    #
    # Function to retrieve saved/persisted data in the MachineMotion Controller (key - data pair)
    # @param key --- Description: key is a string that identifies the data to retrieve. --- Type: string.
    # @param callback --- Description: callback is the function to invoke when the asynchronous data is received. --- Type: function with on argument that will contain the data in json serialized format.
    # @status
    #
    def getData(self, key, callback):
        #Send the request to MachineMotion

        self.mySocket.emit('getData', key)

        # On reception of the data invoke the callback function.
        self.mySocket.on('getDataResponse', callback)

    def detachControlDevice(self, port, callback):

        if (self.__isPortValid(port)):
            if port in self.attachedDevices.keys():
                del self.attachedDevices[port]

            # Assign the user callback to the socket response object
            self.detach_control_device_socket_response.set_user_callback(callback)

            # Send a command to reada control device that is connected to the MachineMotion controller
            detachCmd = {"port": port}
            packet = json.dumps(detachCmd)
            self.mySocket.emit('detachControlDevice', packet)

            self.detach_control_device_socket_response.wait_for_response(self.mySocket, 'detachControlDeviceResponse', callback)

            #time.sleep(0.25)

    def attachControlDevice(self, port, device, callback):

        if (self.__isPortValid(port) and self.__isDeviceValid(device)):
            self.attachedDevices[port] = device

            # Assign the user callback to the socket response object
            self.attach_control_device_socket_response.set_user_callback(callback)

            # Send a command to reada control device that is connected to the MachineMotion controller
            attachCmd = {"port": port, "device": device}
            packet = json.dumps(attachCmd)
            self.mySocket.emit('attachControlDevice', packet)

            self.attach_control_device_socket_response.wait_for_response(self.mySocket, 'attachControlDeviceResponse', callback)

            #time.sleep(0.25)

    def readControlDevice(self, port, signal, callback):
        if (self.__isPortValid(port) and self.__isSignalValid(signal)):
            if port not in self.attachedDevices.keys() or self.attachedDevices[port] == "IO_EXPANDER_GENERIC":
                # Unattached or IO device
                callback("true" if (self.portInputs[port] & self.signalMasks[signal] > 0) else "false")
            # Legacy devices
            else:
                # Send a command to read a control device that is connected to the MachineMotion controller
                readCmd = {"port": port, "signal": signal}
                packet = json.dumps(readCmd)
                self.mySocket.emit('readControlDevice', packet)

                self.read_control_device_socket_response.wait_for_response(self.mySocket, 'readControlDeviceResponse', callback)


    def writeControlDevice(self, port, signal, value, callback):
        if (self.__isPortValid(port) and self.__isSignalValid(signal)):
            # Unattached or IO device
            if port not in self.attachedDevices.keys() or self.attachedDevices[port] == "IO_EXPANDER_GENERIC":
                portNumber = self.validPorts.index(port) + 1
                signalNumber = self.validSignals.index(signal) - 4
                self.myMqttClient.publish('digitalOutput/' + str(portNumber) + '/' + str(signalNumber), '1' if value else '0')
                callback("true" if value else "false")
            # Legacy devices
            else :
                # Assign the user callback to the socket response object
                self.write_control_device_socket_response.set_user_callback(callback)

                # Send a command to read a control device that is connected to the MachineMotion controller
                writeCmd = {"port": port, "signal": signal, "value": value}
                packet = json.dumps(writeCmd)
                self.mySocket.emit('writeControlDevice', packet)

                self.write_control_device_socket_response.wait_for_response(self.mySocket, 'writeControlDeviceResponse', callback)



    def __onConnect(self, client, userData, flags, rc):
        if rc == 0:
            self.myMqttClient.subscribe('digitalInput/#')

    def __onMessage(self, client, userData, msg):
        port = int(msg.topic.replace('digitalInput/', '')) - 1
        values = int(msg.payload, 16)
        if(port >= 0 and port < len(self.validPorts)) :
            self.portInputs[self.validPorts[port]] = values

    def __onDisconnect(self, client, userData, rc):
       print("Disconnected with rtn code [%d]"% (rc) )

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
        if(display_connection_debug_messages): print('[SocketIO Connected]')

    def on_reconnect(self):
        if(display_connection_debug_messages): print('[SocketIO Reconnected]')
        global lastSendTimeStamp
        global machineMotionRef

        lastSendTimeStamp = time.time()
        machineMotionRef.myGCode.__setLineNumber__(1)

    def on_disconnect(self):
        if(display_connection_debug_messages): print('[SocketIO Disconnected]')
