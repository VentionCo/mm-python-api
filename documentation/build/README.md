# pythonAPIDocGen

Description:
This tool parses the docstrings inside our MachineMotion python library. It converts these docstrings into an html template. 


1) update mm-python-api to the latest git version
2) ensure docstrings have the following format to be properly converted to html:

    '''
    desc: Sets voltage on specified pin of digital IO output pin to either logic HIGH (24V) or LOW (0V).
    params:
        deviceNetworkId:
            desc:The IO Modules device network ID. It can be found printed on the product sticker on the back of the digital IO module.
            type: Integer
        pin:
            desc: The output pin number to write to.
            type: Integer
        value:
            desc: Writing '1' or HIGH will set digial output to 24V, writing 0 will set digital output to 0V.
            type: Integer
    returnValue: Description of return value
    returnValueType: Type
    exampleCodePath: example code filename (assumes code is saved in mm-python-api/examples)
    note: Output pins maximum sourcing current is 75 mA and the maximum sinking current is 100 mA. The pin labels on the digital IO module (pin 1, pin 2, pin 3, pin 4) correspond in software to (0, 1, 2, 3). Therefore, digitalWrite(deviceNetworkId, 2, 1)  will set output pin 3 to 24V.

    '''

3) run 'python generateHtml.py' *** only tested with python 2