# File name:            MachineMotion.py                            #
# Version:              4.7                                         #

# Import standard libraries
import json, time, threading, sys
import traceback
import re


if sys.version_info.major < 3:
    from httplib import HTTPConnection
    from urllib import urlencode
else:
    from http.client import HTTPConnection
    from urllib.parse import urlencode

# Import package dependent libraries
import paho.mqtt.client as mqtt
import paho.mqtt.subscribe as MQTTsubscribe


class AXIS_TYPE:
    BALL_SCREW = "ball_screw"
    BELT_CONVEYOR = "belt_conveyor"
    BELT_RACK = "belt_rack"
    ELECTRIC_CYLINDER = "electric_cylinder"
    ENCLOSED_BALL_SCREW = "enclosed_ball_screw"
    ENCLOSED_LEAD_SCREW = "enclosed_lead_screw"
    ENCLOSED_TIMING_BELT = "enclosed_timing_belt"
    HEAVY_DUTY_ROLLER_CONVEYOR = "heavy_duty_roller_conveyor"
    INDEXER_V2 = "indexer_v2"
    RACK_AND_PINION = "rack_and_pinion"
    RACK_AND_PINION_V2 = "rack_and_pinion_v2"
    ROLLER_CONVEYOR = "roller_conveyor"
    TIMING_BELT = "belt"
    TIMING_BELT_CONVEYOR = "timing_belt_conveyor"
    TELESCOPIC_COLUMN = "telescopic_column"

    CUSTOM = "custom"


class MACHINEMOTION_HW_VERSIONS:
    MMv1 = 1
    MMv2 = 2
    MMv2OneDrive = 3


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
    DRIVE4 = 4


class AXIS_NAME:
    X = "X"
    Y = "Y"
    Z = "Z"
    W = "W"


class UNITS_SPEED:
    mm_per_min = "mm per minute"
    mm_per_sec = "mm per second"


class UNITS_ACCEL:
    mm_per_min_sqr = "mm per minute"
    mm_per_sec_sqr = "mm per second"


class DEFAULT_IP_ADDRESS:
    usb_windows = "192.168.7.2"
    usb_mac_linux = "192.168.7.2"
    ethernet = "192.168.0.2"
    localhost = "127.0.0.1"


DEFAULT_IP = DEFAULT_IP_ADDRESS.usb_windows


class MICRO_STEPS:
    ustep_full = 1
    ustep_2 = 2
    ustep_4 = 4
    ustep_8 = 8
    ustep_16 = 16
    ustep_32 = 32


class MECH_GAIN:
    timing_belt_150mm_turn = 150
    legacy_timing_belt_200_mm_turn = 200
    enclosed_timing_belt_mm_turn = 208
    ballscrew_10mm_turn = 10
    enclosed_ballscrew_16mm_turn = 16
    legacy_ballscrew_5_mm_turn = 5
    indexer_deg_turn = 85
    indexer_v2_deg_turn = 36
    roller_conveyor_mm_turn = 157.7
    belt_conveyor_mm_turn = 73.563
    rack_pinion_mm_turn = 157.08
    rack_pinion_v2_mm_turn = 141.37
    electric_cylinder_mm_turn = 6
    belt_rack_mm_turn = 125
    enclosed_lead_screw_mm_turn = 4
    hd_roller_conveyor_mm_turn = 123.3


class STEPPER_MOTOR:
    steps_per_turn = 200


class AUX_PORTS:
    aux_1 = 0
    aux_2 = 1
    aux_3 = 2
    aux_4 = 3


class ENCODER_TYPE:
    real_time = "realtime-position"
    stable = "stable-position"


class BRAKE_STATES:
    locked = "locked"
    unlocked = "unlocked"
    unknown = "unknown"


class BRAKE:
    PRESENT = "present"
    NONE = "none"


class TUNING_PROFILES:
    DEFAULT = "default"
    CONVEYOR_TURNTABLE = "conveyor_turntable"
    CUSTOM = "custom"


class CONTROL_LOOPS:
    OPEN_LOOP = "open"
    CLOSED_LOOP = "closed"


class POWER_SWITCH:
    ON = "on"
    OFF = "off"


class PUSH_BUTTON:
    class COLOR:
        BLACK = 0
        WHITE = 1

    class STATE:
        PUSHED = "pushed"
        RELEASED = "released"


class MOTOR_SIZE:
    SMALL = "Small Servo"
    MEDIUM = "Medium Servo"
    LARGE = "Large Servo"
    ELECTRIC_CYLINDER = "Nema 17 Stepper"


class GEARBOX:
    RATIO_5_TO_1 = 1.0 / 5.0
    NONE = 1.0


HARDWARE_MIN_HOMING_FEEDRATE = 500
HARDWARE_MAX_HOMING_FEEDRATE = 8000

MIN_MOTOR_CURRENT = 1.5  # Amps
MAX_MOTOR_CURRENT = 10.0  # Amps
ELECTRIC_CYLINDER_MAX_MOTOR_CURRENT = 1.68  # Amps

MAX_IO_ADDRESS = 8

MIN_HOMING_SPEED = 1


class MQTT:
    class PATH:
        ESTOP = "estop"
        ESTOP_STATUS = ESTOP + "/status"
        ESTOP_TRIGGER_REQUEST = ESTOP + "/trigger/request"
        ESTOP_TRIGGER_RESPONSE = ESTOP + "/trigger/response"
        ESTOP_RELEASE_REQUEST = ESTOP + "/release/request"
        ESTOP_RELEASE_RESPONSE = ESTOP + "/release/response"
        ESTOP_SYSTEMRESET_REQUEST = ESTOP + "/systemreset/request"
        ESTOP_SYSTEMRESET_RESPONSE = ESTOP + "/systemreset/response"

        AUX_PORT_POWER = "aux_power"
        AUX_PORT_SAFETY = "aux_safety_power"

        SMARTDRIVES_READY = "smartDrives/areReady"

    TIMEOUT = 10.0  # Number of seconds while we wait for MQTT response


class IO_STATE(object):
    def __init__(self, ioType, deviceId, port, value):
        if not ioType in ["digital-input", "digital-output"]:
            raise Exception(
                'ioType must be: "digital-input" or "digital-output. received: {}'.format(
                    ioType
                )
            )
        elif not 1 <= deviceId <= MAX_IO_ADDRESS:
            raise Exception(
                "deviceId must be between 1 and {}. Received: {}".format(
                    MAX_IO_ADDRESS, deviceId
                )
            )
        elif not 0 <= port <= 3:
            raise Exception("port must be between 0 and 3. Received: {}".format(port))
        elif value not in [0, 1]:
            raise Exception("value must be between 0 or 1. Received: {}".format(value))

        self.ioType = ioType
        self.deviceId = deviceId
        self.port = port
        self.value = value
        self.active = False

    def toJSON(self):
        return {
            "ioType": self.ioType,
            "deviceId": self.deviceId,
            "port": self.port,
            "value": self.value,
            "active": self.active,
        }


class DIGITAL_OUTPUT_STATE(IO_STATE):
    def __init__(self, deviceId, port, value):
        """
        desc: For use with path following applications.
        Defines a digital output's state, which can then be used to configure a connected peripheral's behaviour.
        params:
            deviceId:
                desc: The device ID of the module. Defined by its onboard dipswitch.
                type: Integer between 1 and 8
            port:
                desc: The output port of the module.
                type: integer between 0 and 3
            value:
                desc: The desired value being defined. 1 if the input pin is logic HIGH (24V), 0 if the input pin is logic LOW (0V).
                type: Integer. 0 or 1.
        exampleCodePath: pathFollowing.py
        """
        super(DIGITAL_OUTPUT_STATE, self).__init__(
            "digital-output", deviceId, port, value
        )

    @staticmethod
    def fromJSON(pObject):
        # parse from JSON.
        # returns DIGITAL_OUTPUT_STATE, valid (bool)
        for lField in ["deviceId", "port", "value"]:
            if not lField in pObject or not isinstance(pObject[lField], int):
                return None, False
        return (
            DIGITAL_OUTPUT_STATE(
                pObject["deviceId"], pObject["port"], pObject["value"]
            ),
            True,
        )


class TOOL:
    def __init__(self, number, cwIo, ccwIo=None):
        """
        desc: A TOOL object defines a group of digital outputs to be used in path following applications.
        Each tool must have a clockwise direction, and may optionally have a counter-clockwise direction. When defined and configured,
        the T,M3,M4,M5 and M6 G-Code commands can be used (see: configPathMode)
        params:
            number:
                desc: Corresponds to the tool's index in the motion server's internal tool table.
                When defined, the desired tool can selected using the T command (e.g T1 in G-code selects tool 1).
                type: positive integer.
            cwIo:
                desc: The digital output mapping of device ID, port and value which will turn desired physical tool on in the clockwise direction.
                Related to the M3 and M5 commands in G-Code.
                type: Instance of the DIGITAL_OUTPUT_STATE class
            ccwIo:
                desc: Optional. The digital output mapping of device ID, port and value which will turn desired physical tool on in the counter-clockwise direction.
                Related to the M4 and M5 commands in G-Code.
                type: Instance of the DIGITAL_OUTPUT_STATE class
            exampleCodePath: pathFollowing.py
        """
        if not (isinstance(number, int) and number > -1):
            raise Exception(
                "Tool number must be a non-negative integer. Received: {}".format(
                    number
                )
            )
        if not (isinstance(cwIo, DIGITAL_OUTPUT_STATE)):
            raise Exception(
                "IO for clockwise direction must be an instance of DIGITAL_OUTPUT_STATE. Received: {}".format(
                    cwIo
                )
            )
        self.number = number
        self.cwIo = cwIo
        if ccwIo:
            if not (isinstance(ccwIo, DIGITAL_OUTPUT_STATE)):
                raise Exception(
                    "IO for counter-clockwise direction must be an instance of DIGITAL_OUTPUT_STATE. Received: {}".format(
                        ccwIo
                    )
                )
            self.ccwIo = ccwIo

    def toJSON(self):
        toolJson = {self.number: {"cw": self.cwIo.toJSON()}}
        if hasattr(self, "ccwIo"):
            toolJson[self.number]["ccw"] = self.ccwIo.toJSON()
        return toolJson

    @staticmethod
    def fromJSON(pToolNumber, pObject):
        # validate and parse object into class TOOL
        # returns TOOL, valid (boolean)
        if "cw" not in pObject:
            return None, False
        lClockwiseState, lValid = DIGITAL_OUTPUT_STATE.fromJSON(pObject["cw"])
        if not lValid:
            return None, False
        lCounterClockwiseState = None
        if "ccw" in pObject:
            lCounterClockwiseState, lValid = DIGITAL_OUTPUT_STATE.fromJSON(
                pObject["ccw"]
            )
            if not lValid:
                return None, False
        return TOOL(pToolNumber, lClockwiseState, lCounterClockwiseState), True


DEFAULT_TIMEOUT = 65


def stderr(*args):
    # print(*args, file=sys.stderr, flush=True) only works in python3
    sys.stderr.write(" ".join(map(lambda x: str(x), list(args))) + "\n")
    sys.stderr.flush()


def HTTPSend(
    host,
    path,
    data=None,
    JsonResponse=False,
    JsonRequest=False,
    timeout=DEFAULT_TIMEOUT,
):
    timeout = DEFAULT_TIMEOUT if timeout <= 0 else timeout
    timeouts = [DEFAULT_TIMEOUT for i in range(int(timeout / DEFAULT_TIMEOUT))]
    if timeout % DEFAULT_TIMEOUT > 0:
        timeouts.append(timeout % DEFAULT_TIMEOUT)

    for i, current_timeout in enumerate(timeouts):
        try:
            lConn = HTTPConnection(host, timeout=current_timeout)
            if None == data:
                lConn.request("GET", path)
            else:
                contentType = (
                    "application/json" if JsonRequest else "application/octet-stream"
                )
                headers = {"Content-type": contentType}
                lConn.request("POST", path, data, headers)
            lResponse = lConn.getresponse()
            status = lResponse.status
            lResponse = lResponse.read()
            if status != 200:
                raise Exception(
                    "request http://%s%s failed with status %d: %s"
                    % (host, path, status, str(lResponse))
                )
            if not JsonResponse:
                # Casting as a string is necessary for python3
                return lResponse.decode("utf-8")
            return lResponse
        except Exception as e:
            stderr(
                "ERROR - Could not GET %s: %s (%s)" % (path, traceback.format_exc(), e)
            )
            if lConn:
                lConn.close()
                lConn = None
            if i + 1 == len(timeouts):
                raise e


#
# Class that handles all gCode related communications
# @status
#
class GCode:
    """skip"""

    #
    # Class constructor
    # PRIVATE
    # @param socket --- Description: The GCode class requires a socket object to communicate with the controller. The socket object is passed at contruction time.
    # @status
    #
    def __init__(self, ip, isMMv2=False, isMMv2OneDrive=False):
        # Passing in the socket instance at construction
        self.myIp = ip
        self.libPort = ":8000"
        self.isMMv2 = isMMv2
        self.isMMv2OneDrive = isMMv2OneDrive
        return

    #
    # Function to map API axis labels to motion controller axis labels
    # PRIVATE
    # @param axis --- Description: The API axis label.
    # @status
    #
    def __getTrueAxis__(self, axis):
        if self.isMMv2OneDrive:
            strs = "X"
        elif self.isMMv2:
            strs = "XYZW"
        else:
            strs = "XYZ"

        if axis < 1 or axis > len(strs):
            rng = ", ".join([str(i + 1) for i in range(len(strs))])
            raise Exception(
                "Invalid axis index %d ! (must be in range %s)" % (axis, rng)
            )
        return strs[axis - 1]

    #
    # Function that packages the data in a JSON object and sends to the MachineMotion server over a socket connection.
    # PRIVATE
    #
    def __send__(
        self,
        cmd,
        data=None,
        JsonResponse=False,
        JsonRequest=False,
        timeout=DEFAULT_TIMEOUT,
    ):
        return HTTPSend(
            self.myIp + self.libPort, cmd, data, JsonResponse, JsonRequest, timeout
        )

    #
    # Function to send a raw G-Code ASCII command
    # @param gCode --- Description: gCode is string representing the G-Code command to send to the controller. Type: string.
    # @status
    #
    def __emit__(self, gCode, timeout=DEFAULT_TIMEOUT):
        try:
            path = "/gcode?%s" % urlencode({"gcode": "%s" % gCode})
            rep = self.__send__(path, timeout=timeout)
            # Call user callback only if relevant
            if self.__userCallback__ is not None:
                self.__userCallback__(rep)
            return rep
        except Exception as e:
            raise e

    def __emitEchoOk__(self, gCode, timeout=DEFAULT_TIMEOUT):
        reply = self.__emit__(gCode, timeout=timeout)
        if "echo" in reply and "ok" in reply:
            return reply
        else:
            raise Exception("Error in gCode execution: %s" % str(reply))

    #
    # Function to send commands specifically to the smartDrives
    # @status
    #
    def __sendToSmartDrives__(
        self, url, payload=None, JsonResponse=False, JsonRequest=False
    ):
        rep = self.__send__(url, payload, JsonResponse, JsonRequest)

        # Call user callback only if relevant
        if self.__userCallback__ is None:
            pass
        else:
            self.__userCallback__(
                str(rep)
            )  # Casting as a string is necessary for python3

        return rep

    #
    # Function to send the config to the smartDrives
    # @param config --- Description: config is an object representing the config payload to send to the controller. Type: object.
    # @status
    #
    def __sendConfigToSmartDrives__(self, drive, payload, JsonResponse=False):
        url = "/smartDrives/configuration?%s" % urlencode({"drive": "%s" % drive})

        return self.__sendToSmartDrives__(url, payload, JsonResponse, JsonRequest=True)

    #
    # Function to ask the configuration to the smartDrives
    # @status
    #
    def __askConfigToSmartDrives__(self, drive):
        return self.__sendConfigToSmartDrives__(drive, None, JsonResponse=True)

    #
    # Function to ask the position to the smartDrives
    # @status
    #
    def __askPositionToSmartDrives__(self):
        # Expecting a json encoded response
        return self.__sendToSmartDrives__("/smartDrives/position", JsonResponse=True)

    @staticmethod
    def __userCallback__(data):
        return

    def __keepSocketAlive__(self):
        pass

    # Private function
    def __setUserCallback__(self, userCallback):
        # Save the user function to call on incoming messages locally
        self.__userCallback__ = userCallback

        # Start the periodic process that fetches the sockets that were received by the OS
        self.__keepSocketAlive__()

        return


def _restrictInputValue(argName, argValue, argClass):
    validParams = [i for i in argClass.__dict__.keys() if i[:1] != "_"]
    validValues = [argClass.__dict__[i] for i in validParams]
    if argValue in validValues:
        return

    errorMessage = (
        "An invalid selection was made. Given parameter '"
        + str(argName)
        + "' must be one of the following values:"
    )
    for param in validParams:
        errorMessage += (
            "\n"
            + argClass.__name__
            + "."
            + param
            + " ("
            + str(argClass.__dict__[param])
            + ")"
        )
    raise Exception(errorMessage)


# Version independent numerical checker
def _isNumber(number):
    # Python 2 has two integer types - int and long. There is no 'long integer' in Python 3 anymore : integers in Python 3 are of unlimited size.
    if sys.version_info.major < 3:
        return isinstance(number, (int, long, float))
    else:
        return isinstance(number, (int, float))


class ActuatorConfigParams:
    def __init__(
        self,
        axisType,
        motorSize,
        brake=None,
        tuningProfile=None,
        gearbox=None,
        motorCurrent=None,
        gain=None,
        controlLoop=None,
        homingSpeed=None,
    ):
        """
        desc: Creates a class can be used to configure drives on a Machine Motion.
        params:
            axisType:
                desc: Type of the axis to be configured (impacts the default configuration values)
                type: String of the AXIS_TYPE class
            motorSize:
                desc: Size of the motor connected to the drive
                type: String of the MOTOR_SIZE class
            brake:
                desc: The brake installed on the connected actuator
                type: String of the Brake class | None
            tuningProfile:
                desc: The tuning profile to be assigned to the motor connected to the drive
                type: String of the TUNING_PROFILES class | None
            gearbox:
                desc: The gearbox ratio of the gearbox connected to the motor connected to the drive
                type: Number of the GEARBOX class | None
            motorCurrent:
                desc: The motorCurrent to be assigned to the motor connected to the drive
                type: number | None
            gain:
                desc: The gain to be assigned to the motor connected to the drive
                note: Only for actuators with type CUSTOM
                type: number | None
            controlLoop:
                desc: The control loop used by the motor connected to the drive
                note: Only for actuators with type CUSTOM
                type: String of the CONTROL_LOOPS class | None
            homingSpeed:
                desc: The speed of the homing motion of the actuator in mm/s
                type: number | None
        compatibility: MachineMotion v2.
        exampleCodePath: configActuator.py
        """
        self.axisType = axisType
        self.motorSize = motorSize
        self.brake = brake
        self.gain = gain
        self.tuningProfile = tuningProfile
        self.gearbox = gearbox
        self.motorCurrent = motorCurrent
        self.controlLoop = controlLoop
        self.homingSpeed = homingSpeed

        self.validate()

    def toJSON(self):
        jsonStr = json.dumps(self.__dict__)
        return json.loads(jsonStr)

    def validate(self):
        _restrictInputValue("axisType", self.axisType, AXIS_TYPE)
        _restrictInputValue("motorSize", self.motorSize, MOTOR_SIZE)
        if self.brake != None:
            _restrictInputValue("brake", self.brake, BRAKE)
        if self.tuningProfile != None:
            _restrictInputValue("tuningProfile", self.tuningProfile, TUNING_PROFILES)
        if self.gearbox != None:
            if self.axisType == AXIS_TYPE.CUSTOM and self.gearbox != GEARBOX.NONE:
                raise Exception("Gearbox is not supported for axes of custom type")
            _restrictInputValue("gearbox", self.gearbox, GEARBOX)
        if self.motorCurrent != None:
            if not _isNumber(self.motorCurrent):
                raise Exception("Motor current must be a number")
            if self.motorCurrent > MAX_MOTOR_CURRENT:
                eprint(
                    "Motor current was clipped from %f A to maximum value %f A"
                    % (self.motorCurrent, MAX_MOTOR_CURRENT)
                )
                self.motorCurrent = MAX_MOTOR_CURRENT
            elif self.motorCurrent < MIN_MOTOR_CURRENT:
                eprint(
                    "Motor current value was clipped from %f A to minimum value %f A"
                    % (self.motorCurrent, MIN_MOTOR_CURRENT)
                )
                self.motorCurrent = MIN_MOTOR_CURRENT
        if self.gain != None:
            if self.axisType != AXIS_TYPE.CUSTOM:
                raise Exception("Can only set gain on axes of type CUSTOM")
            if not _isNumber(self.gain):
                raise Exception("Gain must be a number")
        elif self.axisType == AXIS_TYPE.CUSTOM:
            raise Exception("Gain is required for axes of custom type")
        if self.controlLoop != None:
            if self.axisType != AXIS_TYPE.CUSTOM:
                raise Exception("Can only set control loop on axes of type CUSTOM")
            _restrictInputValue("controlLoop", self.controlLoop, CONTROL_LOOPS)
        if self.homingSpeed != None:
            if not _isNumber(self.homingSpeed):
                raise Exception("Homing speed must be a number")
            if self.homingSpeed < MIN_HOMING_SPEED:
                eprint(
                    "Homing speed value was clipped from %f A to minimum value %f A"
                    % (self.homingSpeed, MIN_HOMING_SPEED)
                )
                self.homingSpeed = MIN_HOMING_SPEED


class DriveConfigParams:
    def __init__(self, driveNumber, direction):
        """
        desc: Creates an object representing the configuration for a specific drive on a Machine Motion.
        params:
            driveNumber:
                desc: The number of the drive to be configured
                type: Number of the AXIS_NUMBER class
            direction:
                desc: Defines the direction of motion of the drive
                type: String of the DIRECTION class
            compatibility: MachineMotion v2.
            exampleCodePath: configActuator.py
        """
        self.driveNumber = driveNumber
        self.direction = direction
        self.validate()

    def toJSON(self):
        jsonStr = json.dumps(self.__dict__)
        return json.loads(jsonStr)

    def validate(self):
        _restrictInputValue("driveNumber", self.driveNumber, AXIS_NUMBER)
        _restrictInputValue("direction", self.direction, DIRECTION)


#
# Class used to encapsulate the MachineMotion controller
# @status
#
class MachineMotion(object):
    """z-index:100"""

    # Version independent MQTT parser
    def __parseMessage(self, message, jsonLoads=True):
        # Decode the payload according to the Python version

        if sys.version_info.major < 3:
            payload = message
        else:
            payload = message.decode("utf-8")
        # Json decode the payload or not
        if jsonLoads:
            try:
                return json.loads(payload)
            except Exception as e:
                stderr("WARNING - Invalid JSON payload: " + e)
                return None
        return payload

    # Class constructor
    def __init__(
        self,
        machineIp=DEFAULT_IP_ADDRESS.usb_windows,
        gCodeCallback=(lambda *args: None),
        machineMotionHwVersion=MACHINEMOTION_HW_VERSIONS.MMv1,
    ):
        """
        desc: Constructor of MachineMotion class
        params:
            machineIp:
                desc: IP address of the Machine Motion
                type: string of the DEFAULT_IP_ADDRESS class, or other valid IP address
                default: DEFAULT_IP_ADDRESS.usb_windows
            gCodeCallback:
                desc: Allows to define a custom behaviour for the MachineMotion object
                      when a response is received from the motion controller.
                type: function
                default: None
            machineMotionHwVersion:
                desc: The hardware version of the MachineMotion being used
                type: string of the MACHINEMOTION_HW_VERSIONS class
                default: MACHINEMOTION_HW_VERSIONS.MMv1
        compatibility: MachineMotion v1 and MachineMotion v2.
        exampleCodePath: moveRelative.py, oneDriveControl.py
        """
        self.__async_support = None  # cached flag.
        self.__MachineMotionSoftwareVersion = None  # cached flag.
        self.IP = machineIp
        self.machineMotionHwVersion = machineMotionHwVersion
        self.isMMv2 = self.machineMotionHwVersion >= MACHINEMOTION_HW_VERSIONS.MMv2
        self.isMMv2OneDrive = (
            self.machineMotionHwVersion == MACHINEMOTION_HW_VERSIONS.MMv2OneDrive
        )

        self.myConfiguration = {
            "machineIp": self.IP,
            "machineGateway": "notInitialized",
            "machineNetmask": "notInitialized",
        }
        self.myGCode = GCode(self.IP, self.isMMv2, self.isMMv2OneDrive)
        self.myGCode.__setUserCallback__(gCodeCallback)

        self.maxIo = MAX_IO_ADDRESS if self.isMMv2 else 3
        self.myIoExpanderAvailabilityState = [False] * self.maxIo
        self.myEncoderRealtimePositions = [0, 0, 0]  # MMv1 only
        self.myEncoderStablePositions = [0, 0, 0]  # MMv1 only
        self.digitalInputs = {}
        self.pushButtonStates = {}
        self._userDigitalInputCallback = None

        dev_count = 4 if self.isMMv2 else 3
        self.brakeStatus_control = [
            None for i in range(dev_count)
        ]  # MMv2 does not support control power
        self.brakeStatus_safety = [None for i in range(dev_count)]
        self.estopStatus = None
        self.areSmartDrivesReady = None

        # MQTT
        self.myMqttClient = None
        self.myMqttClient = mqtt.Client()
        self.myMqttClient.on_connect = self.__onConnect
        self.myMqttClient.on_message = self.__onMessage
        self.myMqttClient.on_disconnect = self.__onDisconnect
        self.myMqttClient.connect(machineIp)
        self.myMqttClient.loop_start()

        # Set callback to default until user initialize it
        self.eStopCallback = lambda *args: None

        # Initialize all of the possible push button callbacks
        # The callbacks are stored in a dict of dicts of functions. The dict is first built with
        # the total amount of possible push button addresses, then with the total amount buttons
        # available per module.
        # The callback associated with pressing the black button of module 1 can be accessed as follows:
        # address = 1
        # function = self.pushButtonCallbacks[str(address)][str(PUSH_BUTTON.COLOR.BLACK)]
        self.pushButtonCallbacks = {}
        for address in range(1, self.maxIo + 1):
            self.pushButtonCallbacks.update({str(address): {}})
            validParams = [i for i in PUSH_BUTTON.COLOR.__dict__.keys() if i[:1] != "_"]
            validValues = [str(PUSH_BUTTON.COLOR.__dict__[i]) for i in validParams]
            for button in validValues:
                self.pushButtonCallbacks[str(address)].update(
                    {button: (lambda *args: None)}
                )

        # Initializing axis parameters
        self.steps_mm = [
            "Axis 0 does not exist",
            "notInitialized",
            "notInitialized",
            "notInitialized",
            "notInitialized",
        ]
        self.u_step = [
            "Axis 0 does not exist",
            "notInitialized",
            "notInitialized",
            "notInitialized",
            "notInitialized",
        ]
        self.mech_gain = [
            "Axis 0 does not exist",
            "notInitialized",
            "notInitialized",
            "notInitialized",
            "notInitialized",
        ]
        self.direction = [
            "Axis 0 does not exist",
            "notInitialized",
            "notInitialized",
            "notInitialized",
            "notInitialized",
        ]

        return

    def moveContinuous(self, axis, speed=None, accel=None, direction=None):
        """
        desc: Starts an axis using speed mode.
        params:
            axis:
                desc: Axis to move
                type: Number of AXIS_NUMBER class
            speed:
                desc: Optional. Speed to move the axis at in mm/s. If no speed is specified, the axis will move at the configured axis max speed in the positive axis direction.
                type: Number, positive or negative
            accel:
                desc: Optional. Acceleration used to reach the desired speed, in mm/s^2. If no acceleration is specified, the axis will move at the configured axis max acceleration
                type: Positive number
            direction:
                desc: Optional. Overrides sign of speed. Determines the direction of the continuous move. If no direction is given, the actuator will move according to the direction of `speed`.
                type: String of the DIRECTION class.
        compatibility: MachineMotion v1 and MachineMotion v2. On software versions older than v2.4.0, speed and acceleration arguments are mandatory.
        exampleCodePath: moveContinuous.py
        """

        # Verify argument type to avoid sending garbage in the GCODE
        self._restrictAxisValue(axis)
        lMajor, lMinor, lPatch = self._getSoftwareVersion()
        # Check arguments
        if (lMajor < 2 or (lMajor == 2 and lMinor < 4)) and (
            not _isNumber(speed) or not _isNumber(accel)
        ):
            raise Exception("Unrecognized mandatory speed, acceleration arguments")
        if speed is not None and not _isNumber(speed):
            raise Exception("Invalid Speed argument: " + str(speed))
        if accel is not None and not _isNumber(accel):
            raise Exception("Invalid Acceleration argument: " + str(accel))
        if direction is not None:
            _restrictInputValue("direction", direction, DIRECTION)

        if direction is not None:
            lDirectionStr = "-" if direction == DIRECTION.NEGATIVE else ""
        elif speed is not None and speed < 0:
            lDirectionStr = "-"
        else:
            lDirectionStr = ""

        if lMajor > 2 or (lMajor == 2 and lMinor >= 3):
            lSpeedStr = str(abs(speed)) if speed is not None else ""
            lAccelStr = str(abs(accel)) if accel is not None else ""
            gCode = (
                "V7 S"
                + lDirectionStr
                + lSpeedStr
                + " A"
                + lAccelStr
                + " "
                + self.myGCode.__getTrueAxis__(axis)
            )
        else:
            # Check if steps_per_mm are defined locally. If not, query them.
            if not _isNumber(self.steps_mm[axis]):
                self.populateStepsPerMm()
            # Send speed command with accel
            gCode = (
                "V4 S"
                + lDirectionStr
                + str(abs(speed * self.steps_mm[axis]))
                + " A"
                + str(abs(accel * self.steps_mm[axis]))
                + " "
                + self.myGCode.__getTrueAxis__(axis)
            )
        self.myGCode.__emitEchoOk__(gCode)
        return

    def stopMoveContinuous(self, axis, accel=None):
        """
        desc: Stops an axis using speed mode.
        params:
            axis:
                desc: Axis to move
                type: Number of the AXIS_NUMBER class
            accel:
                desc: Optional. Acceleration used to reach a null speed, in mm/s2. If no accel is specified, the axis will decelerate at the configured max axis acceleration.
                type: Positive number
        compatibility: MachineMotion v1 and MachineMotion v2. On software versions older than v2.4.0, accel argument is mandatory.
        exampleCodePath: moveContinuous.py
        """
        return self.moveContinuous(axis, 0, accel)

    # ------------------------------------------------------------------------
    # Determines if the given id is valid for a drive.
    def _restrictAxisValue(self, axis):
        # MMv1 has drives 1,2,3
        # MMv2 has drives 1,2,3,4
        # MMv2OneDrive has drive 1
        self.myGCode.__getTrueAxis__(axis)
        return True

    # ------------------------------------------------------------------------
    # Determines if the given id is valid for a Brake.
    # @param {int} port - Port identifier
    def _restrictBrakePort(self, port):
        # Brakes are connected to AUX port on MMv1
        # Brakes are connected to JunctionBox brake port on MMv2
        if self.isMMv2OneDrive:
            maxId = 1
        elif self.isMMv2:
            maxId = 4
        else:
            maxId = 3
        if port < 1 or port > maxId:
            rng = ", ".join([str(i + 1) for i in range(maxId)])
            raise Exception(
                "Invalid brake port %d ! (must be in range %s)" % (port, rng)
            )
        return True

    # ------------------------------------------------------------------------
    # Determines if the given id is valid for an IO Exapnder.
    # @param {int} id - Device identifier
    def isIoExpanderIdValid(self, id):
        # IO-Expander IDs range between 1 and maxIo.
        if id < 1 or id > self.maxIo:
            rng = ", ".join([str(i) for i in range(1, self.maxIo + 1)])
            raise Exception(
                "Invalid Digital IO Module device ID %d (must be in range %s)"
                % (id, rng)
            )
        return True

    # ------------------------------------------------------------------------
    # Determines if the given input pin identifier is valid for an IO Exapnder.
    # @param {int} deviceId - Device identifier
    # @param {int} pinId    - Pin identifier
    def isIoExpanderInputIdValid(self, deviceId, pinId):
        self.isIoExpanderIdValid(deviceId)
        # IO-Expander pins range between 0 and 3.
        if pinId < 0 or pinId > 3:
            rng = ", ".join([str(i) for i in range(4)])
            raise Exception(
                "Invalid Digital IO Module pin id %d (must be in range %s)"
                % (pinId, rng)
            )
        return True

    # ------------------------------------------------------------------------
    # Determines if the given output pin identifier is valid for an IO Exapnder.
    # @param {int} deviceId - Device identifier
    # @param {int} pinId    - Pin identifier
    def isIoExpanderOutputIdValid(self, deviceId, pinId):
        return self.isIoExpanderInputIdValid(deviceId, pinId)

    # ------------------------------------------------------------------------
    # Determines if the given push button address is valid for a given push button module.
    # @param {int} deviceId - Device identifier
    # @param {str} buttonId    - Button identifier
    def isPushButtonInputIdValid(self, deviceId, buttonId):
        self.isIoExpanderIdValid(deviceId)
        _restrictInputValue("buttonId", buttonId, PUSH_BUTTON.COLOR)
        return True

    # ------------------------------------------------------------------------
    # Determines if the given id is valid for an encoder.
    def isEncoderIdValid(self, id):
        # For MMv1 only, encoder IDs range 0, 1, 2.
        if id < 0 or id > 2:
            rng = ", ".join([str(i) for i in range(3)])
            raise Exception("invalid encoder id %d (must be in range %s)" % (id, rng))
        return True

    def populateStepsPerMm(self, onlyMarlin=False):
        lMajor, lMinor, lPatch = self._getSoftwareVersion()
        if not (lMajor < 2 or (lMajor == 2 and lMinor < 4)):
            raise Exception(
                "function populateStepsPerMm is not supported by MachineMotion software v2.3.0 and newer"
            )
        # For axes 1,2,3 ask directly from Marlin
        reply_M503 = self.myGCode.__emitEchoOk__("M503")
        beginning = reply_M503.find("M92")
        self.steps_mm[1] = float(
            reply_M503[
                reply_M503.find("X", beginning)
                + 1 : (reply_M503.find("Y", beginning) - 1)
            ]
        )
        self.steps_mm[2] = float(
            reply_M503[
                reply_M503.find("Y", beginning)
                + 1 : (reply_M503.find("Z", beginning) - 1)
            ]
        )
        self.steps_mm[3] = float(
            reply_M503[
                reply_M503.find("Z", beginning)
                + 1 : (reply_M503.find("E", beginning) - 1)
            ]
        )
        self.direction[1] = (
            DIRECTION.NORMAL if self.steps_mm[1] > 0 else DIRECTION.REVERSE
        )
        self.direction[2] = (
            DIRECTION.NORMAL if self.steps_mm[2] > 0 else DIRECTION.REVERSE
        )
        self.direction[3] = (
            DIRECTION.NORMAL if self.steps_mm[3] > 0 else DIRECTION.REVERSE
        )
        return

    def deduce_steps_per_mm(self, mech_gain, u_step, direction):
        steps_per_mm = abs(
            float(STEPPER_MOTOR.steps_per_turn) * float(u_step) / float(mech_gain)
        )
        return -steps_per_mm if direction == DIRECTION.REVERSE else steps_per_mm

    def getDesiredPositions(self, axis=None):
        """
        desc: Returns the desired position of the axes.
        params:
            axis (optional):
                desc: The axis to get the desired position of.
                type: Number
        returnValue: The position of the axis if that parameter was specified, or a dictionary containing the desired position of every axis.
        returnValueType: Number or Dictionary of numbers
        note: This function returns the 'open loop' position of each axis.
        compatibility: Recommended for MachineMotion v1.
        exampleCodePath: getPositions.py
        """

        desiredPositions = self.getCurrentPositions()

        if isinstance(axis, int):  # Axis is a single number, return a number
            self._restrictAxisValue(axis)
            if axis == 4:
                raise Exception(
                    "The desired position of the 4th axis is not supported."
                )
            return desiredPositions[axis]
        else:  # Return the whole dictionary
            return desiredPositions

    def getCurrentPositions(self):
        # Note : Deprecated this function, as it does not do what its name suggests...
        # It returns the desired position, and not the current one.

        reply = self.myGCode.__emitEchoOk__("M114")

        positions = {
            1: float(reply[reply.find("X") + 2 : (reply.find("Y") - 1)]),
            2: float(reply[reply.find("Y") + 2 : (reply.find("Z") - 1)]),
            3: float(reply[reply.find("Z") + 2 : (reply.find("E") - 1)]),
        }

        # Note : The desired position of the 4th drive is unobtainable from the smartDrives.

        return positions

    def getActualPositions(self, axis=None):
        """
        desc: Returns the current position of the axes.
        params:
            axis (optional):
                desc: The axis to get the current position of.
                type: Number
        returnValue: The position of the axis if that parameter was specified, or a dictionary containing the current position of every axis, in mm.
        returnValueType: Number or Dictionary of numbers
        compatibility: MachineMotion v1 and MachineMotion v2.
        exampleCodePath: getPositions.py
        """
        axes = [1, 2, 3]
        if axis != None:  # Restrict argument if we were given some
            self._restrictAxisValue(axis)
            axes = [axis]

        # If MM v1, use M114, and read step counts.
        if not self.isMMv2:
            # Find out step counts
            reply_M114 = self.myGCode.__emitEchoOk__("M114")
            beginning = reply_M114.find("Count")
            step_count = {
                1: int(
                    reply_M114[
                        reply_M114.find("X", beginning)
                        + 3 : (reply_M114.find("Y", beginning) - 1)
                    ]
                ),
                2: int(
                    reply_M114[
                        reply_M114.find("Y", beginning)
                        + 2 : (reply_M114.find("Z", beginning) - 1)
                    ]
                ),
                3: int(
                    reply_M114[
                        reply_M114.find("Z", beginning)
                        + 2 : (
                            reply_M114.find(" ", reply_M114.find("Z", beginning) + 2)
                        )
                    ]
                ),
            }

            # Find out step per mm and then calculate position
            positions = {}
            for drive in axes:
                # If the steps_per_mm are not defined locally, retrieve them from Marlin
                if not _isNumber(self.steps_mm[drive]):
                    self.populateStepsPerMm()
                # Deduce position
                positions[drive] = int(step_count[drive] / self.steps_mm[drive])

        # If MM v2, use smartDrive server route
        else:
            reply = self.myGCode.__askPositionToSmartDrives__()

            if "Error" in str(reply):  # str() encoding is necessary for Python3
                raise Exception("Error in gCode execution")
            else:
                parsedReply = self.__parseMessage(reply)
                if not self.isMMv2OneDrive:
                    positions = {
                        1: parsedReply["X"],
                        2: parsedReply["Y"],
                        3: parsedReply["Z"],
                        4: parsedReply["W"],
                    }
                else:
                    positions = {1: parsedReply["X"]}

        if isinstance(axis, int):  # Axis is a single number, return a number
            return positions[axis]
        else:  # Return the whole dictionary
            return positions

    def getEndStopState(self):
        """
        desc: Returns the current state of all home and end sensors.
        returnValue: The states of all end stop sensors {x_min, x_max, y_min, y_max, z_min, z_max} "TRIGGERED" or "open"
        returnValueType: Dictionary
        compatibility: MachineMotion v1 and MachineMotion v2.
        exampleCodePath: getEndStopState.py
        """

        if self.isMMv2OneDrive:
            states = {"x_min": None, "x_max": None}
        else:
            states = {
                "x_min": None,
                "x_max": None,
                "y_min": None,
                "y_max": None,
                "z_min": None,
                "z_max": None,
                "w_min": None,
                "w_max": None,
            }

        def trimUntil(S, key):
            return S[S.find(key) + len(key) :]

        reply = self.myGCode.__emitEchoOk__("M119")

        keyE = "\\n"
        if keyE not in reply:
            keyE = "\n"

        # Remove first line (echo line)
        reply = trimUntil(reply, keyE)
        if "x_min" in reply:
            keyB = "x_min: "
            states["x_min"] = reply[(reply.find(keyB) + len(keyB)) : (reply.find(keyE))]

            # Remove x_min line
            reply = trimUntil(reply, keyE)
        else:
            raise Exception("Error in gCode")

        if "x_max" in reply:
            keyB = "x_max: "
            states["x_max"] = reply[(reply.find(keyB) + len(keyB)) : (reply.find(keyE))]

            # Remove x_max line
            reply = trimUntil(reply, keyE)

        else:
            raise Exception("Error in gCode")

        if not self.isMMv2OneDrive:
            if "y_min" in reply:
                keyB = "y_min: "
                states["y_min"] = reply[
                    (reply.find(keyB) + len(keyB)) : (reply.find(keyE))
                ]

                # Remove y_min line
                reply = trimUntil(reply, keyE)

            else:
                raise Exception("Error in gCode")

            if "y_max" in reply:
                keyB = "y_max: "
                states["y_max"] = reply[
                    (reply.find(keyB) + len(keyB)) : (reply.find(keyE))
                ]

                # Remove y_max line
                reply = trimUntil(reply, keyE)

            else:
                raise Exception("Error in gCode")

            if "z_min" in reply:
                keyB = "z_min: "
                states["z_min"] = reply[
                    (reply.find(keyB) + len(keyB)) : (reply.find(keyE))
                ]

                # Remove z_min line
                reply = trimUntil(reply, keyE)

            else:
                raise Exception("Error in gCode")

            if "z_max" in reply:
                keyB = "z_max: "
                states["z_max"] = reply[
                    (reply.find(keyB) + len(keyB)) : (reply.find(keyE))
                ]

                # Remove z_max line
                reply = trimUntil(reply, keyE)

            else:
                raise Exception("Error in gCode")

            if "w_min" in reply:
                keyB = "w_min: "
                states["w_min"] = reply[
                    (reply.find(keyB) + len(keyB)) : (reply.find(keyE))
                ]

                # Remove w_min line
                reply = trimUntil(reply, keyE)

            elif self.isMMv2:
                raise Exception("Error in gCode")

            if "w_max" in reply:
                keyB = "w_max: "
                states["w_max"] = reply[
                    (reply.find(keyB) + len(keyB)) : (reply.find(keyE))
                ]

                # Remove w_max line
                reply = trimUntil(reply, keyE)

            elif self.isMMv2:
                raise Exception("Error in gCode")

        return states

    def stopAllMotion(self):
        """
        desc: Immediately stops all motion of all axes.
        note: This function is a hard stop. It is not a controlled stop and consequently does not decelerate smoothly to a stop. Additionally, this function is not intended to serve as an emergency stop since this stop mechanism does not have safety ratings.
        compatibility: MachineMotion v1 and MachineMotion v2.
        exampleCodePath: stopAllMotion.py
        """
        return self.myGCode.__emitEchoOk__("M410")

    def stopAxis(self, *axes):
        """
        desc: Immediately stops motion on a set of axes.
        params:
              *axes:
                  desc: Axis or axes to stop.
                  type: Number or numbers separated by a comma, of the AXIS_NUMBER class
        compatibility: MachineMotion v2.
        exampleCodePath: moveIndependentAxis.py
        """
        lAxes = list(axes)
        if not self._getAsyncSupport():
            raise Exception("Independent axis control not supported on this version")
        if len(lAxes) == 0:
            return
        for lAxis in lAxes:
            self._restrictAxisValue(lAxis)
        return self.myGCode.__emitEchoOk__(
            "M410 " + " ".join(map(self.myGCode.__getTrueAxis__, lAxes))
        )

    def moveToHomeAll(self):
        """
        desc: Initiates the homing sequence of all axes. All axes will move home simultaneously on MachineMotion v2, and sequentially on MachineMotion v1.
        compatibility: MachineMotion v1 and MachineMotion v2.
        exampleCodePath: moveToHomeAll.py
        """
        try:
            return self.myGCode.__emitEchoOk__("G28", timeout=DEFAULT_TIMEOUT * 5)
        except Exception as e:
            self.stopAllMotion()
            raise e

    def moveToHome(self, axis):
        """
        desc: Initiates the homing sequence for the specified axis.
        params:
            axis:
                desc: The axis to be homed.
                type: Number
        note: If configAxisDirection is set to "normal" on axis 1, axis 1 will home itself towards sensor 1A. If configAxisDirection is set to "reverse" on axis 1, axis 1 will home itself towards sensor 1B.
        compatibility: MachineMotion v1 and MachineMotion v2.
        exampleCodePath: moveToHome.py
        """
        self._restrictAxisValue(axis)
        gCode = "G28 " + self.myGCode.__getTrueAxis__(axis)
        try:
            return self.myGCode.__emitEchoOk__(gCode, timeout=DEFAULT_TIMEOUT * 5)
        except Exception as e:
            self.stopAllMotion()
            raise e

    def _getSoftwareVersion(self):
        if self.__MachineMotionSoftwareVersion != None:
            return self.__MachineMotionSoftwareVersion

        lResponseRaw = self.myGCode.__sendToSmartDrives__("/health", JsonResponse=True)
        # GET /health
        # {
        #     time_server_started_at: '2022-01-28T19:43:17.934Z',
        #     mqtt_services_running: {
        #         'services/mm-io-expander-hub/version': 'v2.0',
        #         'services/mm-vention-control/version': '2.3.0',
        #     },
        #     devices: {
        #         'devices/io-expander/1/available': 'false',
        #         'devices/io-expander/2/available': 'false',
        #         'devices/io-expander/3/available': 'false',
        #     },
        #     ip: [],
        #     motion_controller_reachable: true,
        #     io_expander_hub_running: 'io_expander_hub',
        #     estop_triggered: true,
        #     time_now: '2022-01-28T20:09:04.983Z',
        # }
        lResponse = json.loads(lResponseRaw)
        if "mqtt_services_running" not in lResponse:
            self.__MachineMotionSoftwareVersion = [0, 0, 0]
            return self.__MachineMotionSoftwareVersion

        if (
            "services/mm-vention-control/version"
            not in lResponse["mqtt_services_running"]
        ):
            self.__MachineMotionSoftwareVersion = [0, 0, 0]
            return self.__MachineMotionSoftwareVersion

        lVersion = re.search(
            r"(\d+).(\d+).?(\d*)",
            lResponse["mqtt_services_running"]["services/mm-vention-control/version"],
        )
        if lVersion:
            lMajor = int(lVersion.group(1))
            lMinor = int(lVersion.group(2))
            lPatch = int(lVersion.group(3)) if lVersion.group(3) else 0
        else:
            lMajor, lMinor, lPatch = 0, 0, 0

        self.__MachineMotionSoftwareVersion = [lMajor, lMinor, lPatch]
        return self.__MachineMotionSoftwareVersion

    def _getAsyncSupport(self):
        # cached flag to check if machine motion supports independent axes.
        if self.__async_support != None:
            # return cached value.
            return self.__async_support

        lMajor, lMinor, lPatch = self._getSoftwareVersion()
        self.__async_support = False
        if lMajor > 2:
            self.__async_support = True
        if lMajor >= 2 and lMinor >= 4:
            self.__async_support = True
        return self.__async_support

    def setAxisMaxSpeed(self, axis, speed):
        """
        desc: Set maximum speed for a given axis.
        params:
            axis:
                desc: The target to set axis speed.
                type: Number of the AXIS_NUMBER class.
            speed:
                desc: The axis speed in mm/s.
                type: Number
        compatibility: MachineMotion v2.
        exampleCodePath: speedAndAcceleration.py, moveIndependentAxis.py
        """
        if not self.isMMv2:
            raise Exception("Cannot set axis speed on MachineMotionV1")
        if not self._getAsyncSupport():
            raise Exception(
                "Independent axis control not supported on this MachineMotion software version"
            )
        self._restrictAxisValue(axis)
        return self.myGCode.__sendToSmartDrives__(
            "/smartDrives/maxSpeed/" + str(axis),
            json.dumps({"maxSpeed": speed}),
            True,
            True,
        )

    def getAxisMaxSpeed(self, axis):
        """
        desc: Get maximum speed for a given axis.
        params:
            axis:
                desc: The target axis to read maximum speed from.
                type: Number of the AXIS_NUMBER class.
        compatibility: MachineMotion v2.
        returnValue: Axis max speed in mm/s
        returnValueType: Number
        exampleCodePath: speedAndAcceleration.py
        """
        if not self.isMMv2:
            raise Exception("Cannot get axis speed on MachineMotionV1")
        if not self._getAsyncSupport():
            raise Exception(
                "Independent axis control not supported on this MachineMotion software version"
            )
        self._restrictAxisValue(axis)
        lResponse = self.myGCode.__sendToSmartDrives__(
            "/smartDrives/maxSpeed/" + str(axis), JsonResponse=True
        )
        lParsed = json.loads(lResponse)
        return lParsed["maxSpeed"]

    def getActualSpeeds(self, axis=None):
        """
        desc: Get the current measured speed of all or one axis, in mm/s
        params:
            axis:
                desc: The axis to get the current speed of. If None is passed, all axes will be checked.
                type: Number of the AXIS_NUMBER class, or None
                default: None
        compatibility: MachineMotion v2, software version 2.2.0 and newer.
        returnValue: The current speed of the axis if that parameter was specified, or a dictionary containing the current speed of every axis, in mm/s.
        returnValueType: Number or Dictionary of numbers
        exampleCodePath: speedAndAcceleration.py
        """
        lMajor, lMinor, lPatch = self._getSoftwareVersion()
        if lMajor < 2 or (lMajor == 2 and lMinor < 2):
            raise Exception(
                "getActualSpeeds is not supported on this MachineMotion software version"
            )

        if axis != None:  # Restrict argument if we were given some
            self._restrictAxisValue(axis)

        lResponse = self.myGCode.__sendToSmartDrives__(
            "/smartDrives/get/actualSpeed", JsonResponse=True
        )
        lParsed = json.loads(lResponse)["actual speed"]
        lSpeeds = {}
        for axis_string in lParsed:
            lSpeeds[int(axis_string)] = lParsed[axis_string]

        if isinstance(axis, int):  # Axis is a single number, return a number
            return lSpeeds[axis]
        else:  # Return the whole dictionary
            return lSpeeds

    def setAxisMaxAcceleration(self, axis, acceleration):
        """
        desc: Set maximum acceleration for a given axis.
        params:
            axis:
                desc: The target to set axis acceleration.
                type: Number of the AXIS_NUMBER class.
            acceleration:
                desc: The axis acceleration in mm/s^2
                type: Number
        compatibility: MachineMotion v2.
        exampleCodePath: speedAndAcceleration.py, moveIndependentAxis.py
        """
        if not self.isMMv2:
            raise Exception("Cannot set axis acceleration on MachineMotionV1")
        if not self._getAsyncSupport():
            raise Exception(
                "Independent axis control not supported on this MachineMotion software version"
            )
        self._restrictAxisValue(axis)
        return self.myGCode.__sendToSmartDrives__(
            "/smartDrives/maxAcceleration/" + str(axis),
            json.dumps({"maxAcceleration": acceleration}),
            True,
            True,
        )

    def getAxisMaxAcceleration(self, axis):
        """
        desc: Get maximum acceleration for a given axis.
        params:
            axis:
                desc: The target axis to read maximum acceleration from.
                type: Number of the AXIS_NUMBER class.
        compatibility: MachineMotion v2.
        returnValue: Max acceleration for the axis in mm/s^2.
        returnValueType: Number
        exampleCodePath: speedAndAcceleration.py

        """
        if not self.isMMv2:
            raise Exception("Cannot get axis speed on MachineMotionV1")
        if not self._getAsyncSupport():
            raise Exception(
                "Independent axis control not supported on this MachineMotion software version"
            )
        self._restrictAxisValue(axis)
        lResponse = self.myGCode.__sendToSmartDrives__(
            "/smartDrives/maxAcceleration/" + str(axis), JsonResponse=True
        )
        lParsed = json.loads(lResponse)
        return lParsed["maxAcceleration"]

    def moveToPosition(self, axis, position):
        """
        desc: Moves the specified axis to a desired end location.
        params:
            axis:
                desc: The axis which will perform the absolute move command.
                type: Number
            position:
                desc: The desired end position of the axis movement.
                type: Number
        compatibility: MachineMotion v1 and MachineMotion v2.
        exampleCodePath: moveToPosition.py
        """
        self._restrictAxisValue(axis)
        if not self._getAsyncSupport():
            # Set to absolute motion mode
            self.myGCode.__emitEchoOk__("G90")
            # Transmit move command
            self.myGCode.__emitEchoOk__(
                "G0 " + self.myGCode.__getTrueAxis__(axis) + str(position)
            )
            return

        lParams = dict()
        lParams[axis] = position
        return self.myGCode.__sendToSmartDrives__(
            "/smartDrives/motion/moveAbsolute", json.dumps(lParams), True, True
        )

    def moveToPositionCombined(self, axes, positions):
        """
        desc: Moves multiple specified axes to their desired end locations synchronously.
        params:
            axes:
                desc: The axes which will perform the move commands. Ex - [1 ,3]
                type: List
            positions:
                desc: The desired end position of all axess movement. Ex - [50, 10]
                type: List
        compatibility: MachineMotion v1 and MachineMotion v2.
        exampleCodePath: moveToPositionCombined.py
        note: The current speed and acceleration settings are applied to the combined motion of the axes.
        """

        if (not isinstance(axes, list) or not isinstance(positions, list)) or len(
            axes
        ) != len(positions):
            raise TypeError("Axes and Positions must be lists of the same length")
        for axis in axes:
            self._restrictAxisValue(axis)

        if self._getAsyncSupport():
            lParams = dict(zip(axes, positions))
            return self.myGCode.__sendToSmartDrives__(
                "/smartDrives/motion/moveAbsolute", json.dumps(lParams), True, True
            )
        # Set to absolute motion mode
        self.myGCode.__emitEchoOk__("G90")

        # Transmit move command
        command = "G0"
        for axis, position in zip(axes, positions):
            command += " " + self.myGCode.__getTrueAxis__(axis) + str(position)

        self.myGCode.__emitEchoOk__(command)

        return

    def moveRelative(self, axis, distance):
        """
        desc: Moves the specified axis the specified distance.
        params:
            axis:
                desc: The axis to move.
                type: Integer
            distance:
                desc: The travel distance in mm.
                type: Number
        compatibility: MachineMotion v1 and MachineMotion v2.
        exampleCodePath: moveRelative.py
        """

        self._restrictAxisValue(axis)
        if not self._getAsyncSupport():
            # Set to relative motion mode
            self.myGCode.__emitEchoOk__("G91")
            # Transmit move command
            self.myGCode.__emitEchoOk__(
                "G0 " + self.myGCode.__getTrueAxis__(axis) + str(distance)
            )
            return
        lParams = dict()
        lParams[axis] = distance
        return self.myGCode.__sendToSmartDrives__(
            "/smartDrives/motion/moveRelative", json.dumps(lParams), True, True
        )

    def moveRelativeCombined(self, axes, distances):
        """
        desc: Moves the multiple specified axes the specified distances.
        params:
            axes:
                desc: The axes to move. Ex-[1,3]
                type: List of Integers
            distances:
                desc: The travel distances in mm. Ex - [10, 40]
                type: List of Numbers
        compatibility: MachineMotion v1 and MachineMotion v2.
        exampleCodePath: moveRelativeCombined.py
        note: The current speed and acceleration settings are applied to the combined motion of the axes.
        """

        if (not isinstance(axes, list) or not isinstance(distances, list)) or len(
            axes
        ) != len(distances):
            raise TypeError("Axes and Distances must be lists of the same length")

        for axis in axes:
            self._restrictAxisValue(axis)

        if self._getAsyncSupport():
            lParams = dict(zip(axes, distances))
            return self.myGCode.__sendToSmartDrives__(
                "/smartDrives/motion/moveRelative", json.dumps(lParams), True, True
            )

        # Set to relative motion mode
        self.myGCode.__emitEchoOk__("G91")

        # Transmit move command
        command = "G0"
        for axis, distance in zip(axes, distances):
            command += " " + self.myGCode.__getTrueAxis__(axis) + str(distance)

        self.myGCode.__emitEchoOk__(command)

        return

    def setPosition(self, axis, position):
        """
        desc: Override the current position of the specified axis to a new value.
        params:
            axis:
                desc: Overrides the position on this axis.
                type: Number
            position:
                desc: The new position value in mm.
                type: Number
        compatibility: MachineMotion v1 and MachineMotion v2.
        exampleCodePath: setPosition.py
        """
        self._restrictAxisValue(axis)

        # Transmit move command
        self.myGCode.__emitEchoOk__(
            "G92 " + self.myGCode.__getTrueAxis__(axis) + str(position)
        )

        return

    def emitgCode(self, gCode):
        """
        desc: Executes raw gCode on the controller.
        params:
            gCode:
                desc: The g-code that will be passed directly to the controller.
                type: String
        note: All movement commands sent to the controller are by default in mm.
        compatibility: Recommended for MachineMotion v1.
        exampleCodePath: emitgCode.py
        """

        return self.myGCode.__emit__(gCode)

    def isMotionCompleted(self, axis=None):
        """
        desc: Indicates if the last move command has completed.
        params:
             axis:
                desc: Target axis to check. If None is passed, all axes will be checked.
                type: Number of the AXIS_NUMBER class, or None
                default: None
        returnValue: Returns false if the machine is currently executing a movement command.
        returnValueType: Boolean or Dictionary of Booleans
        compatibility: MachineMotion v1 and MachineMotion v2.
        exampleCodePath: getPositions.py, moveIndependantAxis.py
        note: isMotionCompleted does not account for on-going continuous moves.
        """
        # Sending gCode V0 command to
        if axis == None or not self.isMMv2:
            reply = self.myGCode.__emitEchoOk__("V0")
            return "COMPLETED" in reply
        if not self._getAsyncSupport():
            raise Exception(
                "Independent axis control not supported on this MachineMotion software version"
            )
        self._restrictAxisValue(axis)
        lResponse = self.myGCode.__sendToSmartDrives__(
            "/smartDrives/complete/" + self.myGCode.__getTrueAxis__(axis),
            JsonResponse=True,
        )
        lParsed = json.loads(lResponse)
        return lParsed["complete"]

    def waitForMotionCompletion(self, axis=None):
        """
        desc: Pauses python program execution until machine has finished its current movement.
        params:
            axis: Target axis to check. If None is passed, all axes will be checked.
            type: Number or None
            default: None
        compatibility: MachineMotion v1 and MachineMotion v2.
        exampleCodePath: waitForMotionCompletion.py, moveIndependentAxis.py
        note: waitForMotionCompletion does not account for on-going continuous moves.
        """
        delay = 0.5
        if self.isMMv2:
            delay = (
                0.1  # Shorter delay is possible on MMv2 because of the BeagleBone AI
            )
        while not self.isMotionCompleted(axis):
            time.sleep(delay)
        return

    def configHomingSpeed(self, axes, speeds, units=UNITS_SPEED.mm_per_sec):
        try:
            axes = list(axes)
            speeds = list(speeds)
        except TypeError:
            axes = [axes]
            speeds = [speeds]

        if len(axes) != len(speeds):
            raise Exception("Axes and speeds must be of same length")

        for axis in axes:
            self._restrictAxisValue(axis)

        gCodeCommand = "V2"
        for idx, axis in enumerate(axes):
            if units == UNITS_SPEED.mm_per_sec:
                speed_mm_per_min = speeds[idx] * 60
            elif units == UNITS_SPEED.mm_per_min:
                speed_mm_per_min = speeds[idx]

            if speed_mm_per_min < HARDWARE_MIN_HOMING_FEEDRATE:
                raise Exception(
                    "Your desired homing speed of "
                    + str(speed_mm_per_min)
                    + "mm/min can not be less than "
                    + str(HARDWARE_MIN_HOMING_FEEDRATE)
                    + "mm/min ("
                    + str(HARDWARE_MIN_HOMING_FEEDRATE / 60)
                    + "mm/s)."
                )
            if speed_mm_per_min > HARDWARE_MAX_HOMING_FEEDRATE:
                raise Exception(
                    "Your desired homing speed of "
                    + str(speed_mm_per_min)
                    + "mm/min can not be greater than "
                    + str(HARDWARE_MAX_HOMING_FEEDRATE)
                    + "mm/min ("
                    + str(HARDWARE_MAX_HOMING_FEEDRATE / 60)
                    + "mm/s)"
                )

            gCodeCommand = (
                gCodeCommand
                + " "
                + self.myGCode.__getTrueAxis__(axis)
                + str(speed_mm_per_min)
            )

        self.myGCode.__emitEchoOk__(gCodeCommand)

        return

    def configAxis(self, axis, uStep, mechGain):
        """
        desc: Configures motion parameters for a single axis on the MachineMotion v1.
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
        compatibility: MachineMotion v1 only.
        exampleCodePath: configAxis.py
        """
        if self.isMMv2:
            raise Exception(
                "The function configAxis is not supported on MachineMotion v2."
            )

        self._restrictAxisValue(axis)
        _restrictInputValue("uStep", uStep, MICRO_STEPS)

        self.u_step[axis] = int(uStep)
        self.mech_gain[axis] = abs(float(mechGain))
        self.direction[axis] = (
            DIRECTION.NORMAL if float(mechGain) > 0 else DIRECTION.REVERSE
        )
        self.steps_mm[axis] = self.deduce_steps_per_mm(
            self.mech_gain[axis], self.u_step[axis], self.direction[axis]
        )

        self.myGCode.__emitEchoOk__(
            "M92 " + self.myGCode.__getTrueAxis__(axis) + str(self.steps_mm[axis])
        )

        return

    def configAxisDirection(self, axis, direction):
        """
        desc: Configures a single axis to operate in either clockwise (normal) or counterclockwise (reverse) mode. Refer to the Automation System Diagram for the correct axis setting.
        params:
            axis:
                desc: The specified axis.
                type: Number
            direction:
                desc: A string from the DIRECTION class. Either 'DIRECTION.NORMAL' or 'DIRECTION.REVERSE'. Normal direction means the axis will home towards end stop sensor A and reverse will make the axis home towards end stop B.
                type: String
        compatibility: MachineMotion v1 only.
        exampleCodePath: configAxisDirection.py
        """
        if self.isMMv2:
            raise Exception(
                "The function configAxisDirection is not supported on MachineMotion v2."
            )

        self._restrictAxisValue(axis)
        _restrictInputValue("direction", direction, DIRECTION)

        self.direction[axis] = direction
        # Verify that steps_mm exists
        if not _isNumber(self.steps_mm[axis]):
            self.populateStepsPerMm()

        if direction == DIRECTION.NORMAL:
            self.myGCode.__emitEchoOk__(
                "M92 "
                + self.myGCode.__getTrueAxis__(axis)
                + str(abs(self.steps_mm[axis]))
            )
            self.steps_mm[axis] = abs(self.steps_mm[axis])
        elif direction == DIRECTION.REVERSE:
            self.myGCode.__emitEchoOk__(
                "M92 "
                + self.myGCode.__getTrueAxis__(axis)
                + "-"
                + str(abs(self.steps_mm[axis]))
            )
            self.steps_mm[axis] = -abs(self.steps_mm[axis])

        return

    @staticmethod
    def _V2ParamsToActuatorConfigParams(
        drives,
        mechGain,
        directions,
        motorCurrent,
        loop,
        tuningProfile,
        _parent,
        _motorSize,
        _brake,
    ):
        configBody = ActuatorConfigParams(
            AXIS_TYPE.CUSTOM,
            _motorSize,
            _brake,
            tuningProfile,
            GEARBOX.NONE,
            motorCurrent,
            mechGain,
            loop,
        )
        parentIndex = drives.index(_parent)
        drivesWithDirection = [(drives[i], directions[i]) for i in range(len(drives))]
        # Place parent drive first
        drivesWithDirection[parentIndex], drivesWithDirection[0] = (
            drivesWithDirection[0],
            drivesWithDirection[parentIndex],
        )
        driveConfigParamList = [
            DriveConfigParams(d[0], d[1]) for d in drivesWithDirection
        ]
        return (configBody, driveConfigParamList)

    EXEC_ENGINE_PORT = 3100

    def configActuator(self, config, parentDrive, *childDrives):
        """
        desc: Configures motion parameters for a single or group of drives on a MachineMotion v2
        params:
            config:
                desc: The configuration to be applied to the drives
                type: Instance of the ActuatorConfigParams class
            parentDrive:
                desc: The configuration of the parent drive of the axis being configured
                type: Instance of the DriveConfigParams class
            *childDrives:
                desc: The configurations of the child drives in the axis being configured
                type: Instance or tuple of instances of the DriveConfigParam class (Maximum 3)
        note: exactly one drive in *drives must be the parent.
        compatibility: MachineMotion v2 only.
        exampleCodePath: configActuator.py
        """
        lMajor, lMinor, lPatch = self._getSoftwareVersion()
        if lMajor < 2 or lMinor < 6:
            raise Exception(
                "ERROR: configActuator is only supported on MachineMotion version 2.6.0 or higher. Please upgrade your MachineMotion software (currently %d.%d.%d)"
                % (lMajor, lMinor, lPatch)
            )
        maxAllowedChildDrives = 0 if self.isMMv2OneDrive else 3
        if len(childDrives) > maxAllowedChildDrives:
            raise Exception(
                "configActuator was passed "
                + str(len(childDrives) + 1)
                + " drives. The max allowed for this controller is"
                + maxAllowedChildDrives
                + "."
            )

        drives = [parentDrive] + list(childDrives)
        config.validate()
        for drive in drives:
            drive.validate()
        body = {"config": config.toJSON(), "drives": [d.toJSON() for d in drives]}
        execEngineHost = self.IP + ":" + str(self.EXEC_ENGINE_PORT)
        result = json.loads(
            HTTPSend(
                execEngineHost,
                "/v1/library/configure/axis",
                json.dumps(body),
                JsonRequest=True,
            )
        )
        patchedConfig = result["patchedConfig"]
        instructionParams = result["instructionParams"]
        for drive in drives:
            driveNum = drive.driveNumber
            self.direction[driveNum] = drive.direction
            self.mech_gain[driveNum] = patchedConfig["gain"]
            self.steps_mm[driveNum] = instructionParams["mmPerRotation"]
            if "microsteps" in instructionParams:
                self.u_step[driveNum] = instructionParams["microSteps"]
                continue
            self.u_step[driveNum] = MICRO_STEPS.ustep_16

    # ------------------------------------------------------------------------
    # Determines if the io-expander with the given id is available
    #
    # @param device - The io-expander device identifier
    # @return.      - True if the io-expander exists; False otherwise
    def isIoExpanderAvailable(self, device):
        return self.myIoExpanderAvailabilityState[device - 1]

    def detectIOModules(self):
        """
        desc: Returns a dictionary containing all detected IO Modules.
        note: For more information, please see the digital IO datasheet <a href="https://vention.io/docs/datasheets/digital-io-module-datasheet-52">here</a>
        returnValue: Dictionary with keys of format "Digital IO Network Id [id]" and values [id] where [id] is the network IDs of all connected digital IO modules.
        returnValueType: Dictionary
        compatibility: MachineMotion v1 and MachineMotion v2.
        exampleCodePath: digitalRead.py
        """
        foundIOModules = {}
        numIOModules = 0

        # Note : Delay is needed for MQTT callbacks to get triggered (in case detectIOModules is the first function called after instanciating the MachineMotion object)
        time.sleep(0.5)

        # IO module possible addresses are 1, 2, 3, 4, 5, 6, 8
        for ioDeviceID in range(1, self.maxIo + 1):
            if self.isIoExpanderAvailable(ioDeviceID):
                foundIOModules["Digital IO Network Id " + str(ioDeviceID)] = ioDeviceID
                numIOModules = numIOModules + 1

        if numIOModules == 0:
            eprint("No IO Modules found.")
        else:
            return foundIOModules

        return

    def digitalRead(self, deviceNetworkId, pin):
        """
        desc: Reads the state of a digital IO modules input pins.
        params:
            deviceNetworkId:
                desc: The IO Module's device network ID. Defined by its onboard dipswitch.
                type: Integer between 1 and 8
            pin:
                desc: The index of the input pin.
                type: Integer
        returnValue: Returns 1 if the input pin is logic HIGH (24V) and returns 0 if the input pin is logic LOW (0V).
        compatibility: MachineMotion v1 and MachineMotion v2.
        exampleCodePath: digitalRead.py
        """

        self.isIoExpanderInputIdValid(
            deviceNetworkId, pin
        )  # Enforce restrictions on IO-Expander ID and pin number
        if not hasattr(self, "digitalInputs"):
            self.digitalInputs = {}
        if not deviceNetworkId in self.digitalInputs:
            self.digitalInputs[deviceNetworkId] = {}
        if not pin in self.digitalInputs[deviceNetworkId]:
            self.digitalInputs[deviceNetworkId][pin] = 0
        return self.digitalInputs[deviceNetworkId][pin]

    def digitalWrite(self, deviceNetworkId, pin, value):
        """
        desc: Sets voltage on specified pin of digital IO output pin to either logic HIGH (24V) or LOW (0V).
        params:
            deviceNetworkId:
                desc: The IO Module's device network ID. Defined by its onboard dipswitch.
                type: Integer
            pin:
                desc: The output pin number to write to.
                type: Integer
            value:
                desc: Writing '1' or HIGH will set digial output to 24V, writing 0 will set digital output to 0V.
                type: Integer
        compatibility: MachineMotion v1 and MachineMotion v2.
        exampleCodePath: digitalWrite.py
        note: Output pins maximum sourcing current is 75 mA and the maximum sinking current is 100 mA. On older digital IO modules, the pin labels on the digital IO module (pin 1, pin 2, pin 3, pin 4) correspond in software to (0, 1, 2, 3). Therefore, digitalWrite(deviceNetworkId, 2, 1)  will set output pin 3 to 24V.
        """

        self.isIoExpanderOutputIdValid(
            deviceNetworkId, pin
        )  # Enforce restrictions on IO-Expander ID and pin number

        self.myMqttClient.publish(
            "devices/io-expander/"
            + str(deviceNetworkId)
            + "/digital-output/"
            + str(pin),
            "1" if value else "0",
            retain=True,
        )

        return

    def setPowerSwitch(self, deviceNetworkId, switchState):
        """
        desc: Sets a switch of a power switch module to ON (closed) or OFF (open).
        params:
            deviceNetworkId:
                desc: Power switch device network ID. Defined by its onboard dipswitch.
                type: Integer
            value:
                desc: Writing POWER_SWITCH.ON will set the switch to closed, writing POWER_SWITCH.OFF will set the switch to open.
                type: Boolean or String of the POWER_SWITCH class
        compatibility: MachineMotion v2.
        exampleCodePath: powerSwitch.py
        """
        if not self.isMMv2:
            raise Exception(
                "The function setPowerSwitch is only supported on MachineMotion v2."
            )

        self.isIoExpanderIdValid(deviceNetworkId)
        if isinstance(switchState, bool):  # accept boolean.
            switchState = POWER_SWITCH.ON if switchState else POWER_SWITCH.OFF
        else:
            _restrictInputValue("switchState", switchState, POWER_SWITCH)
        self.myMqttClient.publish(
            "devices/power-switch/" + str(deviceNetworkId) + "/digital-output/0",
            switchState,
            retain=True,
        )

        return

    def waitOnPushButton(
        self, deviceNetworkId, button, state=PUSH_BUTTON.STATE.PUSHED, timeout=None
    ):
        """
        desc: Wait until a push button has reached a desired state
        params:
            deviceNetworkId:
                desc: The Push-Button module's device network ID. Defined by its onboard dipswitch.
                type: Integer
            button:
                desc: The address of the button (PUSH_BUTTON.COLOR.BLACK or PUSH_BUTTON.COLOR.WHITE) you want to read
                      see PUSH_BUTTON class
                type: Integer of the PUSH_BUTTON.COLOR class

            state:
                desc: The state of the push button (PUSH_BUTTON.STATE.PUSHED or PUSH_BUTTON.STATE.RELEASED) necessary to proceed
                      see PUSH_BUTTON class
                type: String of the PUSH_BUTTON.STATE class
                default: By default, this function will wait until the desired push button is PUSH_BUTTON.STATE.PUSHED.
            timeout:
                desc: The maximum time (seconds) the function will wait until it returns.
                      If no timeout is passed, the function will wait indefinitely.
                type: Integer, Float or None
                default: None
        returnValue: `True` if push button has reached the desired state, `False` if the timeout has been reached.
        compatibility: MachineMotion v2.
        exampleCodePath: pushButton.py
        """
        if not self.isMMv2:
            raise Exception(
                "The function waitOnPushButton is only supported on MachineMotion v2."
            )
        self.isIoExpanderIdValid(deviceNetworkId)
        _restrictInputValue("button", button, PUSH_BUTTON.COLOR)
        _restrictInputValue("state", state, PUSH_BUTTON.STATE)

        deviceNetworkId = str(deviceNetworkId)
        button = str(button)
        if not hasattr(self, "pushButtonStates"):
            self.pushButtonStates = {}
        if not deviceNetworkId in self.pushButtonStates:
            self.pushButtonStates[deviceNetworkId] = {}
        if not button in self.pushButtonStates[deviceNetworkId]:
            self.pushButtonStates[deviceNetworkId][button] = "unknown"

        if not (
            isinstance(timeout, int) or isinstance(timeout, float) or timeout == None
        ):
            raise Exception("timeout must be of type float, int or None!")

        intervalSeconds = 0.1
        if timeout != None:
            elapsedSeconds = 0
            while (
                self.pushButtonStates[deviceNetworkId][button] != state
                and elapsedSeconds < timeout
            ):
                elapsedSeconds += intervalSeconds
                time.sleep(intervalSeconds)
            if elapsedSeconds > timeout:
                return False
        else:
            while self.pushButtonStates[deviceNetworkId][button] != state:
                time.sleep(intervalSeconds)
        return True

    def bindPushButtonEvent(self, deviceNetworkId, button, callback_function):
        """
        desc: Configures a user-defined function to execute immediately after a change of state of a push button module button
        params:
            deviceNetworkId:
                desc: The Push-Button module's device network ID. Defined by its onboard dipswitch.
                type: Integer
            button:
                desc: The address of the button (PUSH_BUTTON.COLOR.BLACK or PUSH_BUTTON.COLOR.WHITE) you want to read
                      see PUSH_BUTTON class
                type: Integer of the PUSH_BUTTON.COLOR class
            callback_function:
                desc: The function to be executed after a push button changes state.
                type: function
        note: The callback function used will be executed in a new thread.
        compatibility: MachineMotion v2.
        exampleCodePath: pushButton.py
        """
        if not self.isMMv2:
            raise Exception(
                "The function bindPushButtonEvent is only supported on MachineMotion v2."
            )
        self.isIoExpanderIdValid(deviceNetworkId)
        _restrictInputValue("button", button, PUSH_BUTTON.COLOR)
        if not callable(callback_function):
            raise Exception("callback_function must be of type function!")
        self.pushButtonCallbacks[str(deviceNetworkId)][str(button)] = callback_function
        return

    def readPushButton(self, deviceNetworkId, button):
        """
        desc: Reads the state of a Push-Button module button.
        params:
            deviceNetworkId:
                desc: The Push-Button module's device network ID. Defined by its onboard dipswitch.
                type: Integer of the PUSH_BUTTON.COLOR class
            button:
                desc: The address of the button (PUSH_BUTTON.COLOR.BLACK or PUSH_BUTTON.COLOR.WHITE) you want to read
                      see PUSH_BUTTON class
                type: Integer of the PUSH_BUTTON.COLOR class
        returnValue : Returns PUSH_BUTTON.STATE.RELEASED if the input button is released and returns PUSH_BUTTON.STATE.PUSHED if the input button pushed
        compatibility: MachineMotion v2.
        exampleCodePath: pushButton.py
        """
        if not self.isMMv2:
            raise Exception(
                "The function waitOnPushButton is only supported on MachineMotion v2."
            )

        self.isIoExpanderIdValid(deviceNetworkId)  # Enforce restrictions on Push-Button
        _restrictInputValue("button", button, PUSH_BUTTON.COLOR)
        deviceNetworkId = str(deviceNetworkId)
        button = str(button)
        if not hasattr(self, "pushButtonStates"):
            self.pushButtonStates = {}
        if not deviceNetworkId in self.pushButtonStates:
            self.pushButtonStates[deviceNetworkId] = {}
        if not button in self.pushButtonStates[deviceNetworkId]:
            self.pushButtonStates[deviceNetworkId][button] = "unknown"
        return self.pushButtonStates[deviceNetworkId][button]

    def readEncoder(self, encoder, readingType=ENCODER_TYPE.real_time):
        """
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
        compatibility: MachineMotion v1 only.
        exampleCodePath: readEncoder.py
        note: The encoder position returned by this function may be delayed by up to 250 ms due to internal propogation delays.
        """
        if self.isMMv2:
            raise Exception(
                "The function readEncoder is not supported on MachineMotion v2."
            )

        _restrictInputValue("readingType", readingType, ENCODER_TYPE)
        self.isEncoderIdValid(encoder)  # Enforce restrictions on encoder ID

        if readingType == ENCODER_TYPE.real_time:
            return self.myEncoderRealtimePositions[encoder]
        elif readingType == ENCODER_TYPE.stable:
            return self.myEncoderStablePositions[encoder]

        return

    # ------------------------------------------------------------------------
    # Reacts to an eStop event
    #
    # @param {bool} status - true or false
    # @return : call to callback function

    def eStopEvent(self, status):
        self.eStopCallback(status)
        return

    def triggerEstopWithMsg(self, msg="python-api"):
        # This function allows you to trigger an estop and send a custom message  to the service
        # The message should be a string, which will then be logged by the eStop service to
        # allow for easier error handling

        # Creating return value for the function. If nothing good happens, it will return False
        q = []  # List is used to pass share variables with a thread
        q.append(False)

        def mqttResponse(q):
            # Wait for response
            return_value = q.pop()
            return_value = self.__parseMessage(
                MQTTsubscribe.simple(
                    MQTT.PATH.ESTOP_TRIGGER_RESPONSE, retained=False, hostname=self.IP
                ).payload
            )
            q.append(return_value)
            return

        mqttResponseThread = threading.Thread(target=mqttResponse, args=(q,))
        mqttResponseThread.daemon = True
        mqttResponseThread.start()

        # Adding a delay to make sure MQTT simple function is launched before publish is made. Quick fix from bug on App. Launcher.
        time.sleep(0.2)

        # Publish trigger request on MQTT
        self.myMqttClient.publish(
            MQTT.PATH.ESTOP_TRIGGER_REQUEST, msg
        )  # we pass a message to the eStop service, for debugging

        mqttResponseThread.join(MQTT.TIMEOUT)

        if mqttResponseThread.is_alive():
            raise Exception(
                "eStop is still not triggered after " + str(MQTT.TIMEOUT) + " seconds"
            )
        else:
            return q.pop()

    def triggerEstop(self):
        # """
        # desc: Triggers the MachineMotion software emergency stop, cutting power to all drives and enabling brakes (if any). The software E stop must be released (using releaseEstop()) in order to re-enable the machine.
        # returnValue: The success of the operation.
        # returnValueType: Boolean
        # compatibility: MachineMotion v1 and MachineMotion v2.
        # exampleCodePath: eStop.py
        # """
        return self.triggerEstopWithMsg()

    def releaseEstop(self):
        # """
        # desc: Releases the software E-stop and provides power back to the drives.
        # returnValue: The success of the operation.
        # returnValueType: Boolean
        # compatibility: MachineMotion v1 and MachineMotion v2.
        # exampleCodePath: eStop.py
        # """
        # Creating return value for the function. If nothing good happens, it will return False
        q = []  # List is used to pass share variables with a thread
        q.append(False)

        def mqttResponse(q):
            # Wait for response
            return_value = q.pop()
            return_value = self.__parseMessage(
                MQTTsubscribe.simple(
                    MQTT.PATH.ESTOP_RELEASE_RESPONSE, retained=False, hostname=self.IP
                ).payload
            )
            q.append(return_value)
            return

        mqttResponseThread = threading.Thread(target=mqttResponse, args=(q,))
        mqttResponseThread.daemon = True
        mqttResponseThread.start()

        # Adding a delay to make sure MQTT simple function is launched before publish is made. Quick fix from bug on App. Launcher.
        time.sleep(0.2)

        # Publish release request on MQTT
        self.myMqttClient.publish(
            MQTT.PATH.ESTOP_RELEASE_REQUEST, ""
        )  # payload message is not important

        mqttResponseThread.join(MQTT.TIMEOUT)

        if mqttResponseThread.is_alive():
            raise Exception(
                "eStop is still not released after " + str(MQTT.TIMEOUT) + " seconds"
            )
        else:
            return q.pop()

    def resetSystem(self):
        # """
        # desc: Resets the system after an eStop event
        # returnValue: The success of the operation.
        # returnValueType: Boolean
        # compatibility: MachineMotion v1 and MachineMotion v2.
        # exampleCodePath: eStop.py
        # """
        # Creating return value for the function. If nothing good happens, it will return False
        q = []  # List is used to pass share variables with a thread
        q.append(False)

        def mqttResponse(q, should_kill_thread_function):
            # Wait for response
            return_value = q.pop()
            return_value = self.__parseMessage(
                MQTTsubscribe.simple(
                    MQTT.PATH.ESTOP_SYSTEMRESET_RESPONSE,
                    retained=False,
                    hostname=self.IP,
                ).payload
            )
            if self.isMMv2 and return_value:
                # If the resetSystem was successful, we need to wait for the drives to be energized on MMv2 (takes approximately 3sec)
                while not self.areSmartDrivesReady:
                    if should_kill_thread_function():
                        return
                    time.sleep(0.1)
            q.append(return_value)
            return

        should_kill_thread = False
        mqttResponseThread = threading.Thread(
            target=mqttResponse, args=(q, lambda: should_kill_thread)
        )
        mqttResponseThread.daemon = True
        mqttResponseThread.start()

        # Adding a delay to make sure MQTT simple function is launched before publish is made. Quick fix from bug on App. Launcher.
        time.sleep(0.2)

        # Publish reset system request on MQTT
        self.myMqttClient.publish(
            MQTT.PATH.ESTOP_SYSTEMRESET_REQUEST, ""
        )  # payload message is not important

        mqttResponseThread.join(MQTT.TIMEOUT)

        if mqttResponseThread.is_alive():
            should_kill_thread = True  # Kill the thread waiting on MQTT topic
            raise Exception(
                "System is still not ready after " + str(MQTT.TIMEOUT) + " seconds"
            )
        else:
            return q.pop()

    def bindeStopEvent(self, callback_function):
        """
        desc: Configures a user defined function to execute immediately after an E-stop event.
        params:
            callback_function:
                type: function
                desc: The function to be executed after an e-stop is triggered or released.
        compatibility: MachineMotion v1 and MachineMotion v2.
        exampleCodePath: eStop.py
        """
        self.eStopCallback = callback_function
        self.eStopCallback(self.estopStatus)
        return

    def lockBrake(self, aux_port_number, safety_adapter_presence=False):
        """
        desc: Lock the brake, by shutting off the power of the designated AUX port of the MachineMotion (0V).
        params:
            aux_port_number:
                type: Integer
                desc: The number of the AUX port the brake is connected to.
            safety_adapter_presence:
                type: Boolean
                desc: Is a yellow safety adapter plugged in between the brake cable and the AUX port.
        compatibility: MachineMotion v1 and MachineMotion v2.
        exampleCodePath: controlBrakes.py
        note: This function is compatible only with V1F and more recent MachineMotions.
        """
        self._restrictBrakePort(aux_port_number)

        # The safety_adapter_presence flag and specifically its default value are incompatible with MM v2. It must always be set to true.
        if self.isMMv2 and safety_adapter_presence == False:
            raise Exception(
                "The 'safety_adapter_presence' flag must be set to True for MachineMotion v2."
            )

        topic = (
            MQTT.PATH.AUX_PORT_SAFETY
            if safety_adapter_presence
            else MQTT.PATH.AUX_PORT_POWER
        )
        self.myMqttClient.publish(topic + "/" + str(aux_port_number) + "/request", "0V")

        return

    def unlockBrake(self, aux_port_number, safety_adapter_presence=False):
        """
        desc: Unlock the brake, by powering on the designated AUX port of the MachineMotion (24V).
        params:
            aux_port_number:
                type: Integer
                desc: The number of the AUX port the brake is connected to.
            safety_adapter_presence:
                type: Boolean
                desc: Is a yellow safety adapter plugged in between the brake cable and the AUX port.
        compatibility: MachineMotion v1 and MachineMotion v2.
        exampleCodePath: controlBrakes.py
        note: This function is compatible only with V1F and more recent MachineMotions.
        """
        self._restrictBrakePort(aux_port_number)

        # The safety_adapter_presence flag and specifically its default value are incompatible with MM v2. It must always be set to true.
        if self.isMMv2 and safety_adapter_presence == False:
            raise Exception(
                "The 'safety_adapter_presence' flag must be set to True for MachineMotion v2."
            )

        topic = (
            MQTT.PATH.AUX_PORT_SAFETY
            if safety_adapter_presence
            else MQTT.PATH.AUX_PORT_POWER
        )
        self.myMqttClient.publish(
            topic + "/" + str(aux_port_number) + "/request", "24V"
        )

        return

    def getBrakeState(self, aux_port_number, safety_adapter_presence=False):
        """
        desc: Read the current state of the brake connected to a given AUX port of the MachineMotion.
        params:
            aux_port_number:
                type: Integer
                desc: The number of the AUX port the brake is connected to.
            safety_adapter_presence:
                type: Boolean
                desc: Is a yellow safety adapter plugged in between the brake cable and the AUX port.
        returnValue: The current state of the brake, as determined according to the current voltage of the AUX port (0V or 24V). The returned String can be "locked", "unlocked", or "unknown" (for MachineMotions prior to the V1F hardware version), as defined by the BRAKE_STATES class.
        returnValueType: String
        compatibility: MachineMotion v1 and MachineMotion v2.
        exampleCodePath: controlBrakes.py
        note: This function is compatible only with V1F and more recent MachineMotions.
        """
        self._restrictBrakePort(aux_port_number)

        # The safety_adapter_presence flag and specifically its default value are incompatible with MM v2. It must always be set to true.
        if self.isMMv2 and safety_adapter_presence == False:
            raise Exception(
                "The 'safety_adapter_presence' flag must be set to True for MachineMotion v2."
            )

        voltage = (
            self.brakeStatus_safety[aux_port_number - 1]
            if safety_adapter_presence
            else self.brakeStatus_control[aux_port_number - 1]
        )

        if voltage == "0V":
            return BRAKE_STATES.locked
        elif voltage == "24V":
            return BRAKE_STATES.unlocked
        else:
            return BRAKE_STATES.unknown

    def startPath(self, path, maxAcceleration, speedOverride=1.0, rapidSpeed=None):
        """
        desc: Loads and starts a G-Code path. Path mode must first be configured (see configPathMode).
        params:
            path:
                desc: G-Code string
                type: string
            maxAcceleration:
                desc: Defines the maximum system acceleration on the path.
                type: number
            speedOverride:
                desc: Optional.Allows for slowing down or speeding up a G-Code path. When parsed, the path speed will be multiplied by this value.
                type: positive number
                default: 1.0
            rapidSpeed:
                desc: Optional. Allows to manually set the rapid speed in mm/s for G0 commands. If none, rapid speed will default to the lowest axis max speed.
                type: positive number
                default: None
        compatibility: MachineMotion v2.
        exampleCodePath: pathFollowing.py
        """
        if not _isNumber(maxAcceleration) or maxAcceleration <= 0:
            raise Exception(
                "maxAcceleration must be a positive number, received: {}".format(
                    maxAcceleration
                )
            )
        if not _isNumber(speedOverride) or speedOverride <= 0:
            raise Exception(
                "speedOverride must be a positive number, received: {}".format(
                    speedOverride
                )
            )
        if rapidSpeed != None:
            if not _isNumber(rapidSpeed) or rapidSpeed <= 0:
                raise Exception(
                    "rapidSpeed must be a positive number, received: {}".format(
                        rapidSpeed
                    )
                )

        # start path is broken into two requests.
        # 1. loadPath (a potentially long call that parses the gcode text)
        # 2. startPath
        # this allows time backed up requests accrued during parsing to be handled.
        # and prevent jitter at the start of the path due to CPU overload.
        response = self.myGCode.__sendToSmartDrives__(
            "/smartDrives/path",
            json.dumps(
                {
                    "path": path,
                    "acceleration": maxAcceleration,
                    "speedOverride": speedOverride,
                    "rapidSpeed": rapidSpeed,
                }
            ),
            True,
            True,
        )
        return response
        # time.sleep(1)
        # response2 = self.myGCode.__sendToSmartDrives__(
        #     "/smartDrives/path/start", JsonRequest=False, JsonResponse=False
        # )

    def configPathMode(self, axisMap, *tools):
        """
        desc: Each G-Code Path controls axes (e.g. X,Y,Z). Some paths control tools (via T, M3,4,5,6 commands).
            configPathMode Configures relevant axes and digital outputs for path following.
        params:
            axisMap:
                desc: A mapping between each G-Code axis and it associated parent drive, e.g. {"X": 1, "Y": 2, "Z": 3}.
                type: Dict of axis string keys (AXIS_NAME class) and integer drive numbers (AXIS_NUMBER class)
            *tools:
                desc: Tuple of all the tools that will be used in the G-Code path.
                type: tool or tuple of tools of the TOOL class
        compatibility: MachineMotion v2
        exampleCodePath: pathFollowing.py
        """
        usedAxes = []
        usedDrives = []
        for axis in axisMap:
            drive = axisMap[axis]
            if axis in usedAxes:
                raise Exception("Duplicate use of {}".format(axis))
            if drive in usedDrives:
                raise Exception("Duplicate use of {}".format(drive))
            _restrictInputValue("axis", axis, AXIS_NAME)
            _restrictInputValue("drive", axisMap[axis], AXIS_NUMBER)
            usedAxes.append(axis)
            usedDrives.append(drive)

        for tool in tools:
            if not isinstance(tool, TOOL):
                raise Exception(
                    "tool arguments must be of type TOOL. received: {}".format(tool)
                )
            lTool = tool.toJSON()
            lNumber = list(lTool.keys())[0]
            lData = json.dumps(lTool[lNumber])
            response = self.myGCode.__sendToSmartDrives__(
                "/smartDrives/path/tool/{}".format(lNumber), lData, True, True
            )

        response = self.myGCode.__sendToSmartDrives__(
            "/smartDrives/path/axisMap",
            json.dumps(axisMap),
            True,
            True,
        )

    def getPathStatus(self):
        """
        desc: Get the live status of the path following procedue.
        returnValue: object
                        "running": boolean
                        "line": number,
                        "command": string,
                        "speed": number,
                        "acceleration": number,
                        "tool": object,
                        "error": string,
        returnValueType: object
        compatibility: MachineMotion v2
        exampleCodePath: pathFollowing.py
        """
        lResponse = self.myGCode.__sendToSmartDrives__(
            "/smartDrives/path/status", JsonResponse=True
        )
        return json.loads(lResponse)

    def stopPath(self):
        """
        desc: Abruptly stop the path following procedure.
        compatibility: MachineMotion v2.
        exampleCodePath: pathFollowing.py
        """
        self.myGCode.__sendToSmartDrives__("/smartDrives/path/stop")

    # ------------------------------------------------------------------------
    # Register to the MQTT broker on each connection.
    #
    # @param client   - The MQTT client identifier (us)
    # @param userData - The user data we have supply on registration (none)
    # @param flags    - Connection flags
    # @param rc       - The connection return code
    def __onConnect(self, client, userData, flags, rc):
        if rc == 0:
            self.myMqttClient.subscribe("devices/+/+/available")
            self.myMqttClient.subscribe("devices/+/+/digital-input/#")
            self.myMqttClient.subscribe("devices/encoder/+/realtime-position")
            self.myMqttClient.subscribe("devices/encoder/+/stable-position")
            self.myMqttClient.subscribe(MQTT.PATH.ESTOP_STATUS)
            self.myMqttClient.subscribe(MQTT.PATH.AUX_PORT_SAFETY + "/+/status")
            self.myMqttClient.subscribe(MQTT.PATH.AUX_PORT_POWER + "/+/status")
            self.myMqttClient.subscribe(MQTT.PATH.SMARTDRIVES_READY)

        return

    def onDigitalInput(self, callback):
        """hidden
        desc: Set a callback function that is called when digital input updates are received. For internal use.
        params:
            callback:
                desc: Function called when input value is updated.
                type: Callable[deviceType, deviceNetworkId, pin, value] -> None
        returnValue: None
        compatibility: MachineMotion v1 and MachineMotion v2.
        """
        self._userDigitalInputCallback = callback
        return

    def _callUserDigitalInputCallback(self, deviceType, deviceNetworkId, pin, value):
        if self._userDigitalInputCallback is None:
            return
        try:
            self._userDigitalInputCallback(deviceType, deviceNetworkId, pin, value)
        except Exception as e:
            stderr(e)

    # ------------------------------------------------------------------------
    # Update our internal state from the messages received from the MQTT broker
    #
    # @param client   - The MQTT client identifier (us)
    # @param userData - The user data we have supply on registration (none)
    # @param msg      - The MQTT message recieved
    def __onMessage(self, client, userData, msg):
        # try/except to make _onMessage robust to garbage MQTT messages
        try:
            topicParts = msg.topic.split("/")
            if topicParts[0] == "devices":
                device = int(topicParts[2])
                device_str = topicParts[2]
                deviceType = topicParts[1]
                if deviceType == "push-button":
                    self.isIoExpanderIdValid(device)
                    if topicParts[3] == "digital-input":
                        button = int(topicParts[4])
                        button_str = topicParts[4]
                        self.isPushButtonInputIdValid(device, button)
                        state = self.__parseMessage(msg.payload, jsonLoads=False)
                        _restrictInputValue("state", state, PUSH_BUTTON.STATE)

                        if not hasattr(self, "pushButtonStates"):
                            self.pushButtonStates = {}
                        if not device_str in self.pushButtonStates:
                            self.pushButtonStates[device_str] = {}
                        if not button_str in self.pushButtonStates[device_str]:
                            self.pushButtonStates[device_str][button_str] = {}
                        self.pushButtonStates[device_str][button_str] = state
                        self._callUserDigitalInputCallback(
                            "push-button", device, button, state
                        )
                        # to free up Mqtt, call the resulting fn in a new thread
                        cbThread = threading.Thread(
                            target=self.pushButtonCallbacks[device_str][button_str],
                            args=[state],
                        )
                        cbThread.start()
                    return

                if deviceType == "io-expander":
                    self.isIoExpanderIdValid(device)
                    if topicParts[3] == "available":
                        availability = self.__parseMessage(msg.payload)
                        if availability:
                            self.myIoExpanderAvailabilityState[device - 1] = True
                            return
                        else:
                            self.myIoExpanderAvailabilityState[device - 1] = False
                            return
                    pin = int(topicParts[4])
                    self.isIoExpanderInputIdValid(
                        device, pin
                    )  # Enforce restrictions on IO-Expander ID and pin number
                    value = int(self.__parseMessage(msg.payload))

                    if not hasattr(self, "digitalInputs"):
                        self.digitalInputs = {}
                    if not device in self.digitalInputs:
                        self.digitalInputs[device] = {}
                    self.digitalInputs[device][pin] = value
                    self._callUserDigitalInputCallback(
                        "io-expander", device, pin, value
                    )
                    return

                elif deviceType == "encoder":
                    device = int(topicParts[2])
                    position_type = topicParts[3]
                    position = float(self.__parseMessage(msg.payload))
                    if position_type == ENCODER_TYPE.real_time:
                        self.myEncoderRealtimePositions[device] = position
                    elif position_type == ENCODER_TYPE.stable:
                        self.myEncoderStablePositions[device] = position
                    return

            elif topicParts[0] == MQTT.PATH.ESTOP:
                if topicParts[1] == "status":
                    self.estopStatus = self.__parseMessage(msg.payload)
                    self.eStopEvent(self.estopStatus)
                return

            elif topicParts[0] == MQTT.PATH.AUX_PORT_POWER:
                if topicParts[2] == "status":
                    aux_port = int(topicParts[1])
                    self.brakeStatus_control[aux_port - 1] = self.__parseMessage(
                        msg.payload, jsonLoads=False
                    )

            elif topicParts[0] == MQTT.PATH.AUX_PORT_SAFETY:
                if topicParts[2] == "status":
                    aux_port = int(topicParts[1])
                    self.brakeStatus_safety[aux_port - 1] = self.__parseMessage(
                        msg.payload, jsonLoads=False
                    )

            elif msg.topic == MQTT.PATH.SMARTDRIVES_READY:
                self.areSmartDrivesReady = self.__parseMessage(msg.payload)

        except Exception as e:
            stderr(e)

        return

    def __onDisconnect(self, client, userData, rc):
        # eprint("Disconnected with rtn code [%d]"% (rc))
        return

    ########################
    ######## LEGACY ########
    ########################

    # All the functions below are left only for legacy and backwards compatibility purposes.
    # Vention does not advise to use any of them.

    def configAxis_v2(
        self,
        drives,
        mechGain,
        directions,
        motorCurrent,
        loop,
        microSteps,
        tuningProfile,
        _parent=None,
        _motorSize=MOTOR_SIZE.LARGE,
        _brake=BRAKE.NONE,
    ):
        if motorCurrent > MAX_MOTOR_CURRENT:
            eprint(
                "Motor current value was clipped to the maximum ("
                + str(MAX_MOTOR_CURRENT)
                + "A)."
            )
            motorCurrent = MAX_MOTOR_CURRENT
        elif motorCurrent < MIN_MOTOR_CURRENT:
            eprint(
                "Motor current value was clipped to the minimum ("
                + str(MIN_MOTOR_CURRENT)
                + "A)."
            )
            motorCurrent = MIN_MOTOR_CURRENT
        _restrictInputValue("control loop type", loop, CONTROL_LOOPS)
        _restrictInputValue("microSteps", microSteps, MICRO_STEPS)
        _restrictInputValue("tuning profile", tuningProfile, TUNING_PROFILES)
        _restrictInputValue("motor Size", _motorSize, MOTOR_SIZE)
        _restrictInputValue("brake presence", _brake, BRAKE)

        # Cap the current if electric cylinder:
        if (
            _motorSize == MOTOR_SIZE.ELECTRIC_CYLINDER
            and motorCurrent > ELECTRIC_CYLINDER_MAX_MOTOR_CURRENT
        ):
            raise Exception(
                "Current for Actuator type "
                + MOTOR_SIZE.ELECTRIC_CYLINDER
                + " cannot be greater than "
                + str(ELECTRIC_CYLINDER_MAX_MOTOR_CURRENT)
                + " A!"
            )

        if _parent != None:
            _restrictInputValue("parentDrive", _parent, AXIS_NUMBER)

        if mechGain <= 0:
            raise Exception("Mechanical gain should be a positive value.")

        if isinstance(drives, list) != isinstance(directions, list):
            raise Exception("Drives and directions must be of the same type.")

        if not isinstance(drives, list):
            drives = [drives]
            if _parent is None:
                _parent = drives[0]
            directions = [directions]
        if _parent not in drives:
            raise Exception("parent drive is not in drives list")

        if len(drives) > len(self.brakeStatus_control):
            raise Exception(
                "Number of Drives can not exceed {}".format(
                    len(self.brakeStatus_control)
                )
            )

        if len(drives) != len(directions):
            raise Exception("drives and directions are not the same length.")

        (configParams, driveParams) = self._V2ParamsToActuatorConfigParams(
            drives,
            mechGain,
            directions,
            motorCurrent,
            loop,
            tuningProfile,
            _parent,
            _motorSize,
            _brake,
        )
        return self.configActuator(configParams, *driveParams)

    def configStepper(
        self,
        drive,
        mechGain,
        direction,
        motorCurrent,
        microSteps=MICRO_STEPS.ustep_8,
        motorSize=MOTOR_SIZE.LARGE,
    ):
        """hidden
        desc: Configures motion parameters as a stepper motor, for a single drive on the MachineMotion v2.
        params:
            drive:
                desc: The drive to configure.
                type: Number of the AXIS_NUMBER class
            mechGain:
                desc: The distance moved by the actuator for every full rotation of the stepper motor, in mm/revolution.
                type: Number of the MECH_GAIN class
            direction:
                desc: The direction of the axis
                type: String of the DIRECTION class
            motorCurrent:
                desc: The current to power the motor with, in Amps.
                type: Number
            microSteps:
                desc: The microstep setting of the drive.
                type: Number from MICRO_STEPS class
            motorSize:
                desc: The size of the motor(s) connected to the specified drive(s)
                type: String from the MOTOR_SIZE class
                default: MOTOR_SIZE.LARGE
        note: Warning, changing the configuration can de-energize motors and thus cause unintended behaviour on vertical axes.
        compatibility: MachineMotion v2 only.
        exampleCodePath: configStepperServo.py
        """
        if not self.isMMv2:
            raise Exception(
                "The function configStepper is not supported on MachineMotion v1."
            )

        if isinstance(drive, list):
            raise Exception("The drive should be a Number and not a List")
        loop = CONTROL_LOOPS.OPEN_LOOP
        tuningProfile = TUNING_PROFILES.DEFAULT
        self.configAxis_v2(
            drive,
            mechGain,
            direction,
            motorCurrent,
            loop,
            microSteps,
            tuningProfile,
            _motorSize=motorSize,
        )

    def configServo(
        self,
        drives,
        mechGain,
        directions,
        motorCurrent,
        tuningProfile=TUNING_PROFILES.DEFAULT,
        parentDrive=None,
        motorSize=MOTOR_SIZE.LARGE,
        brake=BRAKE.NONE,
    ):
        """hidden
        desc: Configures motion parameters as a servo motor, for a single drive on the MachineMotion v2.
        params:
            drives:
                desc: The drive or list of drives to configure.
                type: Number or list of numbers of the AXIS_NUMBER class
            mechGain:
                desc: The distance moved by the actuator for every full rotation of the stepper motor, in mm/revolution.
                type: Number of the MECH_GAIN class
            directions:
                desc: The direction or list of directions of each configured axis
                type: String or list of strings of the DIRECTION class. Must have the same length as `drives`
            motorCurrent:
                desc: The current to power the motor with, in Amps.
                type: Number
            tuningProfile:
                desc: The tuning profile of the smartDrive. Determines the characteristics of the servo motor's PID controller
                type: String of the TUNING_PROFILES class
                default: TUNING_PROFILES.DEFAULT
            parentDrive:
                desc: The parent drive of the multi-drive axis. The axis' home and end sensors must be connected to this drive.
                type: Number
                default: None
            motorSize:
                desc: The size of the motor(s) connected to the specified drive(s)
                type: String from the MOTOR_SIZE class
                default: MOTOR_SIZE.LARGE
            brake:
                desc: The presence of a brake on the desired axis.
                    If set to BRAKE.PRESENT, moving the axis while the brake is locked will generate an error.
                    If set to BRAKE.NONE, motion will be allowed regardless of internal brake control.
                type: String of the BRAKE class
                default: BRAKE.NONE
        note: Warning, changing the configuration can de-energize motors and thus cause unintended behaviour on vertical axes.
        compatibility: MachineMotion v2 only.
        exampleCodePath: configStepperServo.py, configMultiDriveServo.py
        """
        if not self.isMMv2:
            raise Exception(
                "The function configServo is not supported on MachineMotion v1."
            )

        loop = CONTROL_LOOPS.CLOSED_LOOP
        # Set the microsteps based on the desired gain. this will allow for higher speeds
        if 0.0 <= mechGain < 75.0:
            microSteps = MICRO_STEPS.ustep_full
        elif 75.0 <= mechGain < 150.7:
            microSteps = MICRO_STEPS.ustep_2
        elif 150.7 <= mechGain:
            microSteps = MICRO_STEPS.ustep_4
        else:
            raise Exception("Mechanical gain should be a positive value.")
        self.configAxis_v2(
            drives,
            mechGain,
            directions,
            motorCurrent,
            loop,
            microSteps,
            tuningProfile,
            _parent=parentDrive,
            _motorSize=motorSize,
            _brake=brake,
        )

    def setSpeed(self, speed, units=UNITS_SPEED.mm_per_sec):
        """hidden
        desc: Sets the global speed for all movement commands on all axes.
        params:
            speed:
                desc: The global max speed in mm/s, or mm/min according to the units parameter.
                type: Number
            units:
                desc: Units for speed. Can be switched to UNITS_SPEED.mm_per_min
                defaultValue: UNITS_SPEED.mm_per_sec
                type: String
        compatibility: MachineMotion v1 and MachineMotion v2.
        """

        _restrictInputValue("units", units, UNITS_SPEED)

        if units == UNITS_SPEED.mm_per_min:
            speed_mm_per_min = speed
        elif units == UNITS_SPEED.mm_per_sec:
            speed_mm_per_min = 60 * speed

        self.myGCode.__emitEchoOk__("G0 F" + str(speed_mm_per_min))

        return

    def setAcceleration(self, acceleration, units=UNITS_ACCEL.mm_per_sec_sqr):
        """hidden
        desc: Sets the global acceleration for all movement commands on all axes.
        params:
            mm_per_sec_sqr:
                desc: The global acceleration in mm/s^2.
                type: Number
            units:
                desc: Units for speed. Can be switched to UNITS_ACCEL.mm_per_min_sqr
                defaultValue: UNITS_ACCEL.mm_per_sec_sqr
                type: String
        compatibility: MachineMotion v1 and MachineMotion v2.
        """

        _restrictInputValue("units", units, UNITS_ACCEL)

        if units == UNITS_ACCEL.mm_per_sec_sqr:
            accel_mm_per_sec_sqr = acceleration
        elif units == UNITS_ACCEL.mm_per_min_sqr:
            accel_mm_per_sec_sqr = acceleration / 3600

        # Note : Set travel and print acceleration, to impact G0 and G1 commands.
        self.myGCode.__emitEchoOk__(
            "M204 T" + str(accel_mm_per_sec_sqr) + " P" + str(accel_mm_per_sec_sqr)
        )

        return

    def isReady(self):
        return True
        # return self.myGCode.__isReady__()

    def emitStop(self):
        return self.stopAllMotion()

    def emitHomeAll(self):
        if not self.isMMv2:
            allDrives = 3
        elif self.isMMv2OneDrive:
            allDrives = 1
        else:
            allDrives = 4
        for drive in range(1, allDrives + 1):
            retVal = self.moveToHome(drive)
            self.waitForMotionCompletion()
        return retVal

    def emitHome(self, axis):
        retVal = self.moveToHome(axis)
        self.waitForMotionCompletion()
        return retVal

    def emitSpeed(self, speed, units=UNITS_SPEED.mm_per_sec):
        self.setSpeed(speed, units)

    def emitAcceleration(self, acceleration, units=UNITS_ACCEL.mm_per_sec_sqr):
        self.setAcceleration(acceleration, units)

    def emitAbsoluteMove(self, axis, position):
        self.moveToPosition(axis, position)

    def emitCombinedAxesAbsoluteMove(self, axes, positions):
        self.moveToPositionCombined(axes, positions)

    def emitRelativeMove(self, axis, direction, distance):
        _restrictInputValue("direction", direction, DIRECTION)

        if direction == DIRECTION.NEGATIVE:
            distance = -float(distance)
        self.moveRelative(axis, distance)

    def emitCombinedAxesRelativeMove(self, axes, directions, distances):
        if (
            not isinstance(axes, list)
            or not isinstance(directions, list)
            or not isinstance(distances, list)
        ):
            raise TypeError("Axes, Directions and Distances must be lists")

        # Transmit move command
        tempDistances = [
            -x if direction == DIRECTION.NEGATIVE else x
            for direction, x in zip(directions, distances)
        ]

        self.moveRelativeCombined(axes, tempDistances)

    def emitCombinedAxisRelativeMove(self, axes, directions, distances):
        self.emitCombinedAxesRelativeMove(axes, directions, distances)

    def setContinuousMove(self, axis, speed, accel=100):
        self.moveContinuous(axis, speed, accel)

    def stopContinuousMove(self, axis, accel=100):
        self.stopMoveContinuous(axis, accel)

    def configMachineMotionIp(
        self, mode=None, machineIp=None, machineNetmask=None, machineGateway=None
    ):
        # Note : This function has been deprecated. Please use the ControlCenter to configure the networking.
        # '''
        # desc: Set up the required network information for the Machine Motion controller. The router can be configured in either DHCP mode or static mode.
        # params:
        #     mode:
        #         desc: Sets Network Mode to either DHCP or static addressing. Either <code>NETWORK_MODE.static</code> or <code>NETWORK_MODE.dhcp</code>
        #         type: Constant
        #     machineIp:
        #         desc: The static IP Address given to the controller. (Required if mode = <code>NETWORK_MODE.static</code>)
        #         type: String
        #     machineNetmask:
        #         desc: The netmask IP Address given to the controller. (Required if mode = <code>NETWORK_MODE.static</code>)
        #         type: String
        #     machineGateway:
        #         desc: The gateway IP Address given to the controller. (Required if mode = <code>NETWORK_MODE.static</code>)
        #         type: String
        # Note: All Strings expect the format "XXX.XXX.XXX.XXX". To connect the controller to the internet, the gateway IP should be the same IP as your LAN router.
        # exampleCodePath: configMachineMotionIp.py
        # '''

        if mode == NETWORK_MODE.static:
            if (
                (machineIp is None)
                or (machineNetmask is None)
                or (machineGateway is None)
            ):
                stderr(
                    "NETWORK ERROR: machineIp, machineNetmask and machineGateway cannot be left blank in static mode"
                )

                return False

        # Create a new object and augment it with the key value.

        if mode is not None:
            self.myConfiguration["mode"] = mode
        if machineIp is not None:
            self.myConfiguration["machineIp"] = machineIp
        if machineNetmask is not None:
            self.myConfiguration["machineNetmask"] = machineNetmask
        if machineGateway is not None:
            self.myConfiguration["machineGateway"] = machineGateway

        HTTPSend(self.IP + ":8000", "/configIp", json.dumps(self.myConfiguration))

        time.sleep(1)

        return

    def configMinMaxHomingSpeed(
        self, axes, minspeeds, maxspeeds, units=UNITS_SPEED.mm_per_sec
    ):
        # Note : This function has been deprecated.
        # '''
        # desc: Sets the minimum and maximum homing speeds for each axis.
        # params:
        #     axes:
        #         desc: a list of the axes that require minimum and maximum homing speeds.
        #         type: List
        #     minspeeds:
        #         desc: the minimum speeds for each axis.
        #         type: List
        #     maxspeeds:
        #         desc: the maximum speeds for each axis, in the same order as the axes parameter
        #         type: List
        # exampleCodePath: configHomingSpeed.py
        # note: This function can be used to set safe limits on homing speed. Because homing speed is configured only through software aPI, this safeguards against developers accidently modifying homing speed to unsafe levels.
        # '''
        try:
            axes = list(axes)
            minspeeds = list(minspeeds)
            maxspeeds = list(maxspeeds)
        except TypeError:
            axes = [axes]
            minspeeds = [minspeeds]
            maxspeeds = [maxspeeds]

        if len(axes) != len(minspeeds) or len(axes) != len(maxspeeds):

            class InputsError(Exception):
                pass

            raise InputsError("axes and speeds must be of same length")

        for axis in axes:
            _restrictInputValue("axis", axis, AXIS_NUMBER)

        gCodeCommand = "V1"
        for idx, axis in enumerate(axes):
            if units == UNITS_SPEED.mm_per_sec:
                min_speed_mm_per_min = minspeeds[idx] * 60
                max_speed_mm_per_min = maxspeeds[idx] * 60
            elif units == UNITS_SPEED.mm_per_min:
                min_speed_mm_per_min = minspeeds[idx]
                max_speed_mm_per_min = maxspeeds[idx]

            if min_speed_mm_per_min < HARDWARE_MIN_HOMING_FEEDRATE:
                raise Exception(
                    "Your desired homing speed of "
                    + str(min_speed_mm_per_min)
                    + "mm/min can not be less than "
                    + str(HARDWARE_MIN_HOMING_FEEDRATE)
                    + "mm/min ("
                    + str(HARDWARE_MIN_HOMING_FEEDRATE / 60)
                    + "mm/s)."
                )
            if max_speed_mm_per_min > HARDWARE_MAX_HOMING_FEEDRATE:
                raise Exception(
                    "Your desired homing speed of "
                    + str(max_speed_mm_per_min)
                    + "mm/min can not be greater than "
                    + str(HARDWARE_MAX_HOMING_FEEDRATE)
                    + "mm/min ("
                    + str(HARDWARE_MAX_HOMING_FEEDRATE / 60)
                    + "mm/s)"
                )

            gCodeCommand = (
                gCodeCommand
                + " "
                + self.myGCode.__getTrueAxis__(axis)
                + str(min_speed_mm_per_min)
                + ":"
                + str(max_speed_mm_per_min)
            )

        self.myGCode.__emitEchoOk__(gCodeCommand)

        return

    def saveData(self, key, data):
        # Note : This function has been deprecated.
        # '''
        # desc: Saves/persists data within the MachineMotion Controller in key - data pairs.
        # params:
        #     key:
        #         desc: A string that uniquely identifies the data to save for future retreival.
        #         type: String
        #     data:
        #         desc: The data to save to the machine. The data must be convertible to JSON format.
        #         type: String
        # note: The Data continues to exist even when the controller is shut off. However, writing to a previously used key will override the previous value.
        # exampleCodePath: getData_saveData.py
        # '''

        # Create a new object and augment it with the key value.
        dataPack = {}
        dataPack["fileName"] = key
        dataPack["data"] = data

        # Send the request to MachineMotion
        HTTPSend(self.IP + ":8000", "/saveData", json.dumps(dataPack))
        time.sleep(0.05)

        return

    def getData(self, key, callback):
        # Note : This function has been deprecated.
        # '''
        # desc: Retreives saved/persisted data from the MachineMotion controller (in key-data pairs). If the controller takes more than 3 seconds to return data, the function will return with a value of "Error - getData took too long" under the given key.
        # params:
        #     key:
        #         desc: A Unique identifier representing the data to be retreived
        #         type: String
        #     callback:
        #         desc: Function to callback to process data.
        #         type: function
        # exampleCodePath: getData_saveData.py
        # returnValue: A dictionary containing the saved data.
        # returnValueType: Dictionary
        # '''
        callback(HTTPSend(self.IP + ":8000", "/getData", key))

        return

    def emitDwell(self, milliseconds):
        # Note : This function has been deprecated.
        # '''
        # desc: Pauses motion for a specified time. This function is non-blocking; your program may accomplish other tasks while the machine is dwelling.
        # params:
        #     miliseconds:
        #         desc: The duration to wait in milliseconds.
        #         type: Integer
        # note: The timer starts after all previous MachineMotion movement commands have finished execution.
        # exampleCodePath: emitDwell.py
        # '''
        self.myGCode.__emitEchoOk__("G4 P" + str(milliseconds))
        return

    # This function is left in for legacy, however it is not documented because it is the same functionality as readEncoder
    def readEncoderRealtimePosition(self, encoder):
        self.isEncoderIdValid(encoder)  # Enforce restrictions on encoder ID
        return self.myEncoderRealtimePositions[encoder]

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

    def move(
        self,
        motor,
        rotation=None,
        speed=None,
        accel=None,
        reference="absolute",
        type="synchronous",
    ):
        if rotation is not None:
            # set motor to position mode
            self.myGCode.__emitEchoOk__(
                "V5 " + self.myGCode.__getTrueAxis__(motor) + "1"
            )

            if speed is not None:
                # send speed command (need to convert rotation/s to mm/min )
                self.myGCode.__emitEchoOk__(
                    "G0 F" + str(speed * 60 * self.mech_gain[motor])
                )

            if accel is not None:
                # send accel command (need to convert rotation/s^2 to mm/s^2)
                # Note : Set travel and print acceleration, to impact G0 and G1 commands.
                self.myGCode.__emitEchoOk__(
                    "M204 T"
                    + str(accel * self.mech_gain[motor])
                    + " P"
                    + str(accel * self.mech_gain[motor])
                )

            if reference == "absolute":
                # Set to absolute motion mode
                self.myGCode.__emitEchoOk__("G90")
                # Transmit move command
                self.myGCode.__emitEchoOk__(
                    "G0 "
                    + self.myGCode.__getTrueAxis__(motor)
                    + str(rotation * self.mech_gain[motor])
                )

            elif reference == "relative":
                # send relative move command
                # Set to relative motion mode
                self.myGCode.__emitEchoOk__("G91")
                # Transmit move command
                self.myGCode.__emitEchoOk__(
                    "G0 "
                    + self.myGCode.__getTrueAxis__(motor)
                    + str(rotation * self.mech_gain[motor])
                )

            else:
                return False

            if type == "synchronous":
                self.waitForMotionCompletion()
                return True

            elif type == "asynchronous":
                return True
        else:
            if speed is not None and accel is not None:
                # set motor to speed mode
                self.myGCode.__emitEchoOk__(
                    "V5 " + self.myGCode.__getTrueAxis__(motor) + "2"
                )

                # Send speed command
                self.myGCode.__emitEchoOk__(
                    "V4 S"
                    + str(speed * STEPPER_MOTOR.steps_per_turn * self.u_step[motor])
                    + " A"
                    + str(accel * STEPPER_MOTOR.steps_per_turn * self.u_step[motor])
                    + " "
                    + self.myGCode.__getTrueAxis__(motor)
                )

            else:
                return False

        return False


class MachineMotionV2(MachineMotion):
    """skip"""

    """z-index:99
    """

    def __init__(self, machineIp=DEFAULT_IP_ADDRESS.usb_windows):
        """
        desc: Constructor of MachineMotionV2 class
        params:
            machineIp:
                desc: IP address of the Machine Motion
                type: string of the DEFAULT_IP_ADDRESS class, or other valid IP address
        compatibility: MachineMotion v2.
        exampleCodePath: moveRelative.py
        """
        super(MachineMotionV2, self).__init__(
            machineIp, machineMotionHwVersion=MACHINEMOTION_HW_VERSIONS.MMv2
        )


class MachineMotionV2OneDrive(MachineMotion):
    """skip"""

    """z-index:98
    """

    def __init__(self, machineIp=DEFAULT_IP_ADDRESS.usb_windows):
        """
        desc: Constructor of MachineMotionV2OneDrive class
        params:
            machineIp:
                desc: IP address of the Machine Motion
                type: string of the DEFAULT_IP_ADDRESS class, or other valid IP address
        compatibility: MachineMotion v2 One Drive.
        exampleCodePath: oneDriveControl.py
        """
        super(MachineMotionV2OneDrive, self).__init__(
            machineIp, machineMotionHwVersion=MACHINEMOTION_HW_VERSIONS.MMv2OneDrive
        )


########################
######## LEGACY ########
########################

# All the classes below are left only for legacy and backwards compatibility purposes.
# Vention does not advise to use any of them.


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
    ENCODER = "ENCODER"


class CONTROL_DEVICE_PORTS:
    SENSOR4 = "SENSOR4"
    SENSOR5 = "SENSOR5"
    SENSOR6 = "SENSOR6"


class NETWORK_MODE:
    static = "static"
    dhcp = "dhcp"
