from __future__ import print_function
import sys
import collections

class configWizard:

    validYN = {"Y":True, "N":False}
    exitCommands = ["q"]
    class userQuit(Exception): pass

    def __init__(self):
        self.pythonVersion = sys.version_info[0]
        print("\n>>>\tMachine Motion Wizard Started - Press Q to quit at anytime")
        print(">>>\t----------------------------------------------------------\n>>>")

    def write(self, msg):
        print(">>>\t" + msg, end = "\n>>>\t")
            
        
    def quit(self):
        print(">>>\n>>>\tApplication Quit")
        raise self.userQuit

    def getUserInput(self):
        if self.pythonVersion == 2:
            return raw_input().lower()
        elif self.pythonVersion == 3:
            return input().lower()
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

        # Starts loop that exits when user either quits or enters a valid choice
        try:
            while True:
                self.write(question + " [" + " / ".join(valid.keys()) + "]")
                choice = self.getUserInput()

                if choice in valid:
                    return valid[choice]
                elif choice in self.exitCommands:
                    self.quit()
                else:
                    self.write("Please respond with [" + " or ".join(valid.keys()) + "] \n")
        except self.userQuit:
            return 
    
    #
    # Handles user interaction and logic for asking users questions that return numbers
    # @param question --- Description: A question for the user in string format
    #
    def askNumeric(self, question):
        try:
            while True:
                self.write(question)
                answer = self.getUserInput()

                if answer.isnumeric():
                    return answer
                else:
                    self.write("Please enter a number value")

        except self.userQuit:
            return 
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













# Demo of configWizard that is executed when module is run as a script
if __name__ == "__main__":
    import configWizard
    cw = configWizard.configWizard()
    question = "Do you like green eggs and ham?"
    valid = {"y":"I Do! I like them, Sam-I-Am!", "n":"I do not like them, Sam I am"}
    response = cw.askMultipleChoice(question, valid)
    print(response)
        