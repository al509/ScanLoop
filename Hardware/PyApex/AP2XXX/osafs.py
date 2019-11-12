from PyApex.Common import Send, Receive
import sys


class OsaFs():

    
    def __init__(self, Equipment, Simulation=False):
        '''
        Constructor of an OSA Fast-Sweep embedded in an AP2XXX equipment.
        Equipment is the AP2XXX class of the equipment
        Simulation is a boolean to indicate to the program if it has to run in simulation mode or not
        '''
        self.__Connexion = Equipment.Connexion
        self.__Simulation = Simulation
        self.__ID = Equipment.GetID()
        
        # Variables and constants of the equipment
        self.__StartWavelength = 1530.0
        self.__StopWavelength = 1560.0
        self.__Span = self.__StopWavelength - self.__StartWavelength
        self.__Center = self.__StartWavelength + (self.__Span / 2.0)
        self.__Mode = 2


    def __str__(self):
        '''
        Return the equipment type and the AP2XXX ID
        '''
        return "OSA Fast-Sweep of " + str(self.__ID)
        
        
    def SetStartWavelength(self, Wavelength):
        '''
        Set the start wavelength of the measurement span
        Wavelength is expressed in nm
        '''
        from PyApex.Constantes import APXXXX_ERROR_ARGUMENT_TYPE        
        from PyApex.Errors import ApexError
        
        if not isinstance(Wavelength, (float, int)):
            raise ApexError(APXXXX_ERROR_ARGUMENT_TYPE, "Wavelength")
            sys.exit()

        if not self.__Simulation:
            Command = "OSAFSSTARTWL" + str(Wavelength) + "\n"
            Send(self.__Connexion, Command)

        self.__StartWavelength = Wavelength
        self.__Span = self.__StopWavelength - self.__StartWavelength
        self.__Center = self.__StartWavelength + (self.__Span / 2.0)


    def GetStartWavelength(self):
        '''
        Get the start wavelength of the measurement span
        Wavelength is expressed in nm
        '''
        
        if not self.__Simulation:
            Command = "OSAFSSTARTWL?\n"
            Send(self.__Connexion, Command)
            self.__StartWavelength = float(Receive(self.__Connexion)[:-1])

        return self.__StartWavelength


    def SetStopWavelength(self, Wavelength):
        '''
        Set the stop wavelength of the measurement span
        Wavelength is expressed in nm
        '''
        from PyApex.Constantes import APXXXX_ERROR_ARGUMENT_TYPE      
        from PyApex.Errors import ApexError
        
        if not isinstance(Wavelength, (float, int)):
            raise ApexError(APXXXX_ERROR_ARGUMENT_TYPE, "Wavelength")
            sys.exit()

        if not self.__Simulation:
            Command = "OSAFSSTOPWL" + str(Wavelength) + "\n"
            Send(self.__Connexion, Command)

        self.__StopWavelength = Wavelength
        self.__Span = self.__StopWavelength - self.__StartWavelength
        self.__Center = self.__StartWavelength + (self.__Span / 2.0)


    def GetStopWavelength(self):
        '''
        Get the stop wavelength of the measurement span
        Wavelength is expressed in nm
        '''
        
        if not self.__Simulation:
            Command = "OSAFSSTOPWL?\n"
            Send(self.__Connexion, Command)
            self.__StopWavelength = float(Receive(self.__Connexion)[:-1])

        return self.__StopWavelength

        
    def SetSpan(self, Span):
        '''
        Set the wavelength measurement span
        Span is expressed in nm
        '''
        from PyApex.Constantes import APXXXX_ERROR_ARGUMENT_TYPE  
        from PyApex.Errors import ApexError
        
        if not isinstance(Span, (float, int)):
            raise ApexError(APXXXX_ERROR_ARGUMENT_TYPE, "Span")
            sys.exit()

        self.SetStartWavelength(self.__Center - Span / 2.0)
        self.SetStopWavelength(self.__Center - Span / 2.0)

        self.__StopWavelength = self.GetStopWavelength()
        self.__StartWavelength = self.GetStartWavelength()
        self.__Span = self.__StopWavelength - self.__StartWavelength
        self.__Center = self.__StartWavelength + (self.__Span / 2.0)

        
    def GetSpan(self):
        '''
        Get the wavelength measurement span
        Span is expressed in nm
        '''
        
        self.__StopWavelength = self.GetStopWavelength()
        self.__StartWavelength = self.GetStartWavelength()

        return self.__StopWavelength - self.__StartWavelength

        
    def SetCenter(self, Center):
        '''
        Set the wavelength measurement center
        Center is expressed in nm
        '''
        from PyApex.Constantes import APXXXX_ERROR_ARGUMENT_TYPE
        from PyApex.Errors import ApexError
        
        if not isinstance(Center, (float, int)):
            raise ApexError(APXXXX_ERROR_ARGUMENT_TYPE, "Center")
            sys.exit()

        self.SetStartWavelength(Center - self.__Span / 2.0)
        self.SetStopWavelength(Center - self.__Span / 2.0)

        self.__StopWavelength = self.GetStopWavelength()
        self.__StartWavelength = self.GetStartWavelength()
        self.__Span = self.__StopWavelength - self.__StartWavelength
        self.__Center = self.__StartWavelength + (self.__Span / 2.0)

        
    def GetCenter(self):
        '''
        Get the wavelength measurement center
        Center is expressed in nm
        '''
        
        self.__StopWavelength = self.__GetStopWavelength()
        self.__StartWavelength = self.__GetStartWavelength()

        return (self.__StopWavelength + self.__StartWavelength) / 2.0
        
    
    def SetOSAMode(self, Mode = "Sensitive"):
        '''
        Set the OSA Fast-Sweep mode (Fast or High-Sensitivity)
        Mode can be a string or an integer :
            - Mode = 1 or "Fast" : OSA Fast-Sweep will run in fast mode
            - Mode = 2 or "Sensitive" : OSA Fast-Sweep will run in high-sensitivity mode (default)
        '''
        from PyApex.Constantes import APXXXX_ERROR_ARGUMENT_TYPE
        from PyApex.Errors import ApexError
        
        if isinstance(Mode, (str)):
            if str(Mode).lower() == "fast":
                Mode = 1
            else:
                Mode = 2
        elif isinstance(Mode, (int, float)):
            if Mode != 2:
                Mode = 1
        else:
            raise ApexError(APXXXX_ERROR_ARGUMENT_TYPE, "Mode")
            sys.exit()
        
        if not self.__Simulation:
            Command = "OSAFSMODE" + str(Mode) + "\n"
            Send(self.__Connexion, Command)
        
        self.__Mode = Mode
    
    
    def GetOSAMode(self, Type = 'd'):
        '''
        Return the OSA Fast-Sweep mode (Fast or High-Sensitivity)
        if Type = 'd' (default), return a digit :
            - 1 for Fast
            - 2 for Sensitive
        if Type = 's', return a string :
            - "Fast" for Fast
            - "Sensitive" for High-Sensitivity
        '''
        from PyApex.Constantes import APXXXX_ERROR_ARGUMENT_TYPE
        from PyApex.Errors import ApexError
        
        if not isintance(Type, (str)):
            raise ApexError(APXXXX_ERROR_ARGUMENT_TYPE, "Type")
            sys.exit()
            
        if not self.__Simulation:
            Command = "OSAFSMODE?\n"
            Send(self.__Connexion, Command)
            self.__Mode = int(Receive(self.__Connexion)[:-1])
        
        if str(Type).lower() == 's':
            if self.__Mode == 1:
                return "Fast"
            elif self.__Mode == 2:
                return "Sensitive"
            else:
                return "Unknown Mode"
        else:
            return self.__Mode
    
    
    def Run(self, Type="single"):
        '''
        Run a measurement with the OSA Fast-Sweep
        If Type is
            - "single" or 1, a single measurement is running (default)
            - "repeat" or 2, a repeat measurement is running
        '''
        from PyApex.Errors import ApexError
        
        
        if isinstance(Type, str):                  
            if Type.lower() == "repeat":
                Command = "OSAFSRUN2\n"
            else:
                Command = "OSAFSRUN1\n"
        elif isinstance(Type, (int, float)): 
            if Type == 2:
                Command = "OSAFSRUN2\n"
            else:
                Command = "OSAFSRUN1\n"
        else:
            raise ApexError(APXXXX_ERROR_ARGUMENT_TYPE, "Type")
            sys.exit()
        
        if not self.__Simulation:
            Send(self.__Connexion, Command)
    
    
    def Stop(self):
        '''
        Stop a 'repeat' measurement on the OSA Fast-Sweep
        '''
        if not self.__Simulation:
            Command = "OSAFSSTOP\n"
            Send(self.__Connexion, Command)
    
    
    def GetNPoints(self, TraceNumber = 1):
        '''
        Get the number of points for the specified trace on the OSA Fast-Sweep
        TraceNumber is an integer between 1 (default) and 6
        '''
        from PyApex.Constantes import APXXXX_ERROR_ARGUMENT_TYPE, APXXXX_ERROR_ARGUMENT_VALUE
        from PyApex.Errors import ApexError
        from random import randint
        
        if not isinstance(TraceNumber, (int)):
            raise ApexError(APXXXX_ERROR_ARGUMENT_TYPE, "TraceNumber")
            sys.exit()
        
        if TraceNumber < 0 or TraceNumber > 6:
            raise ApexError(APXXXX_ERROR_ARGUMENT_VALUE, "TraceNumber")
            sys.exit()
        
        if self.__Simulation:
            NPoints = randint(400, 600)
        else:
            Command = "OSAFSPOINTS" + str(int(TraceNumber)) + "\n"
            Send(self.__Connexion, Command)
            try:
                NPoints = int(Receive(self.__Connexion)[:-1])
            except:
                NPoints = 0

        return NPoints
    
    
    def GetData(self, Scale="log", TraceNumber=1):
        '''
        Get the spectrum data of a measurement on the OSA Fast-Sweep
        returns a 2D list [Y-axis Data, X-Axis Data]
        Scale is a string which can be :
            - "log" : get the Y-Axis Data in dBm (default)
            - "lin" : get the Y-Axis Data in mW
        TraceNumber is an integer between 1 (default) and 6
        '''
        from PyApex.Constantes import APXXXX_ERROR_ARGUMENT_TYPE, APXXXX_ERROR_ARGUMENT_VALUE 
        from PyApex.Errors import ApexError
        from random import random
        
        if not isinstance(Scale, str):
            raise ApexError(APXXXX_ERROR_ARGUMENT_TYPE, "Scale")
            sys.exit()
            
        if not isinstance(TraceNumber, (int, float)):
            raise ApexError(APXXXX_ERROR_ARGUMENT_TYPE, "TraceNumber")
            sys.exit()
        
        if TraceNumber <= 0 or TraceNumber > 6:
            raise ApexError(APXXXX_ERROR_ARGUMENT_VALUE, "TraceNumber")
            sys.exit()
        
        NPoints = self.GetNPoints()
        if not self.__Simulation:
            YData = []
            XData = []
            
            if Scale.lower() == "lin":
                Command = "OSAFSDATAL" + str(int(TraceNumber)) + "\n"
            else:
                Command = "OSAFSDATAD" + str(int(TraceNumber)) + "\n"
            Send(self.__Connexion, Command)
            YStr = Receive(self.__Connexion, 20 * NPoints)[:-1]
            print(YStr)
            YStr = YStr.split(" ")
            print(YStr)
            for s in YStr:
                try:
                    YData.append(float(s))
                except:
                    YData.append(0.0)
                
            Command = "OSAFSDATAWL" + str(int(TraceNumber)) + "\n"
            Send(self.__Connexion, Command)
            XStr = Receive(self.__Connexion, 20 * NPoints)[:-1]
            print(XStr)
            XStr = XStr.split(" ")
            print(XStr)
            for s in XStr:
                try:
                    XData.append(float(s))
                except:
                    XData.append(0.0)
        else:
            YData = []
            XData = []
            DeltaX = (self.__StopWavelength - self.__StartWavelength) / NPoints
            for i in range(0, NPoints):
                if Scale.lower() == "lin":
                    YData.append(10.0 * random())
                else:
                    YData.append(60.0 * random() - 50.0)
                XData.append(self.__StartWavelength + i * DeltaX)
                
        return [YData, XData]
    
    