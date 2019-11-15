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

Inexperienced programmers should consider using [MachineLogic's](https://www.vention.io/technical-documents/in-cad-automation-with-machinelogic-24) code-free visual sequence editor instead to create simple motion programs. 

Compared to MachineLogic, Python programs are more complicated, but they offer several advantages. They are generally the best choice if you want your application to:
* Communicate with custom hardware.
* Involve complex logic.
* Integrate with third-party software and tools.

#### For more information on 3D design using Vention, datasheets and more, please visit [Vention.io](https://www.vention.io/technical-documents/machinemotion-controller-datasheet-10).

<div>&nbsp;</div>

## Quick start
 Once you've connected your MachineMotion controller <span style="font-weight: 200"> (see <a href="connecting-to-machinemotion">here</a> for details)</span> running your first Python script is as simple as typing these commands into your terminal:

```console
$ git clone https://github.com/VentionCo/mm-python-api
$ python mm-python-api/examples/demo
```

## Installation

 This manual will guide you through five steps to get MachineMotion up and running with the Python API.

1. [Install Python on your computer](#install-python)
1. [Download the MachineMotion API](#download-the-api-library)
1. [Download the required libraries](#download-the-required-libraries)
1. [Connect to MachineMotion](#connect-to-machinemotion)
1. [Run your first program](#loading-programs-onto-machinemotion)

<div>&nbsp;</div>

### Install Python

1. Go to https://www.python.org/downloads/ to download the latest version of python 
![installPython1].

1. Open and run the installer. If you’re using Windows, make sure you select the option to <b>Add python to path</b>.
![installPython3]


<div>&nbsp;</div>


### Download the API library

MachineMotion comes with pre-installed controller software. There are two versions of the Python API, so make sure you install the correct version of the. The table below indicates which one to choose.

| Controller software| Python API | Git clone | Link |
| ------------- |:-------------:| :-----:| ---|
| v1.2.11 and earlier    | Python API v1.6.8 | `git clone https://github.com/VentionCo/mm-python-api/tree/release/v1.6.8` | [v1.6.8](https://github.com/VentionCo/mm-python-api/tree/release/v1.6.8) |
| v1.12.0 and later    | Python API v2.0+     | `git clone https://github.com/VentionCo/mm-python-api/tree/release/v2.0`) | [v1.12.0](https://github.com/VentionCo/mm-python-api/tree/release/v2.0)

<p style="text-align: center;"><span style="color: #808080; font-size: 11pt;"><em>If your MachineMotion controller is connected to your computer, you can check its software version <a href=”192.168.7.2”>here</a>.</em></p>



Open the command prompt (for Windows) or the terminal (for Mac or Linux), navigate to your destination folder, and paste the suitable 'git clone' command  

#### or 

Follow the download link above and unzip the contents in your directory of choice.

#### Need help? See Github's download guide [here](https://help.github.com/en/github/creating-cloning-and-archiving-repositories/cloning-a-repository).

<div>&nbsp;</div>

### Download the required libraries

 Open the command prompt (for Windows) or the terminal (for Mac or Linux) and run the following installations:  

  ```console
  $ pip install -U socketIO-client
  $ pip install -U pathlib
  $ pip install -U paho-mqtt
  ```

The MachineMotion Python library is now installed and ready to use! Continue below to start your first custom program. 

<div>&nbsp;</div>

## Connect to MachineMotion

MachineMotion connects to a laptop through Ethernet. If your laptop does not have an Ethernet port, use the USB to Ethernet converter included with your MachineMotion purchase. 

For more info on getting MachineMotion to communicate with your computer or network, see the user manual.

[User Manual: MachineMotion](https://www.vention.io/technical-documents/machine-motion-user-manual-71)

<div>&nbsp;</div>

## Loading programs onto MachineMotion

There are two ways to load a custom Python script onto MachineMotion:
1. With the command line/terminal.
1. With the cloud9 IDE.

### Command line programming

1. Open the command prompt (for Windows) or terminal (for Mac and Linux).

1. Browse to the directory where the MachineMotion API library is saved:  
  `cd path/to/folder/mm-python-api/`

1. Execute the demo program with the following line of code:  
   `python examples/example--demo.py` 

1. The demo program will launch. Press q or Ctrl+C to quit anytime.  
![commandLine]

### Cloud9 programming

1. Open the Cloud9 IDE: [http://192.168.7.2:3000/ide.html](http://192.168.7.2:3000/ide.html) 
![cloud91]

1. Copy and paste the `mm-python-api` folder into cloud9
![cloud92]

1. Navigate to examples/example--demo.py and press F5 or 'run' to execute the program
![cloud93]

1. Press 'Run' in the top toolbar of the cloud9 IDE
![cloud94]



## Explore the possibilities

Congratulations on loading your Python API script!

Keep exploring by browsing the sample code in our Python API documentation. 
[Application Programming Interface: Python v1.6.8](https://https://www.vention.io/technical-documents/a5e6df4eef66ae8826357fb2e15b2ab6/python-api-reference-v1-6-8)


###### Feedback on this doc? Please email info@vention.cc with the subject "Technical Documentation".
###### [Release notes: Python v1.6.8](release-notes.md)


