# File name:            _MachineMotion.py                     #
# Note:                 Information about all the g-Code            #
#                       commands supported are available at         #
#                       the following location of the SDK:          #
#                       ./documentation                             #

# Import standard libraries
import json, time, threading, sys

# Import package dependent libraries
import paho.mqtt.client as mqtt
import paho.mqtt.subscribe as MQTTsubscribe

import logging
import traceback

import httplib
import urllib

# Misc. Variables

machineMotionRef = None
gCodeCallbackRef = None

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
    POSITIVE = "positive"
    NEGATIVE = "negative"

class AXIS_NUMBER:
    DRIVE1 = 1
    DRIVE2 = 2
    DRIVE3 = 3

class DEFAULT_IP_ADDRESS:
    usb_windows     = "192.168.7.2"
    usb_mac_linux   = "192.168.7.2"
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

class STEPPER_MOTOR:
    steps_per_turn      = 200

class MQTT :
    class PATH :
        ESTOP = "estop"
        ESTOP_STATUS = ESTOP + "/status"
        ESTOP_TRIGGER_REQUEST = ESTOP + "/trigger/request"
        ESTOP_TRIGGER_RESPONSE = ESTOP + "/trigger/response"
        ESTOP_RELEASE_REQUEST = ESTOP + "/release/request"
        ESTOP_RELEASE_RESPONSE = ESTOP + "/release/response"
        ESTOP_SYSTEMRESET_REQUEST = ESTOP + "/systemreset/request"
        ESTOP_SYSTEMRESET_RESPONSE = ESTOP + "/systemreset/response"

def HTTPSend(host, path, data=None) :
    try :
        # Review: use keep-alive
        lConn = httplib.HTTPConnection(host)
        if None == data:
            lConn.request("GET", path)
        else:
            lConn.request("POST", path, data, {"Content-type": "application/octet-stream"});
        lResponse = lConn.getresponse()
        lResponse = lResponse.read()
        lConn.close()
        return lResponse
    except Exception, _pExc :
        logging.warning("Could not GET %s: %s" % (path, traceback.format_exc()))

#
# Class that handles all gCode related communications
# @status
#
class GCode:
    #
    # Class constructor
    # PRIVATE
    # @param socket --- Description: The GCode class requires a socket object to communicate with the controller. The socket object is passed at contruction time.
    # @status
    #
    def __init__(self, ip):
        # Passing in the socket instance at construction
        self.myIp = ip
        self.libPort = ":8000"
        self.ackReceived = False
        self.lineNumber = 1
        self.lastPacket = {"data": "null", "lineNumber": "null"}
        self.gCodeErrors = {"checksum": "Error:checksum mismatch, Last Line: ", "lineNumber": "Error:Line Number is not Last Line Number+1, Last Line: "}
        self.userCallback = None
        self.steps_per_mm = {
            1 : None,
            2 : None,
            3 : None
        }

        return

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
    #
    def __send__(self, cmd, data=None) :

        return HTTPSend(self.myIp + self.libPort, cmd, data)

    #
    # Function to send a raw G-Code ASCII command
    # @param gCode --- Description: gCode is string representing the G-Code command to send to the controller. Type: string.
    # @status
    #
    def __emit__(self, gCode) :

        rep = self.__send__("/gcode?%s" % urllib.urlencode({"gcode": "%s" % gCode}))

        # Call user callback only if relevant
        if self.__userCallback__ is None : pass
        else :
            self.__userCallback__(rep)

        return rep

    @staticmethod
    def __userCallback__(data): return

    #
    # Function that executes upon reception of messages from the motion controller. The user configured callback in ran after this function.
    # PUBLIC
    # @param data --- Description: The data sent by the motion controller. Type: string.
    # @status
    #
    def __rxCallback__(self, data) :

        # Look if the echo of the last command was found in the incoming data
        if (data.find(self.lastPacket['data'])) != -1: pass
            # The last command was acknowledged

        # Special ack for homing
        elif data.find('X:0.00') != -1 and self.lastPacket['data'].find('G28') != -1: pass
            # The last command was acknowledged

        # Special ack for homing
        elif data.find('DEBUG') != -1 and self.lastPacket['data'].find('M111') != -1: pass
            # The last command was acknowledged

        # Look if errors were received
        elif (data.find('Error:') != -1) : pass

        elif (data.find('Resend:') != -1) : pass

        #Calling specific user defined callback
        self.__userCallback__(data)

        return

    def __keepSocketAlive__(self) : pass

    # Private function
    def __setUserCallback__(self, userCallback) :

        # Save the user function to call on incoming messages locally
        self.__userCallback__ = userCallback

        # Start the periodic process that fetches the sockets that were received by the OS
        self.__keepSocketAlive__()

        return

#
# Class used to encapsulate the MachineMotion controller
# @status
#
class MachineMotion :
    # Class variables

    validPorts   = ["AUX1", "AUX2", "AUX3"]
    valid_u_step = [1, 2, 4, 8, 16]

    avg_perf_V0 = {"count": 0, "total": 0}

    can_wait_for_publish = True # TODO: formalize

    # Class constructor
    def __init__(self, gCodeCallback, machineIp) :
        global machineMotionRef
        #global gCodeCallbackRef

        self.myConfiguration = {"machineIp": "notInitialized", "machineGateway": "notInitialized", "machineNetmask": "notInitialized"}
        self.myGCode = "notInitialized"

        self.myIoExpanderAvailabilityState = [ False, False, False, False ]
        self.myEncoderRealtimePositions    = [ 0, 0, 0 ]

        self.myConfiguration['machineIp'] = machineIp

        # MQTT
        self.myMqttClient = None
        self.myMqttClient = mqtt.Client()
        self.myMqttClient.on_connect = self.__onConnect
        self.myMqttClient.on_message = self.__onMessage
        self.myMqttClient.on_disconnect = self.__onDisconnect
        self.myMqttClient.connect(machineIp)
        self.myMqttClient.loop_start()

        machineMotionRef = self
        #gCodeCallbackRef = gCodeCallback

        # Initializing axis parameters
        self.steps_mm = ["Axis 0 does not exist", "notInitialized", "notInitialized", "notInitialized"]
        self.u_step = ["Axis 0 does not exist", "notInitialized", "notInitialized", "notInitialized"]
        self.mech_gain = ["Axis 0 does not exist", "notInitialized", "notInitialized", "notInitialized"]

        self.__establishConnection(False, gCodeCallback)

        return

    # ------------------------------------------------------------------------
    # Moves a motor with a certain set of parameters
    #
    # @param {int} motor - motor # to move
    # @param {float} rotation - number of rotation to do
    # @param {float} speed - motor speed in rotation/sec
    # @param {float} accel - motor acceleration in rotation/sec^2
    # @param {string} reference - "absolute" (default) or "relative"
    # @param {string} type - "synchronous" (default) or "asychronous"
    # @return {bool} - True if command completed properly

    def move(self, motor, rotation = None, speed = None, accel = None, reference = "absolute", type = "synchronous") :

        if rotation is not None :
            # set motor to position mode
            reply = self.myGCode.__emit__("V5 " + self.getAxisName(motor) + "1")

            if ( "echo" in reply and "ok" in reply ) : pass
            else :
                raise Exception('Error in gCode execution')
                return False

            if speed is not None :
                # send speed command (need to convert rotation/s to mm/min )
                reply = self.myGCode.__emit__("G0 F" + str(speed * 60 * self.mech_gain[motor]))

                if ( "echo" in reply and "ok" in reply ) : pass
                else :
                    raise Exception('Error in gCode execution')
                    return False


            if accel is not None :
                # send accel command (need to convert rotation/s^2 to mm/s^2)
                reply = self.myGCode.__emit__("M204 T" + str(accel * self.mech_gain[motor]))

                if ( "echo" in reply and "ok" in reply ) : pass
                else :
                    raise Exception('Error in gCode execution')
                    return False

            if reference is "absolute" :
                # send absolute move command

                # Set to absolute motion mode
                reply = self.myGCode.__emit__("G90")

                if ( "echo" in reply and "ok" in reply ) :

                    # Transmit move command
                    reply = self.myGCode.__emit__("G0 " + self.getAxisName(motor) + str(rotation * self.mech_gain[motor]))

                    if ( "echo" in reply and "ok" in reply ) : pass
                    else :
                        raise Exception('Error in gCode execution')
                        return False

                else :
                    raise Exception('Error in gCode execution')
                    return False

            elif reference is "relative" :
                # send relative move command
                # Set to relative motion mode
                reply = self.myGCode.__emit__("G91")

                if ( "echo" in reply and "ok" in reply ) :
                    # Transmit move command
                    reply = self.myGCode.__emit__("G0 " + self.getAxisName(motor) + str(rotation * self.mech_gain[motor]))

                    if ( "echo" in reply and "ok" in reply ) : pass
                    else :
                        raise Exception('Error in gCode execution')
                        return False

                else :
                    raise Exception('Error in gCode execution')
                    return False

            else :
                return False

            if type is "synchronous" :
                self.waitForMotionCompletion()
                return True

            elif type is "asynchronous" :
                return True
        else :
            if speed is not None :
                # set motor to speed mode
                reply = self.myGCode.__emit__("V5 " + self.getAxisName(motor) + "2")

                if ( "echo" in reply and "ok" in reply ) : pass
                else :
                    raise Exception('Error in gCode execution')
                    return False

                if accel is not None :
                    # Send speed command
                    reply = self.myGCode.__emit__("V4 S" + str(speed * STEPPER_MOTOR.steps_per_turn * self.u_step[motor]) + " A" + str(accel * STEPPER_MOTOR.steps_per_turn * self.u_step[motor]) + " " + self.getAxisName(motor))

                    if ( "echo" in reply and "ok" in reply ) : pass
                    else :
                        raise Exception('Error in gCode execution')
                        return False

                else :
                    # Send speed command
                    reply = self.myGCode.__emit__("V4 S" + str(speed * STEPPER_MOTOR.steps_per_turn * self.u_step[motor]) + " " + self.getAxisName(motor))

                    if ( "echo" in reply and "ok" in reply ) : pass
                    else :
                        raise Exception('Error in gCode execution')
                        return False

            else :
                return False

        return False

    #
    # Function to map API axis labels to motion controller drive labels
    # PRIVATE
    # @param axis --- Description: The API axis label.
    # @status
    #
    def getAxisName(self, drive):
        if drive == 1: return "X"
        elif drive == 2: return "Y"
        elif drive == 3: return "Z"
        else: return "Axis Error"


    # ------------------------------------------------------------------------
    # Determines if the given id is valid for an IO Exapnder.
    #
    # @param {int} id - Device identifier
    # @return {Bool}  - True if valid; False otherwise
    def isIoExpanderIdValid(self, id) :
        if (id < 1 or id > 3):
            return False
        return True

    # ------------------------------------------------------------------------
    # Determines if the given input pin identifier is valid for an IO Exapnder.
    #
    # @param {int} deviceId - Device identifier
    # @param {int} pinId    - Pin identifier
    # @return {Bool}        - True if valid; False otherwise
    def isIoExpanderInputIdValid(self, deviceId, pinId) :
        if ( not self.isIoExpanderIdValid( deviceId ) ):
            return False
        if (pinId < 0 or pinId > 3):
            return False
        return True

    # ------------------------------------------------------------------------
    # Determines if the given output pin identifier is valid for an IO Exapnder.
    #
    # @param {int} deviceId - Device identifier
    # @param {int} pinId    - Pin identifier
    # @return {Bool}        - True if valid; False otherwise
    def isIoExpanderOutputIdValid(self, deviceId, pinId) :
        if ( not self.isIoExpanderIdValid( deviceId ) ):
            return False
        if (pinId < 0 or pinId > 3):
            return False
        return True

    # ------------------------------------------------------------------------
    # Determines if the given id is valid for an encoder.
    #
    # @return {Bool} - True if valid; False otherwise
    def isEncoderIdValid(self, id) :
        if id >= 0 and id <= 3:
            return True
        return False

    # ------------------------------------------------------------------------
    # Get current positions of all axis
    #
    # return Dictionary : axis 1, 2, 3 with position in mm

    def getCurrentPositions(self) :

        positions = {
            1 : None,
            2 : None,
            3 : None
        }

        reply = self.myGCode.__emit__("M114")

        if ( "echo" in reply and "ok" in reply ) :

            positions[1] = float(reply[reply.find('X')+2:(reply.find('Y')-1)])
            positions[2] = float(reply[reply.find('Y')+2:(reply.find('Z')-1)])
            positions[3] = float(reply[reply.find('Z')+2:(reply.find('E')-1)])

        else : raise Exception('Error in gCode execution')

        return positions

    #
    # Function to get the state of home and end sensors
    # @return endstopStates:{x_min, x_max, y_min, y_max, z_min, z_max} TRIGGERED or not
    def getEndStopState(self) :

        states = {
            'x_min' : None,
            'x_max' : None,
            'y_min' : None,
            'y_max' : None,
            'z_min' : None,
            'z_max' : None,
        }

        def trimUntil(S, key) :
            return S[S.find(key) + len(key) :]

        reply = self.myGCode.__emit__("M119")

        if ( "echo" in reply and "ok" in reply ) :
            #Remove first line (echo line)
            reply = trimUntil(reply, "\n")

            if "x_min" in reply :
                keyB = "x_min: "
                keyE = " \n"
                states['x_min'] = reply[(reply.find(keyB) + len(keyB)) : (reply.find(keyE))]

                #Remove x_min line
                reply = trimUntil(reply, "\n")

            else : raise Exception('Error in gCode')

            if "x_max" in reply :
                keyB = "x_max: "
                keyE = " \n"
                states['x_max'] = reply[(reply.find(keyB) + len(keyB)) : (reply.find(keyE))]

                #Remove x_max line
                reply = trimUntil(reply, "\n")

            else : raise Exception('Error in gCode')

            if "y_min" in reply :
                keyB = "y_min: "
                keyE = " \n"
                states['y_min'] = reply[(reply.find(keyB) + len(keyB)) : (reply.find(keyE))]

                #Remove y_min line
                reply = trimUntil(reply, "\n")

            else : raise Exception('Error in gCode')

            if "y_max" in reply :
                keyB = "y_max: "
                keyE = " \n"
                states['y_max'] = reply[(reply.find(keyB) + len(keyB)) : (reply.find(keyE))]

                #Remove y_max line
                reply = trimUntil(reply, "\n")

            else : raise Exception('Error in gCode')

            if "z_min" in reply :
                keyB = "z_min: "
                keyE = " \n"
                states['z_min'] = reply[(reply.find(keyB) + len(keyB)) : (reply.find(keyE))]

                #Remove z_min line
                reply = trimUntil(reply, "\n")

            else : raise Exception('Error in gCode')

            if "z_max" in reply :
                keyB = "z_max: "
                keyE = " \n"
                states['z_max'] = reply[(reply.find(keyB) + len(keyB)) : (reply.find(keyE))]

                #Remove z_max line
                reply = trimUntil(reply, "\n")

            else : raise Exception('Error in gCode')

        else : raise Exception('Error in gCode execution')

        return states

    #
    # Function that will immediately stop all motion of all the axes
    # @status
    #
    def emitStop(self) :

        reply = self.myGCode.__emit__("M410")

        if ( "echo" in reply and "ok" in reply ) : pass
        else : raise Exception('Error in gCode execution')

        # Wait to insure that other commands after the emit stop are not flushed.
        time.sleep(0.800) # 300 ms is the minimum allowable command

        return

    #
    # Function that will initiate the homing sequence of all axes. The sequence will home all axes using the endstop signals
    # @status
    #
    def emitHomeAll(self) :

        reply = self.myGCode.__emit__("G28")

        if ( "echo" in reply and "ok" in reply ) : pass
        else : raise Exception('Error in gCode execution')

        return

    #
    # Function that will initiate the homing sequence for the axis specified. The sequence will home the axis using the endstops signals.
    # @param axis --- Description: "axis" is the axis number that will be set to home location.  --- Type: number.
    # @status
    #
    def emitHome(self, axis) :

        reply = self.myGCode.__emit__("G28 " + self.myGCode.__getTrueAxis__(axis))

        if ( "echo" in reply and "ok" in reply ) : pass
        else : raise Exception('Error in gCode execution')

        return

    #
    # Function to send a displacement speed configuration command
    # @param mm_per_min --- Description: mm_per_mim is the displacement speed in mm/min --- Type: number.
    # @status
    #
    def emitSpeed(self, mm_per_min) :

        reply = self.myGCode.__emit__("G0 F" +str(mm_per_min))

        if ( "echo" in reply and "ok" in reply ) : pass
        else : raise Exception('Error in gCode execution')

        return

    #
    # Function to send a displacement acceleration configuration command
    # @param mm_per_sec_sqr --- Description: mm_per_sec_sqr is the displacement acceleration in mm/sec^2 --- Type: number.
    # @status
    #
    def emitAcceleration(self, mm_per_sec_sqr) :

        reply = self.myGCode.__emit__("M204 T" + str(mm_per_sec_sqr))

        if ( "echo" in reply and "ok" in reply ) : pass
        else : raise Exception('Error in gCode execution')

        return

    #
    # Function to send an absolute move command to the MachineMotion controller
    # @param axis --- Description: axis is the axis on which the command will be applied. --- Type: string or number.
    # @param position --- Description: position is the position from its home location where the axis will go. --- Type: string or number.
    # @status
    #
    def emitAbsoluteMove(self, axis, position) :

        # Set to absolute motion mode
        reply = self.myGCode.__emit__("G90")

        if ( "echo" in reply and "ok" in reply ) :

            # Transmit move command
            reply = self.myGCode.__emit__("G0 " + self.myGCode.__getTrueAxis__(axis) + str(position))

            if ( "echo" in reply and "ok" in reply ) : pass

            else : raise Exception('Error in gCode execution')

        else : raise Exception('Error in gCode execution')

        return

    #
    # Functions to send an absolute move command to the MachineMotion controller in async mode
    # @param axis --- Description: axis is the axis on which the command will be applied. --- Type: string or number.
    # @param position --- Description: position is the position from its home location where the axis will go. --- Type: string or number.
    # @status
    #
    def emitAsyncAbsoluteMove_part1(self) :

        # Set to absolute motion mode
        reply = self.myGCode.__emit__("G90")

        if ( "echo" in reply and "ok" in reply ) : pass
        else : raise Exception('Error in gCode execution')

        return

    def emitAsyncAbsoluteMove_part2(self, axis, position) :

        # Transmit move command
        reply = self.myGCode.__emit__("G0 " + self.myGCode.__getTrueAxis__(axis) + str(position))

        if ( "echo" in reply and "ok" in reply ) : pass
        else : raise Exception('Error in gCode execution')

        return

    #
    # Function to send an absolute move command to the MachineMotion controller. This command can move more than one axis simultaneously
    # @param axes --- Description: axes are the axes on which the command will be applied. Example : [1, 2, 3] --- Type: list of strings or numbers.
    # @param positions --- Description: positions are the positions from their home location where the axes will go. --- Type: list of strings or numbers.
    # @status
    #
    def emitCombinedAxesAbsoluteMove(self, axes, positions) :
        if (not isinstance(axes, list) or not isinstance(positions, list)):
            raise TypeError("Axes and Postions must be lists")

        # Set to absolute motion mode
        reply = self.myGCode.__emit__("G90")

        if ( "echo" in reply and "ok" in reply ) :
            # Transmit move command
            command = "G0 "
            for axis, position in zip(axes, positions):
                command += self.myGCode.__getTrueAxis__(axis) + str(position) + " "

            reply = self.myGCode.__emit__(command)

            if ( "echo" in reply and "ok" in reply ) : pass
            else : raise Exception('Error in gCode execution')

        else : raise Exception('Error in gCode execution')

        return

    #
    # Function to send a relative move command to the MachineMotion controller
    # @param axis --- Description: axis is the axis on which the command will be applied. --- Type: int or string.
    # @param direction --- Description: direction is the direction in which the relative move will be conducted. --- Type: string of value equal to "positive" or "negative"
    # @param distance is the distance of the relative move.
    # @status
    #
    def emitRelativeMove(self, axis, direction, distance):

        # Set to relative motion mode
        reply = self.myGCode.__emit__("G91")

        if ( "echo" in reply and "ok" in reply ) :

            if direction == DIRECTION.POSITIVE :
                distance = "" + str(distance)
            elif direction  == DIRECTION.NEGATIVE :
                distance = "-" + str(distance)

            # Transmit move command
            reply = self.myGCode.__emit__("G0 " + self.myGCode.__getTrueAxis__(axis) + str(distance))

            if ( "echo" in reply and "ok" in reply ) : pass
            else : raise Exception('Error in gCode execution')

        else : raise Exception('Error in gCode execution')

        return

    #
    # Function to send a relative move command to the MachineMotion controller
    # @param axes --- Description: axes on which the command will be applied. Example : [1, 2, 3] --- Type: list of strings or numbers.
    # @param directions --- Description: direction are the directions in which the relative moves will be conducted. --- Type: list of strings of value equal to "positive" or "negative"
    # @param distances are the distances of the relative moves --- Type: list of strings or numbers.
    # @status
    #
    def emitCombinedAxisRelativeMove(self, axes, directions, distances) :
        if (not isinstance(axes, list) or not isinstance(directions, list) or isinstance(distances, list)):
            raise TypeError("Axes and Postions must be lists")

        # Set to relative motion mode
        reply = self.myGCode.__emit__("G91")

        if ( "echo" in reply and "ok" in reply ) :
            # Transmit move command
            command = "G0 "
            for axis, direction, distance in zip(axes, directions, distances):
                if direction == DIRECTION.POSITIVE :
                    distance = "" + str(distance)
                elif direction  == DIRECTION.NEGATIVE :
                    distance = "-" + str(distance)
                command += self.myGCode.__getTrueAxis__(axis) + str(distance) + " "

            reply = self.myGCode.__emit__(command)

            if ( "echo" in reply and "ok" in reply ) : pass
            else : raise Exception('Error in gCode execution')

        else : raise Exception('Error in gCode execution')

        return

    #
    # Function to send a raw G-Code ASCII command
    # @param gCode --- Description: gCode is string representing the G-Code
    #                               command to send to the controller.
    #                               Type: string.
    # @status
    #
    def emitgCode(self, gCode):

        self.myGCode.__emit__(gCode)

        return

    #
    # Function that indicates if the GCode communication port is ready to send another command.
    # @status
    #
    def isReady(self):
        return True
        #return self.myGCode.__isReady__()

    #
    # Function that indicates if the the last move has completed
    # @status
    #
    def isMotionCompleted(self):

        #Sending gCode V0 command to
        reply = self.myGCode.__emit__("V0")

        #Check if not error message
        if ( "echo" in reply and "ok" in reply ) :
            if ("COMPLETED" in reply) : return True
            else : return False
        else : raise Exception('Error in gCode execution')

        return

    def waitForMotionCompletion(self):
        #Sending gCode V0 command to
        reply = self.myGCode.__emit__("V0")

        #Check if not error message
        if ( "echo" in reply and "ok" in reply ) :

            #Recursively calls the function until motion is completed
            if ("COMPLETED" in reply) : return
            else :
                print "Motion not completed : " + str(self.myConfiguration['machineIp'])
                time.sleep(0.5)
                return self.waitForMotionCompletion()

        else : raise Exception('Error in gCode execution')

        return

    #
    # Function to setup the static IP and the router gateway of the MachineMotion controller
    # @param machineIp --- Description: desired static ip address to assign to the MachineMotion controller. --- Type: string (xxx.xxx.xxx.xxxx) where x are numbers.
    # @param gatewayIP --- Description: ip address of the LAN router. Setting a proper gateway ip addreess enables MachineMotion to access the internet for downloads --- Type: string (xxx.xxx.xxx.xxxx) where x are numbers.
    # @note:           --- For the MachineMotion to access the Internet after an configIp() call, the MachineMotion device must be rebooted.
    # @status
    #
    def configMachineMotionIp(self, mode = None, machineIp = None, machineNetmask = None, machineGateway = None) :

        oldIP = self.myConfiguration["machineIp"]

        # Create a new object and augment it with the key value.

        if mode is not None : self.myConfiguration["mode"] = mode
        if machineIp is not None : self.myConfiguration["machineIp"] = machineIp
        if machineNetmask is not None : self.myConfiguration["machineNetmask"] = machineNetmask
        if machineGateway is not None : self.myConfiguration["machineGateway"] = machineGateway

        HTTPSend(oldIP + ":8000", "/configIp", json.dumps(self.myConfiguration))

        time.sleep(1)

        return

    #
    # Function to configure the axis motion.
    # @param axis       --- Description: The axis number.                           --- Type: number [1, 2, 3]
    # @param _u_step    --- Description: uStep setting.                             --- Type: number either [1, 2, 4, 8, 16]
    # @param _mech_gain --- Description: Mechanical gain of the axis in mm / turn.  --- Type: number
    # @status
    #
    def configAxis(self, axis, _u_step, _mech_gain) :
        self.u_step[axis] = float(_u_step)
        self.mech_gain[axis] = float(_mech_gain)

        # validate that the uStep setting is valid
        if (self.valid_u_step.index(self.u_step[axis]) != -1):
            self.steps_mm[axis] = STEPPER_MOTOR.steps_per_turn * self.u_step[axis] / self.mech_gain[axis]
            reply = self.myGCode.__emit__("M92 " + self.myGCode.__getTrueAxis__(axis) + str(self.steps_mm[axis]))

            if ( "echo" in reply and "ok" in reply ) : pass
            else : raise Exception('Error in gCode execution')

        else: pass

        return

    #
    # Function to configure the homing speed.
    # @param axis           --- Description: The axis number.                   --- Type: number [1, 2, 3]
    # @param homing_speed   --- Description: The desired homing speed in mm/min. --- Type: number
    # @status
    #
    def configHomingSpeed(self, axis, homing_speed) :

        # validate that the axis is valid
        if(axis in [1, 2, 3]):
            reply = self.myGCode.__emit__("V2 " + self.myGCode.__getTrueAxis__(axis) + str(homing_speed))

            if ( "echo" in reply and "ok" in reply ) : pass
            else : raise Exception('Error in gCode execution')

        else : pass

        return

    #
    # Function to save/persist data in the MachineMotion Controller (key - data pair)
    # @param key --- Description: key is a string that identifies the data to save for future retrieval. --- Type: string or number.
    # @param data --- Description: data is a dictionary containing the data to save. --- Type: dictionary.
    # @status
    #
    def saveData(self, key, data) :
        # Create a new object and augment it with the key value.
        dataPack = {}
        dataPack["fileName"] = key
        dataPack["data"] = data

        # Send the request to MachineMotion
        HTTPSend(self.myConfiguration['machineIp'] + ":8000", "/saveData", json.dumps(dataPack))
        time.sleep(0.05)

        return

    #
    # Function to retrieve saved/persisted data in the MachineMotion Controller (key - data pair)
    # @param key --- Description: key is a string that identifies the data to retrieve. --- Type: string.
    # @param callback --- Description: callback is the function to invoke when the asynchronous data is received. --- Type: function with on argument that will contain the data in json serialized format.
    # @status
    #
    def getData(self, key, callback) :
        callback(HTTPSend(self.myConfiguration['machineIp'] + ":8000", "/getData", key))

    # ------------------------------------------------------------------------
    # Determines if the io-expander with the given id is available
    #
    # @param device - The io-expander device identifier
    # @return.      - True if the io-expander exists; False otherwise
    def isIoExpanderAvailable(self, device) :
        return self.myIoExpanderAvailabilityState[ device-1 ]

    # ------------------------------------------------------------------------
    # Read the digital input from a pin a given device.
    #
    # @param device - The device identifier (1-3) to read from
    # @param pin.   - The pin index to read from (0-3)
    # @return.      - The latest pin value
    def digitalRead(self, device, pin) :
        if ( not self.isIoExpanderInputIdValid( device, pin ) ):
            logging.warning("DEBUG: unexpected digital-output parameters: device= " + str(device) + " pin= " + str(pin))
            return
        if (not hasattr(self, 'digitalInputs')):
            self.digitalInputs = {}
        if (not device in self.digitalInputs):
            self.digitalInputs[device] = {}
        if (not pin in self.digitalInputs[device]):
            self.digitalInputs[device][pin] = 0
        return self.digitalInputs[device][pin]

    # ------------------------------------------------------------------------
    # Modify the digital output of the given pin a the specified device.
    #
    # @param device - The device identifier (1-3) to write to
    # @param pin. - The pin index to write to (0-3)
    # @param value - The pin value to be written
    # @param waitForPublish - Whether or not to make sure that the broker
    #            acknowledged the message
    def digitalWrite(self, device, pin, value, waitForPublish=True):
        if ( not self.isIoExpanderOutputIdValid( device, pin ) ):
            logging.warning("DEBUG: unexpected digitalOutput parameters: device= " + str(device) + " pin= " + str(pin))
            return
        resp = self.myMqttClient.publish('devices/io-expander/' + str(device) + '/digital-output/' +  str(pin), '1' if value else '0')
        if waitForPublish and MachineMotion.can_wait_for_publish:
            resp.wait_for_publish()

        return

    # ------------------------------------------------------------------------
    # Returns the last received encoder position.
    #
    # @param {int} encoder - The identifier of the encoder.
    # @return              - The relatime encoder position (deled by up to 250ms)
    #
    # NOTE: The encoder position return may be offset by up to 250ms caused by
    #       internal propagation delays
    def readEncoder(self, encoder):
        return self.readEncoderRealtimePosition( encoder )

    # ------------------------------------------------------------------------
    # Returns the last received encoder position.
    #
    # @param {int} encoder - The identifier of the encoder.
    # @return              - The relatime encoder position (deled by up to 250ms)
    #
    # NOTE: The encoder position return may be offset by up to 250ms caused by
    #       internal propagation delays
    def readEncoderRealtimePosition(self, encoder):
        if ( not self.isEncoderIdValid( encoder ) ):
            logging.warning("DEBUG: unexpected encoder identifier: encoderId= " + str(encoder))
            return
        return self.myEncoderRealtimePositions[encoder]

    # ------------------------------------------------------------------------
    # Reacts to an eStop event
    #
    # @param {bool} status - true or false
    # @return : call to callback function

    def eStopEvent(self, status) :
        self.eStopCallback(status)
        return

    # ------------------------------------------------------------------------
    # Triggers the software eStop
    #
    # @param : none
    # @return : none

    def triggerEstop (self) :
        # Publish trigger request on MQTT
        self.myMqttClient.publish(MQTT.PATH.ESTOP_TRIGGER_REQUEST, "message is not important")
        # Wait for response
        MQTTsubscribe.simple(MQTT.PATH.ESTOP_TRIGGER_RESPONSE, retained = False, hostname = self.myConfiguration['machineIp'])

        return

    # ------------------------------------------------------------------------
    # Releases the software eStop
    #
    # @param : none
    # @return : none

    def releaseEstop (self) :
        # Publish release request on MQTT
        self.myMqttClient.publish(MQTT.PATH.ESTOP_RELEASE_REQUEST, "message is not important")
        # Wait for response
        MQTTsubscribe.simple(MQTT.PATH.ESTOP_RELEASE_RESPONSE, retained = False, hostname = self.myConfiguration['machineIp'])

        return

    # ------------------------------------------------------------------------
    # Resets the system
    #
    # @param : none
    # @return : none

    def resetSystem (self) :

        # Publish reset system request on MQTT
        self.myMqttClient.publish(MQTT.PATH.ESTOP_SYSTEMRESET_REQUEST, "message is not important")
        # Wait for response
        MQTTsubscribe.simple(MQTT.PATH.ESTOP_SYSTEMRESET_RESPONSE, retained = False, hostname = self.myConfiguration['machineIp'])

        return

    # ------------------------------------------------------------------------
    # Binds eStop event to a callback function
    #
    # @param : callback function
    # @return : nothing

    def bindeStopEvent (self, callback_function) :
        self.eStopCallback = callback_function
        return

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
            self.myMqttClient.subscribe(MQTT.PATH.ESTOP_STATUS)

        return

    # ------------------------------------------------------------------------
    # Update our internal state from the messages received from the MQTT broker
    #
    # @param client   - The MQTT client identifier (us)
    # @param userData - The user data we have supply on registration (none)
    # @param msg      - The MQTT message recieved
    def __onMessage(self, client, userData, msg):
        topicParts = msg.topic.split('/')
        deviceType = topicParts[1]

        if len(topicParts) > 2 :
            device = int( topicParts[2] )

        if (deviceType == 'io-expander'):
            if (topicParts[3] == 'available'):
                availability = str( msg.payload ).lower()
                if ( availability ):
                    self.myIoExpanderAvailabilityState[device-1] = True
                    return
                else:
                    self.myIoExpanderAvailabilityState[device-1] = False
                    return
            pin = int( topicParts[4] )
            if ( not self.isIoExpanderInputIdValid(device, pin) ):
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

        if (topicParts[0] == MQTT.PATH.ESTOP) :
            if (topicParts[1] == "status") :
                self.eStopEvent(json.loads(msg.payload))

        return

    def __onDisconnect(self, client, userData, rc):
       logging.info("Disconnected with rtn code [%d]"% (rc))

       return

    def __establishConnection(self, isReconnection, callback):

        # Create the web socket
        self.myGCode = GCode(self.myConfiguration['machineIp'])

        # Set the callback to the user specified function. This callback is used to process incoming messages from the machineMotion controller
        self.myGCode.__setUserCallback__(callback)

        return
