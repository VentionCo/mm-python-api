import sys
import collections

# Define a function to obtain user input
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

