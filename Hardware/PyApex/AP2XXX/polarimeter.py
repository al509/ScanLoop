from PyApex.Common import Send, Receive
import sys


class Polarimeter():

    
    def __init__(self, Equipment, Simulation=False):
        '''
        Constructor of a Polarimeter embedded in an AP2XXX equipment.
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
        return "Polarimeter of " + str(self.__ID)
    
    
    def GetPolarimeterIdentity(self):
        '''
        Gets the serial number of the polarimeter board
        !!! FOR CALIBRATION ONLY !!!
        '''
        
        Values = []
        if not self.__Simulation:
            Command = "POLIDN?\n"
            Send(self.__Connexion, Command)
            Str = Receive(self.__Connexion, 64)[:-1]
            
            for value in Str.split(" "):
                Values.append(value)
        else:
            Values = ["XX-AB3510-XSIMUX", "1.0", "1.1"]
        
        return Values
    
    
    def GetPolarimeterRawPower(self):
        '''
        Gets the power values in binary from the 4 detectors of the polarimeter
        !!! FOR CALIBRATION ONLY !!!
        '''
        from random import randint
        
        Values = []
        if not self.__Simulation:
            Command = "POLRAWPOWER?\n"
            Send(self.__Connexion, Command)
            Str = Receive(self.__Connexion, 64)[:-1]
            
            for v in Str.split(" "):
                try:
                    Values.append(int(v))
                except:
                    pass
        else:
            for i in range(4):
                Values.append(randint(0, 2**14))
        
        return Values
    
    
    def GetPolarimeterTemp(self):
        '''
        Gets the polarimeter temperature in °C
        !!! FOR CALIBRATION ONLY !!!
        '''
        from random import random
        
        if not self.__Simulation:
            Command = "POLTEMP?\n"
            Send(self.__Connexion, Command)
            Str = Receive(self.__Connexion, 64)[:-1]
            
            try:
                Temperature = float(Str)
            except:
                Temperature = 0.0
        else:
            Temperature = 10.0 * random() + 20.0
        
        return Temperature
        
    
    def GetPolarimeterPower(self):
        '''
        Gets the power values in dBm from the 4 detectors of the polarimeter
        !!! FOR CALIBRATION ONLY !!!
        '''
        from random import random
        
        Values = []
        if not self.__Simulation:
            Command = "POLPOWER?\n"
            Send(self.__Connexion, Command)
            Str = Receive(self.__Connexion, 64)[:-1]
            
            for v in Str.split(" "):
                try:
                    Values.append(float(v))
                except:
                    pass
        else:
            for i in range(4):
                Values.append(80.0 * random() - 70.0)
        
        return Values
    
    
    def SetPolarimeterPath(self, Path="full"):
        '''
        Sets the polarimeter path
        Path can be a string or an integer
            - Path = "full" or 0 : the polarimeter input is used (no optical filter) (default)
            - Path = "filtered" or 1 : the OSA input is used (a 170 pm optical filter is used)
        '''
        from PyApex.Constantes import APXXXX_ERROR_ARGUMENT_TYPE
        from PyApex.Errors import ApexError
        
        if not self.__Simulation:
            Command = "POLPATH"
            if isinstance(Path, str):
                if Path.lower() == "filtered":
                    Command += "1"
                else:
                    Command += "0"
            elif isinstance(Path, int):
                if Path == 1:
                    Command += "1"
                else:
                    Command += "0"
            else:
                raise ApexError(APXXXX_ERROR_ARGUMENT_TYPE, "Path")
                sys.exit()
            
            Command += "\n"
            Send(self.__Connexion, Command)
            
    
    def GetPolarimeterPath(self):
        '''
        Gets the polarimeter path
        The returned path is a string:
            - "full" if the polarimeter input is used (no optical filter),
            - "filtered" if the OSA input is used (a 170 pm optical filter is used)
            - "error" if it's not a defined path
        '''
        
        PathString = ""
        if not self.__Simulation:
            Command = "POLPATH?\n"
            Send(self.__Connexion, Command)
            Str = Receive(self.__Connexion, 64)[:-1]
            
            try:
                if int(Str) == 1:
                    PathString = "filtered"
                elif int(Str) == 0:
                    PathString = "full"
            except:
                PathString = "error"
        else:
            PathString = "full"
        
        return PathString
            
            
    def SetPolarimeterWavelength(self, Wavelength):
        '''
        Sets the polarimeter wavelength. Wavelength is expressed in nm
        If the "filtered" path is used, the filter is set to the specified wavelength
        '''
        from PyApex.Constantes import APXXXX_ERROR_ARGUMENT_TYPE
        from PyApex.Errors import ApexError
        
        if not isinstance(Wavelength, (int, float)):
            raise ApexError(APXXXX_ERROR_ARGUMENT_TYPE, "Wavelength")
            sys.exit()
        
        if not self.__Simulation:
            Command = "POLWL" + str(Wavelength) + "\n"
            Send(self.__Connexion, Command)
            
    
    def GetPolarimeterWavelength(self):
        '''
        Gets the polarimeter wavelength
        The returned wavelength is expressed in nm
        '''
        
        if not self.__Simulation:
            Command = "POLWL?\n"
            Send(self.__Connexion, Command)
            Str = Receive(self.__Connexion, 64)[:-1]
            
            try:
                Wavelength = float(Str)
            except:
                Wavelength = 0.0
        else:
            Wavelength = 1550.0
        
        return Wavelength        
    

    def GetStateOfPolarization(self):
        '''
        Gets the State Of Polarization for the selected path
        and the selected wavelength
        '''
        from random import random
        from math import sqrt
        
        Values = []
        if not self.__Simulation:
            Command = "POLSOP?\n"
            Send(self.__Connexion, Command)
            Str = Receive(self.__Connexion, 64)[:-1]
            
            for v in Str.split(" "):
                try:
                    Values.append(float(v))
                except:
                    pass
        else:
            S = []
            S.append(1.0)
            for i in range(3):
                S.append(2.0 * random() - 1.0)
            S0 = sqrt(S[0]**2 + S[1]**2 + S[2]**2)
            for i in range(4):
                Values.append(S[i] / S[0])
        
        return Values
        
    