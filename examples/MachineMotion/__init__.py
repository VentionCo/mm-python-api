# # See StackOverflow - https://stackoverflow.com/questions/448271/what-is-init-py-for
# #  https://docs.python.org/3/reference/import.html#regular-packages
# # The main use for packaging this is to allow python 2 and python 3 compatibility in single source code

#import core
from __future__ import unicode_literals    # at top of module
from ._constants import *
from ._machineMotion import *


# Import package dependent libraries
try:
    from pathlib import Path
    import paho.mqtt.client as mqtt
    from socketIO_client import SocketIO, BaseNamespace
except ModuleNotFoundError as e:
    print("You do not have the correct modules installed. Please type 'pip install -r requirements.txt' to download the library dependencie")
