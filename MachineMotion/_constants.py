
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

# units are mm/min
HARDWARE_MAX_HOMING_FEEDRATE = 15999
HARDWARE_MIN_HOMING_FEEDRATE = 251