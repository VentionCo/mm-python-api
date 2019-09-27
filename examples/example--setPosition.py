                
                
                
##################################################
## Set Position
##################################################
## Author: Francois Giguere
## Version: 1.6.8
## Email: info@vention.cc
## Status: rdy for test
##################################################

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
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                // REGISTER 42: im_set_controller_pos_axis_2
                if(data.search("SET im_set_controller_pos_axis_2") != -1) {
                    var userIntendedPositon =  parseFloat(data.substring("SET im_set_controller_pos_axis_2".length + 1, data.length -1)) / 1000;
                    motion_controller.serialPortSendPacket("G92 Y" + userIntendedPositon);
                    socketSafeWrite(urSocket, "Ack");