from PyApex.Common import Send, Receive
import sys


class Filter():

    
    def __init__(self, Equipment, Simulation=False):
        '''
        Constructor of a Filter embedded in an AP2XXX equipment.
        Equipment is the AP2XXX class of the equipment
        Simulation is a boolean to indicate to the program if it has to run in simulation mode or not
        '''
        self.__Connexion = Equipment.Connexion
        self.__Simulation = Simulation
        self.__ID = Equipment.GetID()


    def __str__(self):
        '''
        Return the equipment type and the AP2XXX ID
        '''
        return "Filter of " + str(self.__ID)
    
    
    def GetFilterIdentity(self):
        '''
        Gets the serial number of the filter board
        !!! FOR CALIBRATION ONLY !!!
        '''
        
        Values = []
        if not self.__Simulation:
            Command = "FILIDN?\n"
            Send(self.__Connexion, Command)
            value = Receive(self.Connexion, 64)[:-1]
        else:
            value = "XX-3380-A-XSIMUX"
        
        return value
    
    
    def SetFilterOutput(self, State = False):
        '''
        Sets the state of the internal optical switch
        State can be a boolean or an integer:
            - State = 0 or False : the filter output is not enabled (default)
            - State = 1 or True : the filter output is enabled
        '''
        from PyApex.Constantes import APXXXX_ERROR_ARGUMENT_TYPE, APXXXX_ERROR_ARGUMENT_VALUE
        from PyApex.Errors import ApexError
        
        if not isinstance(State, (int, bool)):
            raise ApexError(APXXXX_ERROR_ARGUMENT_TYPE, "State")
            sys.exit()
        
        if int(State) not in [0, 1]:
            raise ApexError(APXXXX_ERROR_ARGUMENT_VALUE, "State")
            sys.exit()
        
        if not self.__Simulation:
            Command = "FILOUTENABLE" + str(int(State)) + "\n"
            Send(self.__Connexion, Command)
    
    
    def GetFilterOutput(self):
        '''
        Gets the state of the internal optical switch
        the returned state is a boolean:
            - State = False : the filter output is not enabled
            - State = True : the filter output is enabled
        '''
        
        if not self.__Simulation:
            Command = "FILOUTENABLE?\n"
            Send(self.__Connexion, Command)
            State = Receive(self.__Connexion, 64)[:-1]
            try:
                State = bool(int(State))
            except:
                pass
        else:
            State = True
            
        return State
    
    
    def SetFilterWavelength(self, Wavelength):
        '''
        Sets the filter static wavelength
        Wavelength is expressed in nm
        '''
        from PyApex.Constantes import APXXXX_ERROR_ARGUMENT_TYPE
        from PyApex.Errors import ApexError
        
        if not isinstance(Wavelength, (int, float)):
            raise ApexError(APXXXX_ERROR_ARGUMENT_TYPE, "Wavelength")
            sys.exit()
        
        if not self.__Simulation:
            Command = "FILWL" + str(Wavelength) + "\n"
            Send(self.__Connexion, Command)
            
        
    def GetFilterWavelength(self):
        '''
        Gets the static wavelength of the optical filter
        the returned wavelength is expressed in nm
        '''
        from random import random
        
        if not self.__Simulation:
            Command = "FILWL?\n"
            Send(self.__Connexion, Command)
            Wavelength = Receive(self.__Connexion, 64)[:-1]
            try:
                Wavelength = float(Wavelength)
            except:
                pass
        else:
            Wavelength = 30.0 * random() + 1530.0
            
        return Wavelength


    def SetFilterMode(self, Mode = "single"):
        '''
        Sets the filter mode
        Mode can be an integer or a string:
            Mode = 1 or "single" : Only 1 filter is used (default)
            Mode = 2 or "dual" : 2 cascaded filters are used
        '''
        from PyApex.Constantes import APXXXX_ERROR_ARGUMENT_TYPE
        from PyApex.Errors import ApexError
        
        if not isinstance(Mode, (int, str)):
            raise ApexError(APXXXX_ERROR_ARGUMENT_TYPE, "Mode")
            sys.exit()
        
        if isinstance(Mode, string):
            if Mode.lower() == "dual":
                Mode = 2
            else:
                Mode = 1
        elif isinstance(Mode, int):
            if Mode == 2:
                Mode = 2
            else:
                Mode = 1
        else:
            raise ApexError(APXXXX_ERROR_ARGUMENT_TYPE, "Mode")
            sys.exit()
        
        if not self.__Simulation:
            Command = "FILMODE" + str(Mode) + "\n"
            Send(self.__Connexion, Command)
            
        
    def GetFilterMode(self):
        '''
        Gets the Mode of the optical filter
        the returned Mode is an integer
        '''
        
        if not self.__Simulation:
            Command = "FILMODE?\n"
            Send(self.__Connexion, Command)
            Mode = Receive(self.__Connexion, 64)[:-1]
            try:
                Mode = int(Mode)
            except:
                pass
        else:
            Mode = 1
            
        return Mode
        
        
    def SetFilterStartWavelength(self, Wavelength):
        '''
        Sets the filter start wavelength for sweep
        Wavelength is expressed in nm
        '''
        from PyApex.Constantes import APXXXX_ERROR_ARGUMENT_TYPE
        from PyApex.Errors import ApexError
        
        if not isinstance(Wavelength, (int, float)):
            raise ApexError(APXXXX_ERROR_ARGUMENT_TYPE, "Wavelength")
            sys.exit()
        
        if not self.__Simulation:
            Command = "FILSTARTWL" + str(Wavelength) + "\n"
            Send(self.__Connexion, Command)
            
        
    def GetFilterStartWavelength(self):
        '''
        Gets the start wavelength of the optical filter sweep
        the returned wavelength is expressed in nm
        '''
        from random import random
        
        if not self.__Simulation:
            Command = "FILSTARTWL?\n"
            Send(self.__Connexion, Command)
            Wavelength = Receive(self.__Connexion, 64)[:-1]
            try:
                Wavelength = float(Wavelength)
            except:
                pass
        else:
            Wavelength = 15.0 * random() + 1530.0
            
        return Wavelength    
        
    
    def SetFilterStopWavelength(self, Wavelength):
        '''
        Sets the filter start wavelength for sweep
        Wavelength is expressed in nm
        '''
        from PyApex.Constantes import APXXXX_ERROR_ARGUMENT_TYPE
        from PyApex.Errors import ApexError
        
        if not isinstance(Wavelength, (int, float)):
            raise ApexError(APXXXX_ERROR_ARGUMENT_TYPE, "Wavelength")
            sys.exit()
        
        if not self.__Simulation:
            Command = "FILSTOPWL" + str(Wavelength) + "\n"
            Send(self.__Connexion, Command)
            
        
    def GetFilterStopWavelength(self):
        '''
        Gets the start wavelength of the optical filter sweep
        the returned wavelength is expressed in nm
        '''
        from random import random
        
        if not self.__Simulation:
            Command = "FILSTOPWL?\n"
            Send(self.__Connexion, Command)
            Wavelength = Receive(self.__Connexion, 64)[:-1]
            try:
                Wavelength = float(Wavelength)
            except:
                pass
        else:
            Wavelength = 15.0 * random() + 1545.0
            
        return Wavelength

    
    def FilterRun(self, Type = "single"):
        '''
        Run a sweep with the optical filter
        If Type is
            - "single" or 1, a single measurement is running (default)
            - "repeat" or 2, a repeat measurement is running
        '''
        from PyApex.Constantes import APXXXX_ERROR_ARGUMENT_TYPE
        from PyApex.Errors import ApexError
        
        if not isinstance(Type, (int, str)):
            raise ApexError(APXXXX_ERROR_ARGUMENT_TYPE, "Type")
            sys.exit()
        
        if isinstance(Type, string):
            if Type.lower() == "repeat":
                Type = 2
            else:
                Type = 1
        elif isinstance(Type, int):
            if Type == 2:
                Type = 2
            else:
                Type = 1
        else:
            raise ApexError(APXXXX_ERROR_ARGUMENT_TYPE, "Type")
            sys.exit()
        
        if not self.__Simulation:
            Command = "FILRUN" + str(Type) + "\n"
            Send(self.__Connexion, Command)
    
    
    def FilterStop(self):
        '''
        Stop a sweep with the optical filter
        If the filter is not running or is running in 'single' mode,
        this command has no effect
        '''
        
        if not self.__Simulation:
            Command = "FILSTOP\n"
            Send(self.__Connexion, Command)