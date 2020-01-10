from _MachineMotion import *
import datetime

# Define a callback to machine motion
def templateCallback(data):
    print("Controller gCode responses " + data)

ip_address          = input("IP ADDRESS:").strip('\r')
number_of_estops    = int(input("NUMBER OF ESTOPS:"))

macaddress          = input("MAC Address:").strip('\r')

# Get date, time and create the test log
datetime.datetime.now()
report = open("C:/Users/raymondVention/Desktop/temp_results/" + macaddress + ".txt","a")
report.write("Date: "+str(datetime.datetime.now())+"\n")
report.write("Testing on port:" + ip_address + "\n")

accel_setup = 5000
speed_setup = 50000

encoder_1_init_pos = 0
encoder_2_init_pos = 0
encoder_3_init_pos = 0

# Instantiate MachineMotion
mm = MachineMotion(templateCallback, ip_address)

def reset_position_reference():

    global encoder_1_init_pos
    global encoder_2_init_pos
    global encoder_3_init_pos
    
    time.sleep(4)
    encoder_1_init_pos = (-1)*mm.readEncoderRealtimePosition(0)/3600.0
    encoder_2_init_pos = (-1)*mm.readEncoderRealtimePosition(1)/3600.0
    encoder_3_init_pos = (-1)*mm.readEncoderRealtimePosition(2)/3600.0

def configure_system():
    global mm
    global accel_setup
    global speed_setup
    global gain

    #Set default acceleration and speed
    mm.emitAcceleration(accel_setup)
    mm.emitSpeed(speed_setup)

    report.write("Speed: " + str(speed_setup) + " mm/s\n")
    report.write("Acceleration: " + str(accel_setup) + " mm/s^2\n")

    # Configure homing speed
    mm.emitgCode("V2 X10000 Y10000 Z10000")
    while mm.isReady() != "true": pass


    # Configure Axes
    for i in range(1, 4):
        mm.configAxis(i, 8, gain)
        while mm.isReady() != "true": pass

def test_homing_sensors():
    report.write("1 - HOMING SENSORS TEST \n")

    mm.emitHomeAll()
    while mm.isReady() != "true": pass

    report.write("All home sensors are good \n")

def test_end_sensors():
    global mm
    
    report.write("2 - END SENSORS TEST \n")

    mm.emitHomeAll()
    while mm.isReady() != "true": pass

    # Check end sensors
    mm.emitgCode("G91")
    mm.isReady()

    mm.emitgCode("G0 X150 F50000")
    mm.waitForMotionCompletion()
    mm.emitgCode("G0 X100 F50000")
    mm.waitForMotionCompletion()

    mm.emitgCode("G0 Y150 F50000")
    mm.waitForMotionCompletion()
    mm.emitgCode("G0 Y100 F5000")
    mm.waitForMotionCompletion()

    mm.emitgCode("G0 Z150 F50000")
    mm.waitForMotionCompletion()
    mm.emitgCode("G0 Z100 F5000")
    mm.waitForMotionCompletion()

    report.write("All end sensors are good \n")

def test_emergency_stop():

    global mm
    global number_of_estops
    
    x = 0
    
    mm.emitHomeAll()
    while mm.isReady() != "true": pass
    
    for x in range (0, number_of_estops):
        mm.emitgCode("G0 X150 Y150 Z150 F1000")
        mm.waitForMotionCompletion()
        
        print("Press E-Stop" + str(x))
        
        if input("1 for continue; 0 for exit:") == "0":
            break

    report.write("E-STOPS test passed\n")

def test_absolute_move():

    global mm
    
    global encoder_1_init_pos
    global encoder_2_init_pos
    global encoder_3_init_pos
    
    global gain
    
    global report
    
    report.write("3 - Absolute movement test \n")
    
    mm.emitHomeAll()
    while mm.isReady() != "true": pass

    reset_position_reference()

    mm.emitgCode("G90")
    while mm.isReady() != "true": pass

    mm.emitgCode("G0 X20 Y80 Z150 F50000")
    mm.waitForMotionCompletion()
    
    time.sleep(4)
    encoder_1_pos = ((-1)*mm.readEncoderRealtimePosition(0)/3600.0)-encoder_1_init_pos
    encoder_2_pos = ((-1)*mm.readEncoderRealtimePosition(1)/3600.0)-encoder_2_init_pos
    encoder_3_pos = ((-1)*mm.readEncoderRealtimePosition(2)/3600.0)-encoder_3_init_pos
    
    deviation_X = abs(20-encoder_1_pos*gain)
    deviation_Y = abs(80-encoder_2_pos*gain)
    deviation_Z = abs(150-encoder_3_pos*gain)

    if deviation_X < 2:
        report.write("X-Axis Absolute Movement Test Succeeded with " + str(deviation_X) + "mm deviation." + " Xtarget is 20mm. Xread is: " + str(encoder_1_pos*gain) + "\n")
    else:
        report.write("X-Axis Absolute Movement Test Failed with " + str(deviation_X) + "mm deviation." + " Xtarget is 20mm. Xread is: " + str(encoder_1_pos*gain) + "\n")
    if deviation_Y < 2:
        report.write("Y-Axis Absolute Movement Test Succeeded with " + str(deviation_Y) + "mm deviation." + " Ytarget is 80mm. Yread is: " + str(encoder_2_pos*gain) + "\n")
    else:
        report.write("Y-Axis Absolute Movement Test Failed with " + str(deviation_Y) + "mm deviation." + " Ytarget is 80mm. Yread is: " + str(encoder_2_pos*gain) + "\n")
    if deviation_Z < 2:
        report.write("Z-Axis Absolute Movement Test Succeeded with " + str(deviation_Z) + "mm deviation." + " Ztarget is 150mm. Zread is: " + str(encoder_3_pos*gain) + "\n")
    else:
        report.write("Z-Axis Absolute Movement Test Failed with " + str(deviation_Z) + "mm deviation." + " Ztarget is 150mm.  Zread is:  " + str(encoder_3_pos*gain) + "\n")

def test_relative_move():
    
    global mm
    
    global encoder_1_init_pos
    global encoder_2_init_pos
    global encoder_3_init_pos
    
    global gain
    
    global report

    report.write("4 - Relative movement test \n")
    
    mm.emitHomeAll("G90")
    while mm.isReady() != "true": pass

    reset_position_reference()
    
    mm.emitgCode("G90")
    while mm.isReady() != "true": pass

    mm.emitgCode("G0 X100 Y100 Z100 F50000")
    mm.waitForMotionCompletion()
    
    mm.emitgCode("G91")
    while mm.isReady() != "true": pass

    mm.emitgCode("G0 X50 Y-50 Z-50 F50000")
    mm.waitForMotionCompletion()
    
    time.sleep(4)
    encoder_1_pos = ((-1)*mm.readEncoderRealtimePosition(0)/3600.0)-encoder_1_init_pos
    encoder_2_pos = ((-1)*mm.readEncoderRealtimePosition(1)/3600.0)-encoder_2_init_pos
    encoder_3_pos = ((-1)*mm.readEncoderRealtimePosition(2)/3600.0)-encoder_3_init_pos
    
    deviation_X = abs(150-encoder_1_pos*gain)
    deviation_Y = abs(50-encoder_2_pos*gain)
    deviation_Z = abs(50-encoder_3_pos*gain)

    if deviation_X < 2:
        report.write("X-Axis Relative Movement Test Succeeded with " + str(deviation_X) + "mm deviation." + " Xtarget is 150mm. Xread is: " + str(encoder_1_pos*gain) + "\n")
    else:
        report.write("X-Axis Relative Movement Test Failed with " + str(deviation_X) + "mm deviation." + " Xtarget is 150mm. Xread is: " + str(encoder_1_pos*gain) + "\n")
    if deviation_Y < 2:
        report.write("Y-Axis Relative Movement Test Succeeded with " + str(deviation_Y) + "mm deviation." + " Ytarget is 50mm. Yread is: " + str(encoder_2_pos*gain) + "\n")
    else:
        report.write("Y-Axis Relative Movement Test Failed with " + str(deviation_Y) + "mm deviation." + " Ytarget is 50mm. Yread is: " + str(encoder_2_pos*gain) + "\n")
    if deviation_Z < 2:
        report.write("Z-Axis Relative Movement Test Succeeded with " + str(deviation_Z) + "mm deviation." + " Ztarget is 50mm. Zread is: " + str(encoder_3_pos*gain) + "\n")
    else:
        report.write("Z-Axis Relative Movement Test Failed with " + str(deviation_Z) + "mm deviation." + " Ztarget is 50mm. Zread is: " + str(encoder_3_pos*gain) + "\n")

configure_system()

test_homing_sensors()

test_end_sensors()

test_emergency_stop()

test_absolute_move()

test_relative_move()

report.close()
