# from flask import Flask
# app = Flask(__name__)

# @app.route('/')
# def hello_world():
#     return 'Hello, World!'

from MachineMotion import *

mm = MachineMotion("192.168.7.2")

mm.emitSpeed(10)
mm.emitRelativeMove(1, "positive", 1000)
mm.waitForMotionCompletion()