[installPython1]: __documentation/_media/download-python-step1.png
[installPython2]: __documentation/_media/download-python-step2.png
[installPython3]: __documentation/_media/download-python-step3.png
[commandLine]: __documentation/_media/deploy-program-command-line.png
[cloud91]: __documentation/_media/deploy-program-cloud9-step1.png
[cloud92]: __documentation/_media/deploy-program-cloud9-step2.png
[cloud93]: __documentation/_media/deploy-program-cloud9-step3.png
[cloud94]: __documentation/_media/deploy-program-cloud9-step4.png

<p style="text-align:center;" ><img src="https://s3.amazonaws.com/ventioncms/vention_images/images/000/002/030/large/cover-python-guide-usermanual.png?15710631541550698858" width="90%" height="90%"></p>

<p>&nbsp;</p>

The MachineMotion Python API simplifies motion control and provides an intuitive, human-readable way to bring your equipment to life. 

Inexperienced programmers should consider using [MachineLogic's](https://www.vention.io/technical-documents/in-cad-automation-with-machinelogic-24) code-free visual sequence editor to create simple motion programs. 

However, for developing complex applications Python programs offer several attractives advantages. They are generally the optimal choice if:
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

* [Install Python on your computer](#install-python)
* [Download the MachineMotion API](#download-the-api-library)
* [Download the Required Libraries](#download-the-required-libraries)
* [Connecting to MachineMotion](#connecting-to-machinemotion)
* [Run your first program](#loading-programs-onto-machinemotion)

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

<p style="text-align: center;"><span style="color: #808080; font-size: 11pt;"><em>If your MachineMotion controller is connected to your computer (192.168.7.2), you can check its software version <a href="">here</a></em></p>



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

If you require more information about how to setup you controller to communicate with your computer or network, consult the resource below.

[User Manual: MachineMotion](https://www.vention.io/technical-documents/machine-motion-user-manual-71)

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
