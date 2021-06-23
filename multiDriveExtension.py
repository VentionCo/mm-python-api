import sys, time, math
sys.path.append("..")
from MachineMotion import *

#########################################################
###### WRAPPER TO SYNCHRONIZE DRIVES WITH SOFTWARE ######
#########################################################

class MultiDriveExtension():
    def __init__(self, mm):
        if mm == None:
            mm = MachineMotion(machineMotionHwVersion=MACHINEMOTION_HW_VERSIONS.MMv2)
        self.mm = mm
        return

    # Configure the motors the same way, to make sure they don't fight each-other
    def configServoMulti(self, driveList, mechGain, directionList, motorCurrent, tuningProfile = TUNING_PROFILES.DEFAULT):
        '''
        desc: Configures motion parameters as a servo motor, for multiple drives on the MachineMotion v2. All motors should share the same gain, current and tuning profile.
        params:
            driveList :
                desc: The drives to configure.
                type: List of Numbers
            mechGain:
                desc: The distance moved by the actuator for every full rotation of the stepper motor, in mm/revolution.
                type: Number
            directionList:
                desc: The directions of the motors
                type: List of Strings from DIRECTION class
            motorCurrent:
                desc: The current to power the motor with, in Amps.
                type: Number
            tuningProfile:
                desc: The tuning profile of the smartDrive.
                type: String
        note: Warning, changing the configuration can de-energize motors and thus cause unintended behaviour on vertical axes.
        '''
        if len(driveList)!=len(directionList):
            raise "The length of driveList must be equal to length of directionList."
        for drive in driveList:
            self.mm._restrictCombinedAxisValue(drive)
        for i in range(len(driveList)):
            self.mm.configServo(driveList[i], mechGain, directionList[i], motorCurrent, tuningProfile)

    def configStepperMulti(self, driveList, mechGain, directionList, motorCurrent, microSteps = MICRO_STEPS.ustep_8):
        '''
        desc: Configures motion parameters as a stepper motor, for multiple drives on the MachineMotion v2. All motors should share the same gain, current and microstepping.
        params:
            driveList:
                desc: The drives to configure.
                type: List of Numbers
            mechGain:
                desc: The distance moved by the actuator for every full rotation of the stepper motor, in mm/revolution.
                type: Number
            directionList:
                desc: The direction of the axis
                type: List of Strings from DIRECTION class
            motorCurrent:
                desc: The current to power the motor with, in Amps.
                type: Number
            microSteps:
                desc: The microstep setting of the drive.
                type: Number from MICRO_STEPS class
        note: Warning, changing the configuration can de-energize motors and thus cause unintended behaviour on vertical axes.
        '''
        if len(driveList)!=len(directionList):
            raise "The length of driveList must be equal to length of directionList."
        for drive in driveList:
            self.mm._restrictCombinedAxisValue(drive)
        for i in range(len(driveList)):
            self.mm.configStepper(driveList[i], mechGain, directionList[i], motorCurrent)

    def emitRelativeMoveMulti(self, driveList, direction, distance):
        '''
        desc: Moves the multiple specified axes the specified distance in the specified direction.
        params:
            driveList:
                desc: The axes to move.
                type: List of Integers
            direction:
                desc: The direction of travel.
                type: String
            distance:
                desc: The travel distances in mm.
                type: Number
        '''
        self.mm.emitCombinedAxisRelativeMove(driveList, [direction]*len(driveList), [distance]*len(driveList))

    def emitAbsoluteMoveMulti(self, driveList, position):
        '''
        desc: Moves multiple specified axes to their desired end locations synchronously.
        params:
            driveList:
                desc: The axes which will perform the move commands.
                type: List of Integers
            position:
                desc: The desired end position.
                type: Number
        '''
        self.mm.emitCombinedAxesAbsoluteMove(driveList, [position]*len(driveList))

    def emitHomeMulti(self, driveList, homingSpeed=None, homingAcceleration=50):
        '''
        desc: Initiates the homing sequence for the specified axes.
        params:
            driveList:
                desc: The axes which will perform the home commands.
                type: List of Integers
            homingSpeed:
                desc: The speed of the homing move, in mm/sec.
                type: Number
            homingAcceleration:
                desc: The acceleration of the homing move, in mm/sec^2.
                type: Number
        note: Make sure you emitSpeed after emitHomeMulti. Make sure you have only one motor with a homing sensor (the other has jumpers)
        '''
        for drive in driveList:
            self.mm._restrictCombinedAxisValue(drive)

        def getHomingSpeedMarlin(microSteps_per_mm):
            USTEPS_PER_ROTATION=8*200
            LINEAR_REGRESSION_HOMING_FEEDRATE_X1=USTEPS_PER_ROTATION/150.0
            LINEAR_REGRESSION_HOMING_FEEDRATE_Y1=4000.0
            LINEAR_REGRESSION_HOMING_FEEDRATE_X2=USTEPS_PER_ROTATION/10.0
            LINEAR_REGRESSION_HOMING_FEEDRATE_Y2=2000.0
            LINEAR_REGRESSION_HOMING_FEEDRATE=LINEAR_REGRESSION_HOMING_FEEDRATE_Y1 + (microSteps_per_mm - LINEAR_REGRESSION_HOMING_FEEDRATE_X1)*(LINEAR_REGRESSION_HOMING_FEEDRATE_Y2-LINEAR_REGRESSION_HOMING_FEEDRATE_Y1)/(LINEAR_REGRESSION_HOMING_FEEDRATE_X2 - LINEAR_REGRESSION_HOMING_FEEDRATE_X1)
            if(LINEAR_REGRESSION_HOMING_FEEDRATE<2000):
                LINEAR_REGRESSION_HOMING_FEEDRATE=2000
            return LINEAR_REGRESSION_HOMING_FEEDRATE/60

        # The homing speed should be the default one, according to the gain
        if homingSpeed == None:
            # Verify that steps_mm exists
            if not self.mm._isNumber(self.mm.steps_mm[driveList[0]]):
                self.mm.populateStepsPerMm()
            steps_mm = self.mm.steps_mm[driveList[0]]
            homingSpeed = getHomingSpeedMarlin(steps_mm)

        # Set acceleration to an arbitrary small value (the default 50mm/sec is "good enough")
        self.emitAccelerationMulti(driveList, homingAcceleration)
        self.emitSpeedMulti(driveList, homingSpeed)
        # Long "infinite" negative move (meant to trigger the home sensor)
        self.emitRelativeMoveMulti(driveList, DIRECTION.NEGATIVE, 1000000)
        self.mm.waitForMotionCompletion()
        # Set position to zero
        self.setPositionMulti(driveList, 0)

    def getActualPositionsMulti(self, driveList):
        '''
        desc: Returns the current position of the multi-drive axis.
        params:
            driveList:
                desc: The drives involved in the multi-drive axis to get the current position of.
                type: List of Numbers
        returnValue: The position of the axis.
        returnValueType: Number
        '''
        for drive in driveList:
            self.mm._restrictCombinedAxisValue(drive)
        return self.mm.getActualPositions(driveList[0])

    def setPositionMulti(self, driveList, position):
        '''
        desc: Override the current position of the specified axes to a new value.
        params:
            driveList:
                desc: Overrides the position on these axes.
                type: List of Numbers
            position:
                desc: The new position value in mm.
                type: Number
        '''
        for drive in driveList:
            self.mm._restrictCombinedAxisValue(drive)
        for drive in driveList:
            self.mm.setPosition(drive, position)

    def emitSpeedMulti(self, driveList, speed):
        '''
        desc: Sets the speed for subsequent movement commands on the multi-drive axis.
        params:
            speed:
                desc: The global max speed in mm/sec.
                type: Number
        '''
        for drive in driveList:
            self.mm._restrictCombinedAxisValue(drive)
        compound_speed = speed*math.sqrt(len(driveList))  # this sets the euclidean speed
        self.mm.emitSpeed(compound_speed)

    def emitAccelerationMulti(self, driveList, acceleration):
        '''
        desc: Sets the acceleration for subsequent movement commands on the multi-drive axis.
        params:
            speed:
                desc: The global max acceleration in mm/sec^2.
                type: Number
        '''
        for drive in driveList:
            self.mm._restrictCombinedAxisValue(drive)
        compound_acc = acceleration*math.sqrt(len(driveList))   # this sets the euclidean acceleration
        self.mm.emitAcceleration(compound_acc)
