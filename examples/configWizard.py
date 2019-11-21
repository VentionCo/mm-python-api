from __future__ import print_function
import sys, os
import collections

try:
    from _MachineMotion import *
except ImportError:
    #Adds mm-python-api to the sys path so that we can access MachineMotion.py 
    parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.append(parentdir)
    from _MachineMotion import *

class configWizard:

    exitCommands = ["q"]
    class userQuit(Exception): pass
    delimiter = ">>\t"
    debugMode = False

    #Initializes variables and starts the command line interface
    def __init__(self):
        self.pythonVersion = sys.version_info[0]
        print("\n" + self.delimiter + "Machine Motion Wizard Started - Press Q to quit at anytime")
        print(self.delimiter + "----------------------------------------------------------")
        print(self.delimiter)

    def setDebugMode(self):
        self.debugMode =True
        return

    #
    # Styles the print messages while in the command line interface
    #
    def write(self, msg):
        if msg is not None:
            print(self.delimiter + msg, end = "\n")
        else: 
            print(self.delimiter + "User Quit Application Early")    

    #
    #Raises the 'user quit' error for error handling
    #
    def quitCW(self):
        print(self.delimiter + "\n" + self.delimiter + "Application Quit")
        raise self.userQuit
    
    #
    # Handles the user input into the command line interface.
    #
    def getUserInput(self):
        print(self.delimiter, end = '')
        if self.pythonVersion == 2:
            userinput = raw_input()
            userinput = userinput.split('\r')[0]

            if(self.debugMode):
                print(userinput)

            return userinput
        elif self.pythonVersion == 3:
            userinput = input()
            
            if(self.debugMode):
                print(userinput)
            
            return userinput.lower()
        else:
            self.write("Application Error: Could not detect which python version is running")
            return "Error"

    #
    # Handles user interaction and logic for asking users yes/no or multiple choice questions.
    # @param question --- Description: A question for the user in string format
    # @param valid --- Description: A set of valid answers to the question (such as {y,n} or {true, false} or {a,b,c,d})
    #
    def askMultipleChoice(self, question, valid):
        choice = ""
        #Makes the keys lowercase and removes any trailing/leading white spaces
        for key in valid.keys():
            valid[key.lower().strip()] = valid.pop(key)

        # Starts loop that exits when user either quits or enters a valid choice
        while True:
            self.write(question + " [" + " / ".join(valid.keys()) + "]")
            choice = self.getUserInput()
            choice =choice.lower().strip()

            if choice in valid:
                return valid[choice]
            elif choice in self.exitCommands:
                self.quitCW()
            else:
                self.write("Please type one of the " + str(len(valid)) + " valid answers exactly  [" + " or ".join(valid.keys()) + "] \n")

    #
    # Handles user interaction and logic for asking users questions that return numbers
    # @param question --- Description: A question for the user in string format
    #
    def askNumeric(self, question):

        self.write("")
        self.write(question)
        answer = self.getUserInput()

        if answer in self.exitCommands:
            self.quitCW()
        else:
            try:
                return int(answer)
            except ValueError:
                self.write("Please enter a number")
                return self.askNumeric(question)
        
    def askYesNo(self, question):
        valid = {"y":True, "n":False}
        return self.askMultipleChoice(question,valid)

    #
    # Prompts the user to check and confirm that sensor sensor xA and sensor xB are installed, where x represents a subset of axes 1,2,3
    # @param axis --- Description: represent which axes need to be checked. It can be a single axis or a set of 2 or 3 axes.
    # @return output --- Description: A dictionary whose keys are each sensor that needs verification (ex - 1A, 1B, 2A ...) and who's value is a boolean representing whether its been installed
    #
    def check_both_end_stops(self, axes):
        valid = {"y":True,"n":False}
        validAxes = {1,2,3}
        output = dict()

        try:
            axes = set(axes)
        except TypeError:
            if isinstance(axes, (int,long)):
                axes = { axes }
            else:
                raise TypeError

        if not axes.issubset(validAxes):
            print("Application Error: Function expects a list of axes that must be checked")

        for axis in axes:
            question = "Application Message: Is Sensor " + str(axis) + "A plugged in?"
            output[str(axis) + "A"] = self.askMultipleChoice(question, valid)
            question = "Application Message: Is Sensor " + str(axis) + "B plugged in?"
            output[str(axis) + "B"] = self.askMultipleChoice(question, valid)

        return output

    def askForSingleAxis(self):
        question = "What axis would you like to test?"
        valid = {"Drive 1":1, "Drive 2":2, "Drive 3":3}
        return self.askMultipleChoice(question, valid)
    
    def askForMechGain(self, axis):
        question = "What actuator do you have installed on axis " + str(axis)+ "?"
        valid = {
        "timing belt"    : MECH_GAIN.timing_belt_150mm_turn,
        "ballscrew"      : MECH_GAIN.ballscrew_10mm_turn,
        "indexer"        : MECH_GAIN.indexer_deg_turn,   
        "conveyor"       : MECH_GAIN.conveyor_mm_turn,               
        "rack and pinion": MECH_GAIN.rack_pinion_mm_turn                  
        }
        return self.askMultipleChoice(question, valid)

    def forceUserToHome(self, axis):
        if self.askYesNo("Would you like to begin homing Axis " + str(axis) + " ?") == False:
            self.write("You must home Axis " + str(axis) + " before sending motion commands")
            if self.askYesNo("Are you ready to home Axis " + str(axis) + "? If No, the demo will exit") == False:
                self.quitCW()

    def askForSpeedAndAcceleration(self):
        speed = self.askForSpeed()
        acceleration = self.askForAcceleration()
        return speed, acceleration


    def askForSpeed(self):
        question = "Please enter a value for global speed"
        return self.askNumeric(question)

    def askForAcceleration(self):
        question = "Please enter a value for global acceleration"
        return self.askNumeric(question)


    def unitTest(self):
        question = "Do you like green eggs and ham?"
        valid = {"y":"I Do! I like them, Sam-I-Am!", "n":"I do not like them, Sam I am"}
        response = self.askMultipleChoice(question, valid)
        self.write(response)

        question = "Would you eat them here or there?"
        valid = {"here":"I would not like them here", "there": "I would not like them there"}
        response = self.askMultipleChoice(question, valid)
        self.write(response)

        question = "Would you like them in a house? Would you like them with a mouse?"
        valid = {"no":"I do not like them in a house, I do not like them with a mouse", "house":"I will eat them in a hosue", "mouse":"I will eat them with a mouse"}
        response = self.askMultipleChoice(question, valid)
        self.write(response)

        question = "On a scale of 1-10 how much do you like green eggs and ham?"
        response = self.askNumeric(question)
        if response > 10:
            self.write("Say! I do so like green eggs and ham")
        elif response > 5:
            self.write("I guess they're okay")
        else:
            self.write("I still hate green eggs and ham")

