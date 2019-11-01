[installPython1]: __documentation/_media/python_2.7_download.png
[installPython2]: __documentation/_media/python_2.7_install_edited.png
[installPython3]: __documentation/_media/python_3.6_install_edited.png
[commandLine]: __documentation/_media/command_Line_Demo.png
[cloud91]: __documentation/_media/cloud9_0.png
[cloud92]: __documentation/_media/cloud9_1.png
[cloud93]: __documentation/_media/cloud9_2.png
[cloud94]: __documentation/_media/cloud9_3.png
<p style="text-align:center;" ><img src="https://s3.amazonaws.com/ventioncms/vention_images/images/000/001/021/large/cover_python_guide.png?1550698357" ></p>


<p>&nbsp;</p>

The MachineMotion Python API simplifies motion control and provides an intuitive, human-readable way to bring your equipment to life. 

Inexperienced programmers should consider using [MachineLogic's](https://www.vention.io/technical-documents/in-cad-automation-with-machinelogic-24) code-free visual sequence editor to create simple motion programs. 

However, this Python API is better suited to developing complex applications. 
The API should be your development tool if:
* The application must communicate with custom hardware
* The application requires complex logic
* The application must integrate with third party software and tools

###### For more information on 3D design using Vention, datasheets and more, please visit [Vention.io](https://www.vention.io/technical-documents/machinemotion-controller-datasheet-10)

<div>&nbsp;</div>

## Quick Start
Wire up the MachineMotion controller ([How-To](#connecting-to-machinemotion)) then type the following commands in the terminal:
```console
$ git clone https://github.com/VentionCo/mm-python-api
$ python mm-python-api/examples/demo
```

## Getting Started

To get started with the MachineMotion Python API:

* Install Python [(link)](#install-python-on-your-computer)
* Download MachineMotion API  [(link)](#install-python-on-your-computer)
* Download required libraries [(link)](#install-python-on-your-computer)
* Connect to MachineMotion [(link)](#install-python-on-your-computer)
* Run your first program [(link)](#install-python-on-your-computer)

<div>&nbsp;</div>

### Install Python
| | |
|---|---|
|![installPython1]|1. Go to https://www.python.org/downloads/ to download the latest version of python |
|![installPython3]|2. Open and run the installer. If using Windows, ensure "Add python to path" option is selected |


<div>&nbsp;</div>


### Download The API Library

The MachineMotion controller software comes pre-installed on the MachineMotion controller. There are two versions of the Python API, so the correct version of the Python API must be selected. The table below shows which version should be downloaded.

| Controller Software| Python API | Git Clone | Link |
| ------------- |:-------------:| :-----:| ---|
| v1.2.11 and earlier    | Python API v1.6.8 | `git clone https://github.com/VentionCo/mm-python-api/tree/release/v1.6.8` | [v1.6.8](https://github.com/VentionCo/mm-python-api/tree/release/v1.6.8) |
| v1.12.0 and later    | Python API v2.0+     | `git clone https://github.com/VentionCo/mm-python-api/tree/release/v2.0`) | [v1.12.0](https://github.com/VentionCo/mm-python-api/tree/release/v2.0)

###### If your machine motion is connected, you can check your controller software vesion <a href="http://192.168.7.2/">here</a> at the top of the page



Open the command prompt (for Windows) or the terminal (for Mac or Linux), navigate to your destination folder and paste the suitable 'git clone' command  

###### or

Follow the download link above and unzip the contents in your directory of choice


###### Need Help? See Github's download guide [here](https://help.github.com/en/github/creating-cloning-and-archiving-repositories/cloning-a-repository)

<div>&nbsp;</div>

### Download the required libraries

 Open the command prompt (for Windows) or the terminal (for Mac or Linux) and run the following installations  

  ```console
  $ pip install -U socketIO-client
  $ pip install -U pathlib
  $ pip install -U paho-mqtt
  ```

The MachineMotion Python library is now installed and ready to use! Continue below to start your first custom program. 

<div>&nbsp;</div>

## Connecting to MachineMotion

MachineMotion connects to a laptop through Ethernet. If your laptop does not have an ethernet port, use the USB to ethernet converter included with the MachineMotion. 


[QuickStart: Connecting to MachineMotion](__documentation/quick_start/machine_motion--quickstart.md)

<div>&nbsp;</div>

## Loading programs onto MachineMotion
There are 2 ways to load a custom python script onto MachineMotion: with the command line or with the cloud9 IDE.

### Command Line Programing

| | |
|---|---|
|![commandLine]| - Open the command prompt (for windows) or terminal (for Mac and Linux) <br>  - Browse to the directory where the MachineMotion API library is saved <br>  - Execute the demo program with the following line of code: <br>     - `python examples/example--demo.py` <br>  - The demo program will launch. Press q or Ctrl+C to quit at anytime. 


### Cloud9 Programing
| | |
|---|---|
|![cloud91]| Open up the Cloud9 IDE: [http://192.168.7.2:3000/ide.html](http://192.168.7.2:3000/ide.html) |
|![cloud92]| Copy and paste the `mm-python-api` folder into cloud9
|![cloud93]| Navigate to examples/example--demo.py and press F5 or 'run' to execute the program
|![cloud94]| Press 'Run' in the top toolbar of the cloud9 IDE


## Explore the Docs!

Congratulations on loading your Python API script!

Continue your journey by reading the docs and reading the example codes.
[Application Programming Interface: Python v1.6.8](__documentation/api/machine_motion_python_api--v1.6.8.md)


###### Please send any technical documnetation feedback to info@vention.cc with the subject "Technical Documentation"
###### [Release Notes: Python v1.6.8](release-notes.md)