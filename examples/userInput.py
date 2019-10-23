import sys
import collections

#
# Handles user interaction and logic for asking users yes/no or multiple choice questions.
# @param question --- Description: A question for the user in string format
# @param valid --- Description: A set of valid answers to the question (such as {y,n} or {true, false} or {a,b,c,d})
#
def user_input(question, valid):
    choice = ""
    while True:
        print(question + " [" + " / ".join(valid.keys()) + "]")
        if sys.version_info[0] == 2:
            choice = raw_input().lower()
        elif sys.version_info[0] == 3:
            choice = input().lower()
        else:
            print("Application Error: Could not detect which python version is running")
            return "Error"

        if choice in valid:
            return valid[choice]
        else:
            print("Please respond with [" + " or ".join(valid.keys()) + "] \n")

#
# Prompts the user to check and confirm that sensor sensor xA and sensor xB are installed, where x represents a subset of axes 1,2,3
# @param axis --- Description: represent which axes need to be checked. It can be a single axis or a set of 2 or 3 axes.
# @return output --- Description: A dictionary whose keys are each sensor that needs verification (ex - 1A, 1B, 2A ...) and who's value is a boolean representing whether its been installed
#
def check_both_end_stops(axes):
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
        output[str(axis) + "A"] = user_input(question, valid)
        question = "Application Message: Is Sensor " + str(axis) + "B plugged in?"
        output[str(axis) + "B"] = user_input(question, valid)

    return output

