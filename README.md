# MachineMotion Programming with Python

<p style="text-align:center;" ><img src="__documentation/_media/CE-CL-105-0003_+python.png" width="75%" height="75%"></p>
<p style="text-align: center;"><span style="color: #808080; font-size: 11pt;"><em>Figure 1: MachineMotion Controller.</em></p>

<p>&nbsp;</p>

## Installation

To set up the MachineMotion Python Library on your computer, follow the steps below:

- Download the version of the library that you require on [GitHub](https://github.com/VentionCo/mm-python-api/releases)

- Install Python on your computer. The MachineMotion library supports both Python 2.7 and Python 3.6.

    - If installing on Windows, make sure to add Python.exe to the PATH environment variable as shown in *Figure 2* and *Figure 3*.

<p style="text-align:center;" ><img src="__documentation/_media/python_2.7_install_edited.png" width="45%" height="45%" <img style="border:1px solid grey;"></p>

<p style="text-align: center;"><span style="color: #808080; font-size: 11pt;"><em>Figure 2: Make sure to select "Add python.exe to path" if installing on Windows.</em></p>

<p style="text-align:center;" ><img src="__documentation/_media/python_3.6_install_edited.png" width="45%" height="45%" <img style="border:1px solid grey;"></p>

<p style="text-align: center;"><span style="color: #808080; font-size: 11pt;"><em>Figure 3: Make sure to click "Add Python 3.6 to PATH" if installing on Windows.</em></p>

- Open the command prompt (for Windows) or the terminal (for Mac or Linux) and run the following installations  

  ```console
  pip install -U socketIO-client
  ```  
  
  ```console
  pip install -U pathlib
  ```

  ```console
  pip install -U paho-mqtt
  ```

- The MachineMotion Python library is now ready to use. Programs can be created and ran from the examples folder.

## Connecting to MachineMotion

If you require more information about how to setup you controller to communicate with your computer or network, consult the ressource below.

[QuickStart: Connecting to MachineMotion](__documentation/quick_start/machine_motion--quickstart.md)

## API Documentation

[Application Programming Interface: Python v1.6.8](__documentation/api/machine_motion_python_api--v1.6.8.md)

## Release Notes
[Release Notes: Python v1.6.8](release-notes.md)
