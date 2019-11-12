from PyApex.Common import Send, Receive
import sys


class TunableLaser():

    
    def __init__(self, Equipment, Simulation=False):
        '''
        Constructor of a TLS embedded in an AP2XXX equipment.
        Equipment is the AP2XXX class of the equipment
        Simulation is a boolean to indicate to the program if it has to run in simulation mode or not
        '''
        self.__Connexion = Equipment.Connexion
        self.__Simulation = Simulation
        self.__ID = Equipment.GetID()
        
        # Variables and constants of the equipment
        self.__Unit = "dBm"
        self.__ValidUnits = ["dbm", "mw"]

        self.__Power = 0.0
        self.__Wavelength = 1550.0
        self.__Status = "OFF"


    def __str__(self):
        '''
        Return the equipment type and the AP2XXX ID
        '''
        return "TLS of " + str(self.__ID)
    
    
    def SetUnit(self, Unit):
        '''
        Set the power unit of the TLS equipment
        Unit is a string which could be "dBm" for logaritmic or "mW" for linear power
        '''
        from PyApex.Constantes import APXXXX_ERROR_ARGUMENT_TYPE
        from PyApex.Errors import ApexError
        
        try:
            Unit = str(Unit)
        except:
            self.__Connexion.close()
            raise ApexError(APXXXX_ERROR_ARGUMENT_TYPE, "Unit")
        else:
            if Unit.lower() in self.__ValidUnits:
                self.__Unit = Unit


    def GetUnit(self):
        '''
        Get the power unit of the TLS equipment
        The return unit is a string
        '''
        return self.__Unit
    
    
    def SetPower(self, Power):
        '''
        Set the power of the TLS equipment
        The power is expressed in the unit defined by the GetUnit() method
        '''
        from PyApex.Constantes import APXXXX_ERROR_ARGUMENT_TYPE
        from PyApex.Errors import ApexError
        from math import log10 as log

        if not isinstance(Power, (int, float)):
            self.__Connexion.close()
            raise ApexError(APXXXX_ERROR_ARGUMENT_TYPE, "Power")

        if self.__Unit.lower() == "mw":
            Power = 10.0 * log(Power)
        self.__Power = Power
        
        if not self.__Simulation:
            Command = "TLSPWR" + str("%.1f" %self.__Power) + "\n"               
            Send(self.__Connexion, Command)


    def GetPower(self):
        '''
        Get the power of the TLS equipment
        The returned power is expressed in the unit defined by the GetUnit() method
        '''
        from PyApex.Constantes import APXXXX_ERROR_ARGUMENT_TYPE, APXXXX_ERROR_ARGUMENT_VALUE
        from PyApex.Constantes import APXXXX_ERROR_VARIABLE_NOT_DEFINED
        from PyApex.Errors import ApexError
        from random import random

        if not self.__Simulation:
            Command = "TLSPWR?\n"               
            Send(self.__Connexion, Command)
            Power = float(Receive(self.__Connexion)[:-1])

            if self.__Unit.lower() == "mw":
                Power = 10.0**(Power / 10.0)

            self.__Power = Power
        
        return self.__Power
    
    
    def SetWavelength(self, Wavelength):
        '''
        Set the static wavelength of the TLS equipment
        The wavelength is expressed in nm
        '''
        from PyApex.Constantes import APXXXX_ERROR_ARGUMENT_TYPE
        from PyApex.Errors import ApexError

        if not isinstance(Wavelength, (int, float)):
            self.__Connexion.close()
            raise ApexError(APXXXX_ERROR_ARGUMENT_TYPE, "Wavelength")

        self.__Wavelength = Wavelength
        
        if not self.__Simulation:
            Command = "TLSSWL" + str("%.3f" %self.__Wavelength) + "\n"               
            Send(self.__Connexion, Command)


    def GetWavelength(self):
        '''
        Get the static wavelength of the TLS equipment
        The wavelength is expressed in nm
        '''
        
        if not self.__Simulation:
            Command = "TLSSWL?\n"               
            Send(self.__Connexion, Command)
            Wavelength = float(Receive(self.__Connexion)[:-1])
            
            self.__Wavelength = Wavelength

        return self.__Wavelength


    def SetFrequency(self, Frequency):
        '''
        Set the static frequency of the TLS equipment
        The frequency is expressed in GHz
        '''
        from PyApex.Constantes import APXXXX_ERROR_ARGUMENT_TYPE, VACCUM_LIGHT_SPEED
        from PyApex.Errors import ApexError

        if not isinstance(Frequency, (int, float)):
            self.__Connexion.close()
            raise ApexError(APXXXX_ERROR_ARGUMENT_TYPE, "Frequency")

        self.__Wavelength = VACCUM_LIGHT_SPEED / Frequency
        
        if not self.__Simulation:
            Command = "TLSSFR" + str("%.3f" %Frequency) + "\n"               
            Send(self.__Connexion, Command)


    def GetFrequency(self):
        '''
        Get the static frequency of the TLS equipment
        The frequency is expressed in GHz
        '''
        from PyApex.Constantes import VACCUM_LIGHT_SPEED
        
        if self.__Simulation:
            Frequency = VACCUM_LIGHT_SPEED / self.__Wavelength
        else:
            Command = "TLSSFR?\n"               
            Send(self.__Connexion, Command)
            Frequency = float(Receive(self.__Connexion)[:-1])
            
            self.__Wavelength = VACCUM_LIGHT_SPEED / Frequency

        return Frequency


    def On(self):
        '''
        Switch on the output power of TLS equipment
        '''
        
        if not self.__Simulation:
            Command = "TLSOUT1\n"
            Send(self.__Connexion, Command)
        
        self.__Status = "ON"


    def Off(self):
        '''
        Switch off the output power of the TLS equipment
        '''
        
        if not self.__Simulation:
            Command = "TLSOUT0\n"
            Send(self.__Connexion, Command)
        
        self.__Status = "OFF"


    def GetStatus(self):
        '''
        Return the status ("ON" or "OFF") of the TLS equipment
        '''

        if not self.__Simulation:
            Command = "TLSOUT?\n"               
            Send(self.__Connexion, Command)
            Status = int(Receive(self.__Connexion)[:-1])

            if Status == 1:
                self.__Status = "ON"
            else:
                self.__Status = "OFF"
        
        return self.__Status

