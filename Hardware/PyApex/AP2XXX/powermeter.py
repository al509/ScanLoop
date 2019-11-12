from PyApex.Common import Send, Receive
import sys


class Powermeter():

    
    def __init__(self, Equipment, Simulation=False):
        '''
        Constructor of a Powermeter embedded in an AP2XXX equipment.
        Equipment is the AP2XXX class of the equipment
        Simulation is a boolean to indicate to the program if it has to run in simulation mode or not
        '''
        self.__Connexion = Equipment.Connexion
        self.__Simulation = Simulation
        self.__ID = Equipment.GetID()
        
        # Variables and constants of the equipment
        self.__Unit = "dBm"
        self.__ValidUnits = ["dbm", "mw"]


    def __str__(self):
        '''
        Return the equipment type and the AP2XXX ID
        '''
        return "Powermeter of " + str(self.__ID)
    
    
    def SetUnit(self, Unit):
        '''
        Set the power unit of the Powermeter equipment
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
        Get power unit of the Powermeter equipment
        The return unit is a string
        '''
        return self.__Unit
    
    
    def GetPower(self, Polar=0):
        '''
        Get the power measured by the Powermeter equipment
        The return power is expressed in the unit defined by the GetUnit() method
        Polar is the polarization channel :
            - 0 : Total power (default)
            - 1 : Power of polarization channel n°1
            - 2 : Power of polarization channel n°2
        '''
        from PyApex.Constantes import APXXXX_ERROR_ARGUMENT_TYPE, APXXXX_ERROR_ARGUMENT_VALUE
        from PyApex.Constantes import APXXXX_ERROR_VARIABLE_NOT_DEFINED
        from PyApex.Errors import ApexError
        from random import random
        
        if not isinstance(Polar, (int)):
            self.__Connexion.close()
            raise ApexError(APXXXX_ERROR_ARGUMENT_TYPE, "Polar")

        if self.__Simulation:
            if self.__Unit.lower() == "dbm":
                Power = 60.0 * random() - 50.0
            elif self.__Unit.lower() == "mw":
                Power = 10.0 * random()
            else:
                self.__Connexion.close()
                raise ApexError(APXXXX_ERROR_VARIABLE_NOT_DEFINED, "self.__Unit")
        else:
            Command = "SPMEASDETECTORDBM1\n"               
            Send(self.__Connexion, Command)
            Power = Receive(self.__Connexion)[:-1]

            for p in Power.split("_"):
                try:
                    Power = float(p)
                except:
                    pass
                
        return Power
    
    
