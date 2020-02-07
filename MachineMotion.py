# File name:            MachineMotion.py                     #
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

import urllib
# Import if python 2
if sys.version_info[0] < 3 :
    import httplib
# Import if python 3
else :
    import http.client

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
    NORMAL = POSITIVE
    REVERSE = NEGATIVE
    CLOCKWISE = POSITIVE
    COUNTERCLOCKWISE = NEGATIVE

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

DEFAULT_IP = "192.168.7.2"

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
    #indexer_deg_turn                = 36
    roller_conveyor_mm_turn         = 157
    belt_conveyor_mm_turn           = 69.12
    rack_pinion_mm_turn             = 157.08

class STEPPER_MOTOR:
    steps_per_turn      = 200

class AUX_PORTS:
    aux_1 = 0
    aux_2 = 1
    aux_3 = 2

class ENCODER_TYPE:
    real_time = "realtime-position"
    stable = "stable-position"

HARDWARE_MIN_HOMING_FEEDRATE =251
HARDWARE_MAX_HOMING_FEEDRATE= 15999

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
    # Note:
    #   The intent of retrying upon failure here is primarily to reconnect to a dead or unreachable server.
    #   The assumption is that an exception at this level reflects a server failure not to be expected by the client.
    #   This behavior could be made optional.
    while True :
        lConn = None
        try :
            # Review: use keep-alive

            # If python 2
            if sys.version_info[0] < 3 :
                lConn = httplib.HTTPConnection(host)
            # Else python 3
            else :
                lConn = http.client.HTTPConnection(host)

            if None == data:
                lConn.request("GET", path)
            else:
                lConn.request("POST", path, data, {"Content-type": "application/octet-stream"});
            lResponse = lConn.getresponse()
            lResponse = lResponse.read()
            lConn.close()
            return str(lResponse) # Casting as a string is necessary for python3
        except Exception :
            logging.warning("Could not GET %s: %s" % (path, traceback.format_exc()))
            if lConn :
                lConn.close()
                lConn = None
            time.sleep(1)
    return ""

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

        # If python 2
        if sys.version_info[0] < 3 :
            rep = self.__send__("/gcode?%s" % urllib.urlencode({"gcode": "%s" % gCode}))
        # Else python 3
        else :
            rep = self.__send__("/gcode?%s" % urllib.parse.urlencode({"gcode": "%s" % gCode}))

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

    class HomingSpeedOutOfBounds(Exception):
        pass

    # Class constructor
    def __init__(self, machineIp, gCodeCallback=None) :

        self.myConfiguration = {"machineIp": "notInitialized", "machineGateway": "notInitialized", "machineNetmask": "notInitialized"}
        self.myGCode = "notInitialized"

        self.myIoExpanderAvailabilityState = [ False, False, False, False ]
        self.myEncoderRealtimePositions    = [ 0, 0, 0 ]
        self.myEncoderStablePositions    = [ 0, 0, 0 ]
        self.digitalInputs = {}

        self.myConfiguration['machineIp'] = machineIp
        self.IP = machineIp

        # MQTT
        self.myMqttClient = None
        self.myMqttClient = mqtt.Client()
        self.myMqttClient.on_connect = self.__onConnect
        self.myMqttClient.on_message = self.__onMessage
        self.myMqttClient.on_disconnect = self.__onDisconnect
        self.myMqttClient.connect(machineIp)
        self.myMqttClient.loop_start()

        # Default callback
        def emptyCallBack(data) : pass

        #Set callback to default until user initialize it
        self.eStopCallback = emptyCallBack

        # Initializing axis parameters
        self.steps_mm = ["Axis 0 does not exist", "notInitialized", "notInitialized", "notInitialized"]
        self.u_step = ["Axis 0 does not exist", "notInitialized", "notInitialized", "notInitialized"]
        self.mech_gain = ["Axis 0 does not exist", "notInitialized", "notInitialized", "notInitialized"]
        self.direction = ["Axis 0 does not exist", "notInitialized", "notInitialized", "notInitialized"]

        if(gCodeCallback):
            self.__establishConnection(False, gCodeCallback)
        else:
            self.__establishConnection(False, emptyCallBack)

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

    def setContinuousMove(self, axis, speed, accel = None) :

        '''
        desc: Starts an axis using speed mode.
        params:
            axis:
                desc: Axis to move
                type: Number
            speed:
                desc: Speed to move the axis at in mm / sec
                type: Number
            accel:
                desc: Acceleration used to reach the desired speed in mm^2 / sec
                type: Number

        exampleCodePath: emitConveyorMove.py
        '''
        # set motor to speed mode
        reply = self.myGCode.__emit__("V5 " + self.getAxisName(axis) + "2")

        if ( "echo" in reply and "ok" in reply ) : pass
        else :
            raise Exception('Error in gCode execution')
            return False

        if accel is not None :
            # Send speed command with accel
            reply = self.myGCode.__emit__("V4 S" + str(speed / self.mech_gain[axis] * STEPPER_MOTOR.steps_per_turn * self.u_step[axis]) + " A" + str(accel / self.mech_gain[axis] * STEPPER_MOTOR.steps_per_turn * self.u_step[axis]) + " " + self.getAxisName(axis))

            if ( "echo" in reply and "ok" in reply ) : pass
            else :
                raise Exception('Error in gCode execution')
                return False

        else :
            # Send speed command
            reply = self.myGCode.__emit__("V4 S" + str(speed / self.mech_gain[axis] * STEPPER_MOTOR.steps_per_turn * self.u_step[axis]) + " " + self.getAxisName(axis))

            if ( "echo" in reply and "ok" in reply ) : pass
            else :
                raise Exception('Error in gCode execution')
                return False

        return

    def stopContinuousMove(self, axis, accel = None) :
        '''
        desc: Starts an axis using speed mode.
        params:
            axis:
                desc: Axis to move
                type: Number
            accel:
                desc: Acceleration used to reach speed = 0 in mm^2 / sec
                type: Number

        exampleCodePath: emitConveyorMove.py
        '''

        if accel is not None :
            # Send speed command with accel
            reply = self.myGCode.__emit__("V4 S0" + " A" + str(accel / self.mech_gain[axis] * STEPPER_MOTOR.steps_per_turn * self.u_step[axis]) + " " + self.getAxisName(axis))

            if ( "echo" in reply and "ok" in reply ) : pass
            else :
                raise Exception('Error in gCode execution')
                return False

        else :
            # Send speed command
            reply = self.myGCode.__emit__("V4 S0 " + self.getAxisName(axis))

            if ( "echo" in reply and "ok" in reply ) : pass
            else :
                raise Exception('Error in gCode execution')
                return False

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

    def getCurrentPositions(self):
        '''
        desc: Returns the current position of each axis.
        returnValue: A dictionary containing the current position of each axis.
        returnValueType: Dictionary
        note: This function returns the 'open loop' position of each axis. If your axis has an encoder, please use readEncoder.
        '''

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

    def getEndStopState(self):
        '''
        desc: Returns the current state of all home and end sensors. <span style="color:red">What do x_min and x_max refer to? Can we replace this language with home and end?</span>
        returnValue: The states of all end stop sensors {x_min, x_max, y_min, y_max, z_min, z_max} TRIGGERED or not
        returnValueType: Dictionary
        '''

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

    def emitStop(self):
        '''
        desc: Immediately stops all motion of all axes.
        note: This function is a hard stop. It is not a controlled stop and consequently does not decelerate smoothly to a stop. Additionally, this function is not intended to serve as an emergency stop since this stop mechanism does not have safety ratings.
        exampleCodePath: emitStop.py
        '''

        reply = self.myGCode.__emit__("M410")

        if ( "echo" in reply and "ok" in reply ) : pass
        else : raise Exception('Error in gCode execution')

        # Wait to insure that other commands after the emit stop are not flushed.
        time.sleep(0.800) # 300 ms is the minimum allowable command

        return

    def emitHomeAll(self):
        '''
        desc: Initiates the homing sequence of all axes. All axes will home sequentially (Axis 1, then Axis 2, then Axis 3).
        exampleCodePath: emitHomeAll.py
        '''

        reply = self.myGCode.__emit__("G28")

        if ( "echo" in reply and "ok" in reply ) : pass
        else : raise Exception('Error in gCode execution')

        return

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

        reply = self.myGCode.__emit__("G28 " + self.myGCode.__getTrueAxis__(axis))

        if ( "echo" in reply and "ok" in reply ) : pass
        else : raise Exception('Error in gCode execution')

        return

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

        reply = self.myGCode.__emit__("G0 F" +str(speed_mm_per_min))

        if ( "echo" in reply and "ok" in reply ) : pass
        else : raise Exception('Error in gCode execution')

        return

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

        reply = self.myGCode.__emit__("M204 T" + str(accel_mm_per_sec_sqr))

        if ( "echo" in reply and "ok" in reply ) : pass
        else : raise Exception('Error in gCode execution')

        return

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

        # Set to absolute motion mode
        reply = self.myGCode.__emit__("G90")

        if ( "echo" in reply and "ok" in reply ) :

            # Transmit move command
            reply = self.myGCode.__emit__("G0 " + self.myGCode.__getTrueAxis__(axis) + str(position))

            if ( "echo" in reply and "ok" in reply ) : pass

            else : raise Exception('Error in gCode execution')

        else : raise Exception('Error in gCode execution')

        return

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

        if (not isinstance(axes, list) or not isinstance(positions, list)):
            raise TypeError("Axes and Postions must be lists")

        for axis in axes:
            self._restrictInputValue("axis", axis, AXIS_NUMBER)

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
        self._restrictInputValue("direction", direction, DIRECTION)

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

        if (not isinstance(axes, list) or not isinstance(directions, list) or not isinstance(distances, list)):
            raise TypeError("Axes, Postions and Distances must be lists")

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
        reply = self.myGCode.__emit__("G92 " + self.myGCode.__getTrueAxis__(axis) + str(position))

        if ( "echo" in reply and "ok" in reply ) : pass
        else : raise Exception('Error in gCode execution')

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

        reply = self.myGCode.__emit__(gCode)

        if ( "echo" in reply and "ok" in reply ) : pass
        else : raise Exception('Error in gCode execution (reply: %s)' % reply)

        return

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
        self._restrictInputValue("direction", direction, DIRECTION)

        self.direction[axis] = direction

        if(direction == DIRECTION.NORMAL):
            reply = self.myGCode.__emit__("M92 " + self.myGCode.__getTrueAxis__(axis) + str(self.steps_mm[axis]))
        elif (direction == DIRECTION.REVERSE):
            reply = self.myGCode.__emit__("M92 " + self.myGCode.__getTrueAxis__(axis) + "-"+ str(self.steps_mm[axis]))

        if ( "echo" in reply and "ok" in reply ) : pass
        else : raise Exception('Error in gCode execution')

        return

    #
    # Function that indicates if the GCode communication port is ready to send another command.
    # @status
    #
    def isReady(self):
        return True
        #return self.myGCode.__isReady__()

    def isMotionCompleted(self):
        '''
        desc: Indicates if the last move command has completed.
        returnValue: Returns false if the machine is currently executing a g-code command. <span style="color:red">Is this true? Or is it only motion commands? </span>
        returnValueType: Boolean
        '''

        #Sending gCode V0 command to
        reply = self.myGCode.__emit__("V0")

        #Check if not error message
        if ( "echo" in reply and "ok" in reply ) :
            if ("COMPLETED" in reply) : return True
            else : return False
        else : raise Exception('Error in gCode execution')

        return

    def waitForMotionCompletion(self):
        '''
        desc: Pauses python program execution until machine has finished its current movement.
        exampleCodePath: waitForMotionCompletion.py

        '''
        #Sending gCode V0 command to
        reply = self.myGCode.__emit__("V0")

        #Check if not error message
        if ( "echo" in reply and "ok" in reply ) :

            #Recursively calls the function until motion is completed
            if ("COMPLETED" in reply) : return
            else :
                print( "Motion not completed : " + str(self.IP))
                time.sleep(0.5)
                return self.waitForMotionCompletion()

        else : raise Exception('Error in gCode execution')

        return

    def configMachineMotionIp(self, mode = None, machineIp = None, machineNetmask = None, machineGateway = None):
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
            if (machineIp is None) or (machineNetmask is None) or (machineGateway is None) :
               print("NETWORK ERROR: machineIp, machineNetmask and machineGateway cannot be left blank in static mode")

               return False

        # Create a new object and augment it with the key value.

        if mode is not None : self.myConfiguration["mode"] = mode
        if machineIp is not None : self.myConfiguration["machineIp"] = machineIp
        if machineNetmask is not None : self.myConfiguration["machineNetmask"] = machineNetmask
        if machineGateway is not None : self.myConfiguration["machineGateway"] = machineGateway

        HTTPSend(self.IP + ":8000", "/configIp", json.dumps(self.myConfiguration))

        time.sleep(1)

        return

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

        gCodeCommand = "V2"
        for idx, axis in enumerate(axes):

            if units == UNITS_SPEED.mm_per_sec:
                speed_mm_per_min = speeds[idx] * 60
            elif units == UNITS_SPEED.mm_per_min:
                speed_mm_per_min = speeds[idx]

            if speed_mm_per_min < HARDWARE_MIN_HOMING_FEEDRATE:
                raise self.HomingSpeedOutOfBounds("Your desired homing speed of " + str(speed_mm_per_min) + "mm/min can not be less than " + str(HARDWARE_MIN_HOMING_FEEDRATE) + "mm/min (" + str(HARDWARE_MIN_HOMING_FEEDRATE/60) + "mm/sec).")
            if speed_mm_per_min > HARDWARE_MAX_HOMING_FEEDRATE:
                raise self.HomingSpeedOutOfBounds("Your desired homing speed of " + str(speed_mm_per_min) + "mm/min can not be greater than " + str(HARDWARE_MAX_HOMING_FEEDRATE) + "mm/min (" + str(HARDWARE_MAX_HOMING_FEEDRATE/60) + "mm/sec)")

            gCodeCommand = gCodeCommand + " " + self.myGCode.__getTrueAxis__(axis) + str(speed_mm_per_min)

        reply = self.myGCode.__emit__(gCodeCommand)

        if ( "echo" in reply and "ok" in reply ) : pass
        else : raise Exception('Error in gCode execution')

        return

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
        gCodeCommand = "V1"
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

            gCodeCommand = gCodeCommand + " " + self.myGCode.__getTrueAxis__(axis) + str(min_speed_mm_per_min) + ":" + str(max_speed_mm_per_min)


        reply = self.myGCode.__emit__(gCodeCommand)

        if ( "echo" in reply and "ok" in reply ) : pass
        else : raise Exception('Error in gCode execution')

        return

    def configAxis(self, axis, uStep, mechGain) :
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

        self.u_step[axis] = float(uStep)
        self.mech_gain[axis] = float(mechGain)

        self.steps_mm[axis] = STEPPER_MOTOR.steps_per_turn * self.u_step[axis] / self.mech_gain[axis]
        reply = self.myGCode.__emit__("M92 " + self.myGCode.__getTrueAxis__(axis) + str(self.steps_mm[axis]))

        if ( "echo" in reply and "ok" in reply ) : pass
        else : raise Exception('Error in gCode execution')

        return

    def saveData(self, key, data) :
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
        HTTPSend(self.IP + ":8000", "/saveData", json.dumps(dataPack))
        time.sleep(0.05)

        return

    def getData(self, key, callback):
        '''
        desc: Retreives saved/persisted data from the MachineMotion controller (in key-data pairs). If the controller takes more than 3 seconds to return data, the function will return with a value of "Error - getData took too long" under the given key.
        params:
            key:
                desc: A Unique identifier representing the data to be retreived
                type: String
            callback:
                desc: Function to callback to process data.
                type: function
        exampleCodePath: getData_saveData.py
        returnValue: A dictionary containing the saved data.
        returnValueType: Dictionary
        '''
        callback(HTTPSend(self.IP + ":8000", "/getData", key))

        return

    # ------------------------------------------------------------------------
    # Determines if the io-expander with the given id is available
    #
    # @param device - The io-expander device identifier
    # @return.      - True if the io-expander exists; False otherwise
    def isIoExpanderAvailable(self, device) :
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

        return

    def digitalRead(self, deviceNetworkId, pin) :
        '''
        desc: Reads the state of a digital IO modules input pins.
        params:
            deviceNetworkId:
                desc: The IO Modules device network ID. It can be found printed on the product sticker on the back of the digital IO module.
                type: Integer
            pin:
                desc: The index of the input pin.
                type: Integer
        returnValue: Returns 1 if the input pin is logic HIGH (24V) and returns 0 if the input pin is logic LOW (0V).
        exampleCodePath: digitalRead.py

        note: The pin labels on the digital IO module (pin 1, pin 2, pin 3, pin 4) correspond in software to (0, 1, 2, 3). Therefore, digitalRead(deviceNetworkId, 2)  will read the value on input pin 3.
        '''

        if ( not self.isIoExpanderInputIdValid( deviceNetworkId, pin ) ):
            logging.warning("DEBUG: unexpected digital-output parameters: device= " + str(deviceNetworkId) + " pin= " + str(pin))
            return
        if (not hasattr(self, 'digitalInputs')):
            self.digitalInputs = {}
        if (not deviceNetworkId in self.digitalInputs):
            self.digitalInputs[deviceNetworkId] = {}
        if (not pin in self.digitalInputs[deviceNetworkId]):
            self.digitalInputs[deviceNetworkId][pin] = 0
        return self.digitalInputs[deviceNetworkId][pin]

    def digitalWrite(self, deviceNetworkId, pin, value) :
        '''
        desc: Sets voltage on specified pin of digital IO output pin to either logic HIGH (24V) or LOW (0V).
        params:
            deviceNetworkId:
                desc: The IO Modules device network ID. It can be found printed on the product sticker on the back of the digital IO module.
                type: Integer
            pin:
                desc: The output pin number to write to.
                type: Integer
            value:
                desc: Writing '1' or HIGH will set digial output to 24V, writing 0 will set digital output to 0V.
                type: Integer
        exampleCodePath: digitalWrite.py

        note: Output pins maximum sourcing current is 75 mA and the maximum sinking current is 100 mA. The pin labels on the digital IO module (pin 1, pin 2, pin 3, pin 4) correspond in software to (0, 1, 2, 3). Therefore, digitalWrite(deviceNetworkId, 2, 1)  will set output pin 3 to 24V.

        '''

        if ( not self.isIoExpanderOutputIdValid( deviceNetworkId, pin ) ):
            logging.warning("DEBUG: unexpected digitalOutput parameters: device= " + str(deviceNetworkId) + " pin= " + str(pin))
            return
        resp = self.myMqttClient.publish('devices/io-expander/' + str(deviceNetworkId) + '/digital-output/' +  str(pin), '1' if value else '0')

        return

    def emitDwell(self, milliseconds) :
        '''
        desc: Pauses motion for a specified time. This function is non-blocking; your program may accomplish other tasks while the machine is dwelling.
        params:
            miliseconds:
                desc: The duration to wait in milliseconds.
                type: Integer
        note: The timer starts after all previous MachineMotion movement commands have finished execution.
        exampleCodePath: emitDwell.py
        '''
        reply = self.myGCode.__emit__("G4 P"+str(milliseconds))

        if ( "echo" in reply and "ok" in reply ) : pass
        else : raise Exception('Error in gCode execution')

        return

    def readEncoder(self, encoder, readingType=ENCODER_TYPE.real_time) :
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

        if (not self.isEncoderIdValid(encoder)):
            print ( "DEBUG: unexpected encoder identifier: encoderId= " + str(encoder) )
            return

        if readingType == ENCODER_TYPE.real_time:
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
    # Reacts to an eStop event
    #
    # @param {bool} status - true or false
    # @return : call to callback function

    def eStopEvent(self, status) :
        self.eStopCallback(status)
        return

    def triggerEstop (self) :
        '''
        desc: Triggers the MachineMotion software emergency stop, cutting power to all drives and enabling brakes (if any). The software E stop must be released (using releaseEstop()) in order to re-enable the machine.
        '''
        # Publish trigger request on MQTT
        self.myMqttClient.publish(MQTT.PATH.ESTOP_TRIGGER_REQUEST, "message is not important")
        # Wait for response
        MQTTsubscribe.simple(MQTT.PATH.ESTOP_TRIGGER_RESPONSE, retained = False, hostname = self.IP)

        return

    def releaseEstop (self) :
        '''
        desc: Releases the software E-stop and provides power back to the drives.
        '''

        # Publish release request on MQTT
        self.myMqttClient.publish(MQTT.PATH.ESTOP_RELEASE_REQUEST, "message is not important")
        # Wait for response
        MQTTsubscribe.simple(MQTT.PATH.ESTOP_RELEASE_RESPONSE, retained = False, hostname = self.IP)

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
        MQTTsubscribe.simple(MQTT.PATH.ESTOP_SYSTEMRESET_RESPONSE, retained = False, hostname = self.IP)

        return


    def bindeStopEvent (self, callback_function) :
        '''
        desc: Configures a user defined function to execute immediately after an E-stop event.
        params:
            callback_function:
                type: function
                desc: The function to be executed after an e-stop is triggered.
        '''
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
                availability = json.loads(msg.payload)
                if (availability):
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
        self.myGCode = GCode(self.IP)

        # Set the callback to the user specified function. This callback is used to process incoming messages from the machineMotion controller
        self.myGCode.__setUserCallback__(callback)

        return
