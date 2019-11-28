
import sys, os
from _MachineMotion import *

mm = MachineMotion(debug, DEFAULT_IP_ADDRESS.usb_windows)

# Configure the axis number 1, 8 uSteps and 150 mm / turn for a timing belt
mm.configAxis(axis=1, _u_step=MICRO_STEPS.ustep_8, _mech_gain = MECH_GAIN.timing_belt_150mm_turn)

