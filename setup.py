#!/usr/bin/env python

from distutils.core import setup

setup(name='mm_python_api',
      version='4.2',
      description='MachineMotion Python SDK',
      packages=[''],
      install_requires=['socketio-client', 'pathlib', 'paho-mqtt']
     )
