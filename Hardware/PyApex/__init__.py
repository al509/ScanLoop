'''
Python 3 package for controlling Apex Technologies equipments

    PyApex.AP1000 allows to control an AP1000 mainframe via Ethernet protocol
    "help(PyApex.AP1000)" for more details

    PyApex.AP2XXX allows to control an AP2XXX OSA or OCSA via Ethernet protocol
    "help(PyApex.AP2XXX)" for more details
    
    PyApex.Terminal allows to send and receive data from an AP2XXX or an AP1000
    directly.

    PyApex.AB3510 allows to control a board AB3510 quad photodetectors via USB 2.0 protocol
    this class requires PyUSB module installed
    "help(PyApex.AB3510)" for more details

    PyApex.AB3380 allows to control a board AB3380 dual filters via USB 2.0 protocol
    this class requires PyUSB module installed
    "help(PyApex.AB3380)" for more details

    PyApex.Etuve allows to control a XU Thermal Etuve via RS232 protocol
    this class requires PySerial module installed
    "help(PyApex.Etuve)" for more details
'''

from Hardware.PyApex.AP2XXX import AP2XXX
from Hardware.PyApex.Console import Terminal

from Hardware.PyApex.Constantes import Celerity

__Version = 1.01
__PythonVersion = 3.4

__ExpertMode = True


def version():
    '''
    Gets the version of the PyApex Package
    '''
    return __Version


def python():
    '''
    Gets the python version needed for the PyApex Package
    '''
    return __PythonVersion

    
def SetExpertMode(Mode):
    '''
    !!! NOT YET IMPLEMENTED !!!
    Sets the using mode of this package.
    Mode is a boolean:
        - False: User mode, only instructions present in
                 the user manual are enabled
        - True:  Expert mode, all instructions including
                 calibration instructions are enabled
    '''
    if isinstance(Mode, bool):
        __ExpertMode = Mode

def GetExpertMode():
    '''
    Gets the using mode of this package.
    This function returns a boolean:
        - False: User mode, only instructions present in
                 the user manual are enabled
        - True:  Expert mode, all instructions including
                 calibration instructions are enabled
    '''
    return __ExpertMode

def GetModule(ModName):
    '''
    Gets the installed modules.
    ModName is a string:
        - "usb":      returns True if the usb module has been
                      imported, False otherwise
        - "serial" :  returns True if the serial module has been
                      imported, False otherwise
    '''
    if isinstance(ModName, str):
        if ModName.lower() == "usb":
            return __UsbModule
        elif ModName.lower() == "serial":
            return __SerialModule

