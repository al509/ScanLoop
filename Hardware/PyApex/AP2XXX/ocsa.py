from PyApex.Common import Send, Receive, ReceiveUntilChar
import sys


class OCSA():


    def __init__(self, Equipment, Simulation=False):
        '''
        Constructor of a Heterodyne OCSA equipment.
        Equipment is the AP2XXX class of the equipment
        Simulation is a boolean to indicate to the program if it has to run in simulation mode or not
        '''
        from PyApex.Constantes import AP2XXX_WLMIN, AP2XXX_WLMAX   
        
        self.__Connexion = Equipment.Connexion
        self.__Simulation = Simulation
        self.__ID = Equipment.GetID()
        self.__Type = self.GetType()
        
        # Variables and constants of the equipment
        self.__OpticalClockRecovery = 0
        self.__DoubleScan = 1
        self.__ControlModeShift = 0
        self.__StartWavelength = AP2XXX_WLMIN
        self.__StopWavelength = AP2XXX_WLMAX
        self.__Span = AP2XXX_WLMAX - AP2XXX_WLMIN
        self.__Center = AP2XXX_WLMIN + (self.__Span / 2)
        self.__ClockFrequency = 0.1 # 100 MHz
        self.__PatternLength = 2**7 - 1 # 127 symbols
        self.__BaudRate = self.__ClockFrequency * self.__PatternLength # 12.7 GHz
        self.__ValidScreensMode = [1, 2, 3, 4, 6, 10]
        self.__ValidScreenType = ["spectrum power", "spectrum phase", "temporal power", 
                                  "temporal phase", "temporal chirp", "temporal alpha",
                                  "constellation", "eye power", "eye phase"]
        self.__ValidPolarType = ["1+2", "1", "2"]
        self.__NPointsFFT = 4096
        self.__ValidScaleUnits = [0 , 1]
        self.__ScaleXUnit = 1
        self.__ScaleYUnit = 1
        self.__Validtracenumbers = [0 , 1 , 2 , 3 , 4 , 5 , 6]
        self.__tracenumber = 1
        self.__NAverage = 5


    def __str__(self):
        '''
        Return the equipment type and the AP2XXX ID
        '''
        return "Heterodyne OCSA " + str(self.__ID)


    def GetType(self):
        '''
        Return the type of the OSA. For example "AP2061" for an AP2061
        '''
        from PyApex.Errors import ApexError
        import re
        
        Type = self.__ID.split("/")[1]
        Type = "AP" + Type
        return Type


    def SetOpticalClockRecovery(self, Enable):
        '''
        Set the status of the optical clock recovery option
        Enable is boolean or integer which can be:
            - True or 1: the option is enabled
            - False or 0: the option is disabled
        '''
        from PyApex.Constantes import APXXXX_ERROR_ARGUMENT_TYPE, APXXXX_ERROR_ARGUMENT_VALUE        
        from PyApex.Errors import ApexError

        if not isinstance(Enable, (bool, int)):
            raise ApexError(APXXXX_ERROR_ARGUMENT_TYPE, "Enable")
            sys.exit()

        if Enable:
            Enable = 1
        else:
            Enable = 0

        if not self.__Simulation:
            Command = "CSPOCRECOVERY" + str(Enable) + "\n"
            Send(self.__Connexion, Command)

        self.__OpticalClockRecovery = Enable


    def GetOpticalClockRecovery(self):
        '''
        Get the status of the optical clock recovery option
        This function returns a boolean which can be:
            - True: the option is enabled
            - False: the option is disabled
        '''
        
        if not self.__Simulation:
            Command = "CSPOCRECOVERY?\n"
            Send(self.__Connexion, Command)
            try:
                self.__OpticalClockRecovery = int(Receive(self.__Connexion)[:-1])
            except:
                pass

        if self.__OpticalClockRecovery:
            return True
        else:
            return False


    def SetDoubleScan(self, Enable):
        '''
        Set the status of the double scan option
        Enable is boolean or integer which can be:
            - True or 1: the option is enabled
            - False or 0: the option is disabled
        '''
        from PyApex.Constantes import APXXXX_ERROR_ARGUMENT_TYPE, APXXXX_ERROR_ARGUMENT_VALUE        
        from PyApex.Errors import ApexError

        if not isinstance(Enable, (bool, int)):
            raise ApexError(APXXXX_ERROR_ARGUMENT_TYPE, "Enable")
            sys.exit()

        if Enable:
            Enable = 1
        else:
            Enable = 0

        if not self.__Simulation:
            Command = "CSPDOUBLESCAN" + str(Enable) + "\n"
            Send(self.__Connexion, Command)

        self.__DoubleScan = Enable


    def GetDoubleScan(self):
        '''
        Get the status of the double scan option
        This function returns a boolean which can be:
            - True: the option is enabled
            - False: the option is disabled
        '''
        
        if not self.__Simulation:
            Command = "CSPDOUBLESCAN?\n"
            Send(self.__Connexion, Command)
            try:
                self.__DoubleScan = int(Receive(self.__Connexion)[:-1])
            except:
                pass

        if self.__DoubleScan:
            return True
        else:
            return False


    def SetControlModeShift(self, Enable):
        '''
        Set the status of the control mode shift option
        Enable is boolean or integer which can be:
            - True or 1: the option is enabled
            - False or 0: the option is disabled
        '''
        from PyApex.Constantes import APXXXX_ERROR_ARGUMENT_TYPE, APXXXX_ERROR_ARGUMENT_VALUE        
        from PyApex.Errors import ApexError

        if not isinstance(Enable, (bool, int)):
            raise ApexError(APXXXX_ERROR_ARGUMENT_TYPE, "Enable")
            sys.exit()

        if Enable:
            Enable = 1
        else:
            Enable = 0

        if not self.__Simulation:
            Command = "CSPCTRLMODESHIFT" + str(Enable) + "\n"
            Send(self.__Connexion, Command)

        self.__ControlModeShift = Enable


    def GetControlModeShift(self):
        '''
        Get the status of the control mode shift option
        This function returns a boolean which can be:
            - True: the option is enabled
            - False: the option is disabled
        '''
        
        if not self.__Simulation:
            Command = "CSPCTRLMODESHIFT?\n"
            Send(self.__Connexion, Command)
            try:
                self.__ControlModeShift = int(Receive(self.__Connexion)[:-1])
            except:
                pass

        if self.__ControlModeShift:
            return True
        else:
            return False


    def SetClockFrequency(self, Frequency):
        '''
        Set the frequency of the pattern clock (repetition frequency)
        Frequency is expressed in GHz
        '''
        from PyApex.Constantes import APXXXX_ERROR_ARGUMENT_TYPE, APXXXX_ERROR_ARGUMENT_VALUE        
        from PyApex.Errors import ApexError
        
        if not isinstance(Frequency, (float, int)):
            raise ApexError(APXXXX_ERROR_ARGUMENT_TYPE, "Frequency")
            sys.exit()

        if not self.__Simulation:
            Command = "CSPCLKFREQ" + str(Frequency) + "\n"
            Send(self.__Connexion, Command)

        self.__ClockFrequency = Frequency


    def GetClockFrequency(self):
        '''
        Get the frequency of the pattern clock (repetition frequency)
        Frequency is expressed in GHz
        '''
        
        if not self.__Simulation:
            Command = "CSPCLKFREQ?\n"
            Send(self.__Connexion, Command)
            self.__ClockFrequency = float(Receive(self.__Connexion)[:-1])

        return self.__ClockFrequency
    
    
    def SetPatternLength(self, Length):
        '''
        Set the Length of the pattern (number of symbols)
        Length is an integer
        '''
        from PyApex.Constantes import APXXXX_ERROR_ARGUMENT_TYPE, APXXXX_ERROR_ARGUMENT_VALUE        
        from PyApex.Errors import ApexError
        
        if not isinstance(Length, (int)):
            raise ApexError(APXXXX_ERROR_ARGUMENT_TYPE, "Length")
            sys.exit()

        if not self.__Simulation:
            Command = "CSPPRBSLENGTH" + str(Length) + "\n"
            Send(self.__Connexion, Command)

        self.__PatternLength = Length
        self.__BaudRate = self.__ClockFrequency * self.__PatternLength


    def GetPatternLength(self):
        '''
        Get the Length of the pattern (number of symbols)
        The returned length is an integer representing the number of symbols in the pattern
        '''
        
        if not self.__Simulation:
            Command = "CSPPRBSLENGTH?\n"
            Send(self.__Connexion, Command)
            self.__PatternLength = int(Receive(self.__Connexion)[:-1])

        return self.__PatternLength
    
    
    def SetBaudRate(self, Rate):
        '''
        Set the baud rate of the modulation (number of symbols per second)
        Rate is expressed in GBaud
        '''
        from PyApex.Constantes import APXXXX_ERROR_ARGUMENT_TYPE, APXXXX_ERROR_ARGUMENT_VALUE        
        from PyApex.Errors import ApexError
        
        if not isinstance(Rate, (float, int)):
            raise ApexError(APXXXX_ERROR_ARGUMENT_TYPE, "Rate")
            sys.exit()

        if not self.__Simulation:
            Command = "CSPBAUDRATE" + str(Rate) + "\n"
            Send(self.__Connexion, Command)

        self.__BaudRate = Rate
        self.__PatternLength = self.__BaudRate / self.__ClockFrequency


    def GetBaudRate(self):
        '''
        Get the baud rate of the modulation (number of symbols per second)
        Rate is expressed in GBaud
        '''
        
        if not self.__Simulation:
            Command = "CSPBAUDRATE?\n"
            Send(self.__Connexion, Command)
            self.__BaudRate = float(Receive(self.__Connexion)[:-1])

        return self.__BaudRate
        
        
    def SetStartWavelength(self, Wavelength):
        '''
        Set the start wavelength of the measurement span
        Wavelength is expressed in nm
        '''
        from PyApex.Constantes import APXXXX_ERROR_ARGUMENT_TYPE, APXXXX_ERROR_ARGUMENT_VALUE        
        from PyApex.Errors import ApexError
        
        if not isinstance(Wavelength, (float, int)):
            raise ApexError(APXXXX_ERROR_ARGUMENT_TYPE, "Wavelength")
            sys.exit()

        if not self.__Simulation:
            Command = "CSPSTRTWL" + str(Wavelength) + "\n"
            Send(self.__Connexion, Command)

        self.__StartWavelength = Wavelength
        self.__Span = self.__StopWavelength - self.__StartWavelength
        self.__Center = self.__StartWavelength + (self.__Span / 2)


    def GetStartWavelength(self):
        '''
        Get the start wavelength of the measurement span
        Wavelength is expressed in nm
        '''
        
        if not self.__Simulation:
            Command = "CSPSTRTWL?\n"
            Send(self.__Connexion, Command)
            self.__StartWavelength = float(Receive(self.__Connexion)[:-1])

        return self.__StartWavelength


    def SetStartFrequency(self, Frequency):
        '''
        Set the start frequency of the measurement span
        Frequency is expressed in GHz
        '''
        from PyApex.Constantes import APXXXX_ERROR_ARGUMENT_TYPE, APXXXX_ERROR_ARGUMENT_VALUE
        from PyApex.Constantes import Celerity
        from PyApex.Errors import ApexError
        
        if not isinstance(Frequency, (float, int)):
            raise ApexError(APXXXX_ERROR_ARGUMENT_TYPE, "Frequency")
            sys.exit()

        if not self.__Simulation:
            Command = "CSPSTRTF" + str(Frequency) + "\n"
            Send(self.__Connexion, Command)
            
        self.__StartWavelength = Celerity / Frequency
        self.__Span = self.__StopWavelength - self.__StartWavelength
        self.__Center = self.__StartWavelength + (self.__Span / 2)


    def GetStartFrequency(self):
        '''
        Get the start frequency of the measurement span
        Frequency is expressed in GHz
        '''
        from PyApex.Constantes import Celerity
        
        if self.__Simulation:
            Frequency = Celerity / self.__StartWavelength 
        else:
            Command = "CSPSTRTF?\n"
            Send(self.__Connexion, Command)
            Frequency = float(Receive(self.__Connexion)[:-1])
            self.__StartWavelength = Celerity / Frequency

        return Frequency
        
        
    def SetStopWavelength(self, Wavelength):
        '''
        Set the stop wavelength of the measurement span
        Wavelength is expressed in nm
        '''
        from PyApex.Constantes import APXXXX_ERROR_ARGUMENT_TYPE, APXXXX_ERROR_ARGUMENT_VALUE        
        from PyApex.Errors import ApexError
        
        if not isinstance(Wavelength, (float, int)):
            raise ApexError(APXXXX_ERROR_ARGUMENT_TYPE, "Wavelength")
            sys.exit()

        if not self.__Simulation:
            Command = "CSPSTOPWL" + str(Wavelength) + "\n"
            Send(self.__Connexion, Command)

        self.__StopWavelength = Wavelength
        self.__Span = self.__StopWavelength - self.__StartWavelength
        self.__Center = self.__StartWavelength + (self.__Span / 2)


    def GetStopWavelength(self):
        '''
        Get the stop wavelength of the measurement span
        Wavelength is expressed in nm
        '''
        
        if not self.__Simulation:
            Command = "CSPSTOPWL?\n"
            Send(self.__Connexion, Command)
            self.__StopWavelength = float(Receive(self.__Connexion)[:-1])

        return self.__StopWavelength
    
    
    def SetStopFrequency(self, Frequency):
        '''
        Set the stop frequency of the measurement span
        Frequency is expressed in GHz
        '''
        from PyApex.Constantes import APXXXX_ERROR_ARGUMENT_TYPE, APXXXX_ERROR_ARGUMENT_VALUE
        from PyApex.Constantes import Celerity
        from PyApex.Errors import ApexError
        
        if not isinstance(Frequency, (float, int)):
            raise ApexError(APXXXX_ERROR_ARGUMENT_TYPE, "Frequency")
            sys.exit()

        if not self.__Simulation:
            Command = "CSPSTOPF" + str(Frequency) + "\n"
            Send(self.__Connexion, Command)
            
        self.__StopWavelength = Celerity / Frequency
        self.__Span = self.__StopWavelength - self.__StartWavelength
        self.__Center = self.__StartWavelength + (self.__Span / 2)


    def GetStopFrequency(self):
        '''
        Get the stop frequency of the measurement span
        Frequency is expressed in GHz
        '''
        from PyApex.Constantes import Celerity
        
        if self.__Simulation:
            Frequency = Celerity / self.__StopWavelength 
        else:
            Command = "CSPSTOPF?\n"
            Send(self.__Connexion, Command)
            Frequency = float(Receive(self.__Connexion)[:-1])
            self.__StopWavelength = Celerity / Frequency

        return Frequency

        
    def SetSpanWavelength(self, Span):
        '''
        Set the wavelength measurement span
        Span is expressed in nm
        '''
        from PyApex.Constantes import APXXXX_ERROR_ARGUMENT_TYPE, APXXXX_ERROR_ARGUMENT_VALUE   
        from PyApex.Errors import ApexError
        
        if not isinstance(Span, (float, int)):
            raise ApexError(APXXXX_ERROR_ARGUMENT_TYPE, "Span")
            sys.exit()

        if not self.__Simulation:
            Command = "CSPSPANWL" + str(Span) + "\n"
            Send(self.__Connexion, Command)

        self.__Span = Span
        self.__StopWavelength = self.__Center + (self.__Span / 2)
        self.__StartWavelength = self.__Center - (self.__Span / 2)

        
    def GetSpanWavelength(self):
        '''
        Get the wavelength measurement span
        Span is expressed in nm
        '''
        
        if not self.__Simulation:
            Command = "CSPSPANWL?\n"
            Send(self.__Connexion, Command)
            self.__Span = float(Receive(self.__Connexion)[:-1])

        return self.__Span

        
    def SetSpanFrequency(self, Span):
        '''
        Set the frequency measurement span
        Span is expressed in GHz
        '''
        from PyApex.Constantes import APXXXX_ERROR_ARGUMENT_TYPE, APXXXX_ERROR_ARGUMENT_VALUE
        from PyApex.Constantes import Celerity
        from PyApex.Errors import ApexError
        
        if not isinstance(Span, (float, int)):
            raise ApexError(APXXXX_ERROR_ARGUMENT_TYPE, "Span")
            sys.exit()

        if not self.__Simulation:
            Command = "CSPSPANF" + str(Span) + "\n"
            Send(self.__Connexion, Command)
        
        CenterF = Celerity / self.__Center
        self.__Span = Celerity * (Span / CenterF**2)
        self.__StopWavelength = self.__Center + (self.__Span / 2)
        self.__StartWavelength = self.__Center - (self.__Span / 2)


    def GetSpanFrequency(self):
        '''
        Get the frequency measurement span
        Span is expressed in GHz
        '''
        from PyApex.Constantes import Celerity
        
        if self.__Simulation:
            Span = Celerity / self.__StopWavelength 
        else:
            Command = "CSPSPANF?\n"
            Send(self.__Connexion, Command)
            Span = float(Receive(self.__Connexion)[:-1])
            CenterF = Celerity / self.__Center
            self.__Span = Celerity * (Span / CenterF**2)

        return Span
    
        
    def SetCenterWavelength(self, Center):
        '''
        Set the wavelength measurement center
        Center is expressed in nm
        '''
        from PyApex.Constantes import APXXXX_ERROR_ARGUMENT_TYPE, APXXXX_ERROR_ARGUMENT_VALUE 
        from PyApex.Errors import ApexError
        
        if not isinstance(Center, (float, int)):
            raise ApexError(APXXXX_ERROR_ARGUMENT_TYPE, "Center")
            sys.exit()

        if not self.__Simulation:
            Command = "CSPCTRWL" + str(Center) + "\n"
            Send(self.__Connexion, Command)

        self.__Center = Center
        self.__StopWavelength = self.__Center + (self.__Span / 2)
        self.__StartWavelength = self.__Center - (self.__Span / 2)

        
    def GetCenterWavelength(self):
        '''
        Get the wavelength measurement center
        Center is expressed in nm
        '''
        
        if not self.__Simulation:
            Command = "CSPCTRWL?\n"
            Send(self.__Connexion, Command)
            self.__Center = float(Receive(self.__Connexion)[:-1])

        return self.__Center

    
    def SetCenterFrequency(self, Center):
        '''
        Set the stop frequency of the measurement span
        Center is expressed in GHz
        '''
        from PyApex.Constantes import APXXXX_ERROR_ARGUMENT_TYPE, APXXXX_ERROR_ARGUMENT_VALUE
        from PyApex.Constantes import Celerity
        from PyApex.Errors import ApexError
        
        if not isinstance(Center, (float, int)):
            raise ApexError(APXXXX_ERROR_ARGUMENT_TYPE, "Center")
            sys.exit()

        if not self.__Simulation:
            Command = "CSPCTRF" + str(Center) + "\n"
            Send(self.__Connexion, Command)
            
        self.__Center = Celerity / Center
        self.__StopWavelength = self.__Center + (self.__Span / 2)
        self.__StartWavelength = self.__Center - (self.__Span / 2)


    def GetCenterFrequency(self):
        '''
        Get the stop frequency of the measurement span
        Frequency is expressed in GHz
        '''
        from PyApex.Constantes import Celerity
        
        if self.__Simulation:
            Center = Celerity / self.__StopWavelength 
        else:
            Command = "CSPCTRF?\n"
            Send(self.__Connexion, Command)
            Center = float(Receive(self.__Connexion)[:-1])
            self.__Center = Celerity / Center

        return Center
    
    
    def SetAveragingValue(self, Number):
        '''
        Set the number of sweeps to average before displaying
        Number is a positive integer. When Number = 1, there
        is no averaging.
        '''
        from PyApex.Constantes import APXXXX_ERROR_ARGUMENT_TYPE, APXXXX_ERROR_ARGUMENT_VALUE
        from PyApex.Errors import ApexError
        
        if not isinstance(Number, int):
            raise ApexError(APXXXX_ERROR_ARGUMENT_TYPE, "Number")
            sys.exit()
        
        if Number <= 0:
            raise ApexError(APXXXX_ERROR_ARGUMENT_VALUE, "Number")
            sys.exit()
        
        if not self.__Simulation:
            Command = "CSPAVERAGING" + str(Number) + "\n"
            Send(self.__Connexion, Command)
    
    
    def GetAveragingValue(self):
        '''
        Get the number of averaged sweeps before displaying
        When Number = 1, there is no averaging.
        '''
        
        if self.__Simulation:
            Averaging = 1
        else:
            Command = "CSPAVERAGING?\n"
            Send(self.__Connexion, Command)
            Averaging = int(Receive(self.__Connexion)[:-1])

        return Averaging
    
    
    def SetContinueAveraging(self, Enable):
        '''
        Enables the continue averaging option
        Enable is a boolean:
            - True: the option is enabled
            - False: the option is disabled
        '''
        
        Command = "CSPCONTINUEAVRG"
        if Enable == True:
            Command += "1\n"
        else:
            Command += "0\n"
        
        if not self.__Simulation:
            Send(self.__Connexion, Command)
    
    
    def GetContinueAveraging(self):
        '''
        Get the value of the continue averaging option
        '''
        
        if self.__Simulation:
            Averaging = 0
        else:
            Command = "CSPCONTINUEAVRG?\n"
            Send(self.__Connexion, Command)
            Averaging = int(Receive(self.__Connexion)[:-1])

        return Averaging
    
    
    def GetFilterBandWidth(self):
        '''
        Get the filter bandwidth of the O.C.S.A. mode
        Bandwidth is expressed in MHz
        '''
        
        if self.__Simulation:
            Bandwidth = 20.0 
        else:
            Command = "CSPFILBW?\n"
            Send(self.__Connexion, Command)
            Bandwidth = float(Receive(self.__Connexion)[:-1])

        return Bandwidth
    
    
    def GetSweepSpeed(self, Unit = "nm"):
        '''
        Get the local oscillator sweep speed in the O.C.S.A. mode
        Sweep speed is expressed in nm/s or in GHz/s depending on 'Unit':
            - Unit = "nm": sweep speed is expressed in nm/s
            - Unit = "GHz": sweep speed is expressed in GHz/s
        '''
        from PyApex.Constantes import APXXXX_ERROR_ARGUMENT_TYPE, APXXXX_ERROR_ARGUMENT_VALUE
        from PyApex.Errors import ApexError
        from PyApex.Constantes import Celerity
        
        if not isinstance(Unit, str):
            raise ApexError(APXXXX_ERROR_ARGUMENT_TYPE, "Unit")
            sys.exit() 
        
        if self.__Simulation:
            SweepSpeed = 3000.0 
        else:
            Command = "CSPSWPSPEED?\n"
            Send(self.__Connexion, Command)
            SweepSpeed = float(Receive(self.__Connexion)[:-1])
        
        if str(Unit).lower() == "nm":
            SweepSpeed = -(1550.0**2 * SweepSpeed) / (Celerity)

        return SweepSpeed
    
    
    def SetCarrierMode(self, Mode = 1, TraceNumber = 0):
        '''
        Set the carrier mode
        Mode can be an integer or a string:
            - 0 or "manual": Carrier mode is set to "Manual mode"
            - 1 or "highest": Carrier mode is set to "Highest mode" (default)
            - 2 or "auto": Carrier mode is set to "Auto mode"
        TraceNumber is an integer between 0 and 6:
            - 0: Carrier mode is set for all traces (default)
            - 1 to 6: Carrier mode is set to the specified trace
        '''
        from PyApex.Constantes import APXXXX_ERROR_ARGUMENT_TYPE, APXXXX_ERROR_ARGUMENT_VALUE
        from PyApex.Errors import ApexError
        
        if not isinstance(Mode, (int, str)):
            raise ApexError(APXXXX_ERROR_ARGUMENT_TYPE, "Mode")
            sys.exit()
        
        if not isinstance(TraceNumber, int):
            raise ApexError(APXXXX_ERROR_ARGUMENT_TYPE, "TraceNumber")
            sys.exit()
        
        if not TraceNumber in self.__Validtracenumbers:
            raise ApexError(APXXXX_ERROR_ARGUMENT_VALUE, "TraceNumber")
            sys.exit()
        
        if isinstance(Mode, str):
            if Mode.lower() == "manual":
                Mode = 0
            elif Mode.lower() == "auto":
                Mode = 2
            else:
                Mode = 1
        
        if isinstance(Mode, int):
            if Mode < 0 or Mode > 2:
                raise ApexError(APXXXX_ERROR_ARGUMENT_VALUE, "Mode")
                sys.exit()
        
        if not self.__Simulation:
            Command = "CSPCARRIERMODE" + str(TraceNumber) + "," + str(Mode) + "\n"
            Send(self.__Connexion, Command)
    
    
    def GetCarrierMode(self, TraceNumber = 0):
        '''
        Get the carrier mode
        Mode is a string:
            - "manual": Carrier mode is in the "Manual mode"
            - "highest": Carrier mode is in the "Highest mode"
            - "auto": Carrier mode is in the "Auto mode"
        TraceNumber is an integer between 0 and 6:
            - 0: Carrier mode is set for all traces (default)
            - 1 to 6: Carrier mode is set to the specified trace
        '''
        from PyApex.Constantes import APXXXX_ERROR_ARGUMENT_TYPE, APXXXX_ERROR_ARGUMENT_VALUE
        from PyApex.Errors import ApexError
        
        if not isinstance(TraceNumber, int):
            raise ApexError(APXXXX_ERROR_ARGUMENT_TYPE, "TraceNumber")
            sys.exit()
        
        if not TraceNumber in self.__Validtracenumbers:
            raise ApexError(APXXXX_ERROR_ARGUMENT_VALUE, "TraceNumber")
            sys.exit()
        
        if self.__Simulation:
            Mode = 1
        else:
            Command = "CSPCARRIERMODE" + str(TraceNumber) + "?\n"
            Send(self.__Connexion, Command)
            Mode = int(Receive(self.__Connexion)[:-1])
        
        if Mode == 0:
            Mode = "manual"
        elif Mode == 1:
            Mode = "highest"
        elif Mode == 2:
            Mode = "auto"
        
        return Mode
    
    
    def SetCarrierWavelength(self, Carrier, TraceNumber = 0):
        '''
        Set the carrier wavelength of the signal
        Carrier is expressed in nm
        TraceNumber is an integer between 0 and 6:
            - 0: Carrier mode is set for all traces (default)
            - 1 to 6: Carrier mode is set to the specified trace
        '''
        from PyApex.Constantes import APXXXX_ERROR_ARGUMENT_TYPE, APXXXX_ERROR_ARGUMENT_VALUE 
        from PyApex.Errors import ApexError
        
        if not isinstance(Carrier, (float, int)):
            raise ApexError(APXXXX_ERROR_ARGUMENT_TYPE, "Carrier")
            sys.exit()
        
        if not isinstance(TraceNumber, int):
            raise ApexError(APXXXX_ERROR_ARGUMENT_TYPE, "TraceNumber")
            sys.exit()
        
        if not TraceNumber in self.__Validtracenumbers:
            raise ApexError(APXXXX_ERROR_ARGUMENT_VALUE, "TraceNumber")
            sys.exit()

        if not self.__Simulation:
            Command = "CSPCARRIERWL" + str(TraceNumber) + "," + str(Carrier) + "\n"
            Send(self.__Connexion, Command)

        
    def GetCarrierWavelength(self, TraceNumber = 0):
        '''
        Get the carrier wavelength of the signal
        Carrier is expressed in nm
        TraceNumber is an integer between 0 and 6:
            - 0: Carrier mode is set for all traces (default)
            - 1 to 6: Carrier mode is set to the specified trace
        '''
        from PyApex.Constantes import APXXXX_ERROR_ARGUMENT_TYPE, APXXXX_ERROR_ARGUMENT_VALUE
        from PyApex.Errors import ApexError
        
        if not isinstance(TraceNumber, int):
            raise ApexError(APXXXX_ERROR_ARGUMENT_TYPE, "TraceNumber")
            sys.exit()
        
        if not TraceNumber in self.__Validtracenumbers:
            raise ApexError(APXXXX_ERROR_ARGUMENT_VALUE, "TraceNumber")
            sys.exit()
        
        if self.__Simulation:
            Carrier = self.__Center
        if not self.__Simulation:
            Command = "CSPCARRIERWL" + str(TraceNumber) + "?\n"
            Send(self.__Connexion, Command)
            Carrier = float(Receive(self.__Connexion)[:-1])

        return Carrier

    
    def SetCarrierFrequency(self, Carrier, TraceNumber = 0):
        '''
        Set the carrier frequency of the signal
        Carrier is expressed in GHz
        TraceNumber is an integer between 0 and 6:
            - 0: Carrier mode is set for all traces (default)
            - 1 to 6: Carrier mode is set to the specified trace
        '''
        from PyApex.Constantes import APXXXX_ERROR_ARGUMENT_TYPE, APXXXX_ERROR_ARGUMENT_VALUE
        from PyApex.Constantes import Celerity
        from PyApex.Errors import ApexError
        
        if not isinstance(Carrier, (float, int)):
            raise ApexError(APXXXX_ERROR_ARGUMENT_TYPE, "Carrier")
            sys.exit()
        
        if not isinstance(TraceNumber, int):
            raise ApexError(APXXXX_ERROR_ARGUMENT_TYPE, "TraceNumber")
            sys.exit()
        
        if not TraceNumber in self.__Validtracenumbers:
            raise ApexError(APXXXX_ERROR_ARGUMENT_VALUE, "TraceNumber")
            sys.exit()

        if not self.__Simulation:
            Command = "CSPCARRIERF" + str(TraceNumber) + "," + str(Carrier) + "\n"
            Send(self.__Connexion, Command)


    def GetCarrierFrequency(self, TraceNumber = 0):
        '''
        Get the carrier frequency of the signal
        Carrier is expressed in GHz
        TraceNumber is an integer between 0 and 6:
            - 0: Carrier mode is set for all traces (default)
            - 1 to 6: Carrier mode is set to the specified trace
        '''
        from PyApex.Constantes import Celerity
        from PyApex.Constantes import APXXXX_ERROR_ARGUMENT_TYPE, APXXXX_ERROR_ARGUMENT_VALUE
        from PyApex.Errors import ApexError
        
        if not isinstance(TraceNumber, int):
            raise ApexError(APXXXX_ERROR_ARGUMENT_TYPE, "TraceNumber")
            sys.exit()
        
        if not TraceNumber in self.__Validtracenumbers:
            raise ApexError(APXXXX_ERROR_ARGUMENT_VALUE, "TraceNumber")
            sys.exit()
        
        if self.__Simulation:
            Carrier = Celerity / self.__Center 
        else:
            Command = "CSPCARRIERF" + str(TraceNumber) + "?\n"
            Send(self.__Connexion, Command)
            Carrier = float(Receive(self.__Connexion)[:-1])

        return Carrier
    
    
    def SetNbModesBeforeCarrier(self, Number, TraceNumber = 0):
        '''
        Set the number of modes before the carrier (in frequency unit)
        Number is a positive integer
        TraceNumber is an integer between 0 and 6:
            - 0: Carrier mode is set for all traces (default)
            - 1 to 6: Carrier mode is set to the specified trace
        '''
        from PyApex.Constantes import APXXXX_ERROR_ARGUMENT_TYPE, APXXXX_ERROR_ARGUMENT_VALUE
        from PyApex.Errors import ApexError
        
        if not isinstance(Number, int):
            raise ApexError(APXXXX_ERROR_ARGUMENT_TYPE, "Number")
            sys.exit()
        
        if Number <= 0:
            raise ApexError(APXXXX_ERROR_ARGUMENT_VALUE, "Number")
            sys.exit()
        
        if not isinstance(TraceNumber, int):
            raise ApexError(APXXXX_ERROR_ARGUMENT_TYPE, "TraceNumber")
            sys.exit()
        
        if not TraceNumber in self.__Validtracenumbers:
            raise ApexError(APXXXX_ERROR_ARGUMENT_VALUE, "TraceNumber")
            sys.exit()
        
        if not self.__Simulation:
            Command = "CSPNBMODEBEFORE" + str(TraceNumber) + "," + str(Number) + "\n"
            Send(self.__Connexion, Command)
    
    
    def GetNbModesBeforeCarrier(self, TraceNumber = 0):
        '''
        Get the number of modes before the carrier (in frequency unit)
        TraceNumber is an integer between 0 and 6:
            - 0: Carrier mode is set for all traces (default)
            - 1 to 6: Carrier mode is set to the specified trace
        '''
        from PyApex.Constantes import APXXXX_ERROR_ARGUMENT_TYPE, APXXXX_ERROR_ARGUMENT_VALUE
        from PyApex.Errors import ApexError
        
        if not isinstance(TraceNumber, int):
            raise ApexError(APXXXX_ERROR_ARGUMENT_TYPE, "TraceNumber")
            sys.exit()
        
        if not TraceNumber in self.__Validtracenumbers:
            raise ApexError(APXXXX_ERROR_ARGUMENT_VALUE, "TraceNumber")
            sys.exit()
        
        if self.__Simulation:
            Number = 128
        else:
            Command = "CSPNBMODEBEFORE" + str(TraceNumber) + "?\n"
            Send(self.__Connexion, Command)
            Number = int(Receive(self.__Connexion)[:-1])

        return Number
    
    
    def SetFrequencyModesBeforeCarrier(self, Frequency, TraceNumber = 0):
        '''
        Set the frequency range of modes before the carrier (in frequency unit)
        Frequency is expressed in GHz
        TraceNumber is an integer between 0 and 6:
            - 0: Carrier mode is set for all traces (default)
            - 1 to 6: Carrier mode is set to the specified trace
        '''
        from PyApex.Constantes import APXXXX_ERROR_ARGUMENT_TYPE, APXXXX_ERROR_ARGUMENT_VALUE
        from PyApex.Constantes import Celerity
        from PyApex.Errors import ApexError
        
        if not isinstance(Frequency, (float, int)):
            raise ApexError(APXXXX_ERROR_ARGUMENT_TYPE, "Frequency")
            sys.exit()
        
        if not isinstance(TraceNumber, int):
            raise ApexError(APXXXX_ERROR_ARGUMENT_TYPE, "TraceNumber")
            sys.exit()
        
        if not TraceNumber in self.__Validtracenumbers:
            raise ApexError(APXXXX_ERROR_ARGUMENT_VALUE, "TraceNumber")
            sys.exit()

        if not self.__Simulation:
            Command = "CSPMODEBEFOREF" + str(TraceNumber) + "," + str(Frequency) + "\n"
            Send(self.__Connexion, Command)
    
    
    def GetFrequencyModesBeforeCarrier(self, TraceNumber = 0):
        '''
        Get the frequency range of modes before the carrier (in frequency unit)
        Frequency is expressed in GHz
        TraceNumber is an integer between 0 and 6:
            - 0: Carrier mode is set for all traces (default)
            - 1 to 6: Carrier mode is set to the specified trace
        '''
        from PyApex.Constantes import Celerity
        from PyApex.Constantes import APXXXX_ERROR_ARGUMENT_TYPE, APXXXX_ERROR_ARGUMENT_VALUE
        from PyApex.Errors import ApexError
        
        if not isinstance(TraceNumber, int):
            raise ApexError(APXXXX_ERROR_ARGUMENT_TYPE, "TraceNumber")
            sys.exit()
        
        if not TraceNumber in self.__Validtracenumbers:
            raise ApexError(APXXXX_ERROR_ARGUMENT_VALUE, "TraceNumber")
            sys.exit()
        
        if self.__Simulation:
            Frequency = Celerity / self.__StopWavelength 
        else:
            Command = "CSPMODEBEFOREF" + str(TraceNumber) + "?\n"
            Send(self.__Connexion, Command)
            Frequency = float(Receive(self.__Connexion)[:-1])

        return Frequency
    
    
    def SetNbModesAfterCarrier(self, Number, TraceNumber = 0):
        '''
        Set the number of modes after the carrier (in frequency unit)
        Number is a positive integer
        TraceNumber is an integer between 0 and 6:
            - 0: Carrier mode is set for all traces (default)
            - 1 to 6: Carrier mode is set to the specified trace
        '''
        from PyApex.Constantes import APXXXX_ERROR_ARGUMENT_TYPE, APXXXX_ERROR_ARGUMENT_VALUE
        from PyApex.Errors import ApexError
        
        if not isinstance(Number, int):
            raise ApexError(APXXXX_ERROR_ARGUMENT_TYPE, "Number")
            sys.exit()
        
        if Number <= 0:
            raise ApexError(APXXXX_ERROR_ARGUMENT_VALUE, "Number")
            sys.exit()
        
        if not isinstance(TraceNumber, int):
            raise ApexError(APXXXX_ERROR_ARGUMENT_TYPE, "TraceNumber")
            sys.exit()
        
        if not TraceNumber in self.__Validtracenumbers:
            raise ApexError(APXXXX_ERROR_ARGUMENT_VALUE, "TraceNumber")
            sys.exit()
        
        if not self.__Simulation:
            Command = "CSPNBMODEAFTER" + str(TraceNumber) + "," + str(Number) + "\n"
            Send(self.__Connexion, Command)
    
    
    def GetNbModesAfterCarrier(self, TraceNumber = 0):
        '''
        Get the number of modes before the carrier (in frequency unit)
        TraceNumber is an integer between 0 and 6:
            - 0: Carrier mode is set for all traces (default)
            - 1 to 6: Carrier mode is set to the specified trace
        '''
        from PyApex.Constantes import APXXXX_ERROR_ARGUMENT_TYPE, APXXXX_ERROR_ARGUMENT_VALUE
        from PyApex.Errors import ApexError
        
        if not isinstance(TraceNumber, int):
            raise ApexError(APXXXX_ERROR_ARGUMENT_TYPE, "TraceNumber")
            sys.exit()
        
        if not TraceNumber in self.__Validtracenumbers:
            raise ApexError(APXXXX_ERROR_ARGUMENT_VALUE, "TraceNumber")
            sys.exit()
        
        if self.__Simulation:
            Number = 128
        else:
            Command = "CSPNBMODEAFTER" + str(TraceNumber) + "?\n"
            Send(self.__Connexion, Command)
            Number = int(Receive(self.__Connexion)[:-1])

        return Number
    
    
    def SetFrequencyModesAfterCarrier(self, Frequency, TraceNumber = 0):
        '''
        Set the frequency range of modes after the carrier (in frequency unit)
        Frequency is expressed in GHz
        TraceNumber is an integer between 0 and 6:
            - 0: Carrier mode is set for all traces (default)
            - 1 to 6: Carrier mode is set to the specified trace
        '''
        from PyApex.Constantes import APXXXX_ERROR_ARGUMENT_TYPE, APXXXX_ERROR_ARGUMENT_VALUE
        from PyApex.Constantes import Celerity
        from PyApex.Errors import ApexError
        
        if not isinstance(Frequency, (float, int)):
            raise ApexError(APXXXX_ERROR_ARGUMENT_TYPE, "Frequency")
            sys.exit()
        
        if not isinstance(TraceNumber, int):
            raise ApexError(APXXXX_ERROR_ARGUMENT_TYPE, "TraceNumber")
            sys.exit()
        
        if not TraceNumber in self.__Validtracenumbers:
            raise ApexError(APXXXX_ERROR_ARGUMENT_VALUE, "TraceNumber")
            sys.exit()

        if not self.__Simulation:
            Command = "CSPMODEAFTERF" + str(TraceNumber) + "," + str(Frequency) + "\n"
            Send(self.__Connexion, Command)
    
    
    def GetFrequencyModesAfterCarrier(self, TraceNumber = 0):
        '''
        Get the frequency range of modes after the carrier (in frequency unit)
        Frequency is expressed in GHz
        TraceNumber is an integer between 0 and 6:
            - 0: Carrier mode is set for all traces (default)
            - 1 to 6: Carrier mode is set to the specified trace
        '''
        from PyApex.Constantes import APXXXX_ERROR_ARGUMENT_TYPE, APXXXX_ERROR_ARGUMENT_VALUE
        from PyApex.Constantes import Celerity
        from PyApex.Errors import ApexError
        
        if not isinstance(TraceNumber, int):
            raise ApexError(APXXXX_ERROR_ARGUMENT_TYPE, "TraceNumber")
            sys.exit()
        
        if not TraceNumber in self.__Validtracenumbers:
            raise ApexError(APXXXX_ERROR_ARGUMENT_VALUE, "TraceNumber")
            sys.exit()
        
        if self.__Simulation:
            Frequency = Celerity / self.__StartWavelength 
        else:
            Command = "CSPMODEAFTERF" + str(TraceNumber) + "?\n"
            Send(self.__Connexion, Command)
            Frequency = float(Receive(self.__Connexion)[:-1])

        return Frequency
    
    
    def SetNbPoints(self, Number, TraceNumber = 0):
        '''
        Set the number of points for the FFT operation
        Number is a positive integer
        TraceNumber is an integer between 0 and 6:
            - 0: Carrier mode is set for all traces (default)
            - 1 to 6: Carrier mode is set to the specified trace
        '''
        from PyApex.Constantes import APXXXX_ERROR_ARGUMENT_TYPE, APXXXX_ERROR_ARGUMENT_VALUE
        from PyApex.Errors import ApexError
        
        if not isinstance(Number, int):
            raise ApexError(APXXXX_ERROR_ARGUMENT_TYPE, "Number")
            sys.exit()
        
        if Number <= 0:
            raise ApexError(APXXXX_ERROR_ARGUMENT_VALUE, "Number")
            sys.exit()
        
        if not isinstance(TraceNumber, int):
            raise ApexError(APXXXX_ERROR_ARGUMENT_TYPE, "TraceNumber")
            sys.exit()
        
        if not TraceNumber in self.__Validtracenumbers:
            raise ApexError(APXXXX_ERROR_ARGUMENT_VALUE, "TraceNumber")
            sys.exit()
        
        if not self.__Simulation:
            Command = "CSPNBPOINTS" + str(TraceNumber) + "," + str(Number) + "\n"
            Send(self.__Connexion, Command)
    
    
    def GetNbPoints(self, TraceNumber = 0):
        '''
        Get the number of points for the FFT operation
        TraceNumber is an integer between 0 and 6:
            - 0: Carrier mode is set for all traces (default)
            - 1 to 6: Carrier mode is set to the specified trace
        '''
        from PyApex.Constantes import APXXXX_ERROR_ARGUMENT_TYPE, APXXXX_ERROR_ARGUMENT_VALUE
        from PyApex.Errors import ApexError
        
        if not isinstance(TraceNumber, int):
            raise ApexError(APXXXX_ERROR_ARGUMENT_TYPE, "TraceNumber")
            sys.exit()
        
        if not TraceNumber in self.__Validtracenumbers:
            raise ApexError(APXXXX_ERROR_ARGUMENT_VALUE, "TraceNumber")
            sys.exit()
        
        if self.__Simulation:
            Number = 4096
        else:
            Command = "CSPNBPOINTS" + str(TraceNumber) + "?\n"
            Send(self.__Connexion, Command)
            Number = int(Receive(self.__Connexion)[:-1])

        return Number
    
    
    def SetTimeShift(self, TimeShift, TraceNumber = 0):
        '''
        Set the time shift used for the FFT operation
        TimeShift is a float expressed in ns
        TraceNumber is an integer between 0 and 6:
            - 0: Carrier mode is set for all traces (default)
            - 1 to 6: Carrier mode is set to the specified trace
        '''
        from PyApex.Constantes import APXXXX_ERROR_ARGUMENT_TYPE, APXXXX_ERROR_ARGUMENT_VALUE
        from PyApex.Errors import ApexError
        
        if not isinstance(TimeShift, (int, float)):
            raise ApexError(APXXXX_ERROR_ARGUMENT_TYPE, "TimeShift")
            sys.exit()
        
        if not isinstance(TraceNumber, int):
            raise ApexError(APXXXX_ERROR_ARGUMENT_TYPE, "TraceNumber")
            sys.exit()
        
        if not TraceNumber in self.__Validtracenumbers:
            raise ApexError(APXXXX_ERROR_ARGUMENT_VALUE, "TraceNumber")
            sys.exit()
        
        if not self.__Simulation:
            Command = "CSPTIMESHIFT" + str(TraceNumber) + "," + str(TimeShift) + "\n"
            Send(self.__Connexion, Command)
    
    
    def GetTimeShift(self, TraceNumber = 0):
        '''
        Get the time shift used for the FFT operation
        Time shift is expressed in ns
        TraceNumber is an integer between 0 and 6:
            - 0: Carrier mode is set for all traces (default)
            - 1 to 6: Carrier mode is set to the specified trace
        '''
        from PyApex.Constantes import APXXXX_ERROR_ARGUMENT_TYPE, APXXXX_ERROR_ARGUMENT_VALUE
        from PyApex.Errors import ApexError
        
        if not isinstance(TraceNumber, int):
            raise ApexError(APXXXX_ERROR_ARGUMENT_TYPE, "TraceNumber")
            sys.exit()
        
        if not TraceNumber in self.__Validtracenumbers:
            raise ApexError(APXXXX_ERROR_ARGUMENT_VALUE, "TraceNumber")
            sys.exit()
        
        if self.__Simulation:
            TimeShift = 0.0
        else:
            Command = "CSPTIMESHIFT" + str(TraceNumber) + "?\n"
            Send(self.__Connexion, Command)
            TimeShift = float(Receive(self.__Connexion)[:-1])

        return TimeShift
    
    
    def SetPhaseOrigin(self, PhaseOrigin, GraphType = "all"):
        '''
        Set the the phase origin for spectrum and / or temporal graphs
        PhaseOrigin is expressed in degrees
        GraphType is an integer or a string:
            - "all" or 0: PhaseOrigin is applied to spectrum and temporal graphs (default)
            - "spectrum" or 1: PhaseOrigin is applied to spectrum graphs only
            - "temporal" or 2: PhaseOrigin is applied to temporal graphs only
        '''
        from PyApex.Constantes import APXXXX_ERROR_ARGUMENT_TYPE, APXXXX_ERROR_ARGUMENT_VALUE
        from PyApex.Errors import ApexError
        
        if not isinstance(PhaseOrigin, (int, float)):
            raise ApexError(APXXXX_ERROR_ARGUMENT_TYPE, "PhaseOrigin")
            sys.exit()
        
        if not isinstance(GraphType, (int, str)):
            raise ApexError(APXXXX_ERROR_ARGUMENT_TYPE, "GraphType")
            sys.exit()
        
        if isinstance(GraphType, str):
            if GraphType.lower() == "spectrum":
                GraphType = 1
            elif GraphType.lower() == "temporal":
                GraphType = 2
            else:
                GraphType = 0
        
        if not GraphType in [0, 1, 2]:
            raise ApexError(APXXXX_ERROR_ARGUMENT_VALUE, "GraphType")
            sys.exit()
        
        if not self.__Simulation:
            if GraphType == 0 or GraphType == 1:
                Command = "CSPORIPHIF" + str(PhaseOrigin) + "\n"
                Send(self.__Connexion, Command)
            if GraphType == 0 or GraphType == 2:
                Command = "CSPORIPHIT" + str(PhaseOrigin) + "\n"
                Send(self.__Connexion, Command)
    
    
    def GetPhaseOrigin(self, GraphType = "all"):
        '''
        Get the the phase origin for spectrum and / or temporal graphs
        Phase origin are expressed in degrees and returned in a list
        GraphType is an integer or a string:
            - "all" or 0: PhaseOrigin of both spectrum and temporal graphs (default)
            - "spectrum" or 1: Phase origin of spectrum graphs only
            - "temporal" or 2: Phase origin of temporal graphs only
        If GraphType = "all" (or 0), the two phase origins are returned in the list:
            - index 0: Phase origin of spectrum graphs
            - index 1: Phase origin of temporal graphs
        '''
        from PyApex.Constantes import APXXXX_ERROR_ARGUMENT_TYPE, APXXXX_ERROR_ARGUMENT_VALUE
        from PyApex.Errors import ApexError
        
        if not isinstance(GraphType, (int, str)):
            raise ApexError(APXXXX_ERROR_ARGUMENT_TYPE, "GraphType")
            sys.exit()
        
        if isinstance(GraphType, str):
            if GraphType.lower() == "spectrum":
                GraphType = 1
            elif GraphType.lower() == "temporal":
                GraphType = 2
            else:
                GraphType = 0
        
        if not GraphType in [0, 1, 2]:
            raise ApexError(APXXXX_ERROR_ARGUMENT_VALUE, "GraphType")
            sys.exit()
        
        if self.__Simulation:
            if GraphType == 0:
                PhaseOrigin = [0.0, 0.0]
            else:
                PhaseOrigin = [0.0]
        else:
            PhaseOrigin = []
            if GraphType == 0 or GraphType == 1:
                Command = "CSPORIPHIF?\n"
                Send(self.__Connexion, Command)
                PhaseOrigin.append(float(Receive(self.__Connexion)[:-1]))
            if GraphType == 0 or GraphType == 2:
                Command = "CSPORIPHIT?\n"
                Send(self.__Connexion, Command)
                PhaseOrigin.append(float(Receive(self.__Connexion)[:-1]))
        
        return PhaseOrigin
    
    
    def SetPhaseWrapping(self, PhaseWrapping = "no", GraphType = "all"):
        '''
        Set the the phase wrapping for spectrum and / or temporal graphs
        PhaseWrapping can be an integer or a string:
            - "no" or 0: No wrapping is applied (default)
            - "basic" or 1: A basic wrapping is applied
            - "linear" or 2: A linear wrapping is applied
        GraphType can be an integer or a string:
            - "all" or 0: PhaseWrapping is applied to spectrum and temporal graphs (default)
            - "spectrum" or 1: PhaseWrapping is applied to spectrum graphs only
            - "temporal" or 2: PhaseWrapping is applied to temporal graphs only
        '''
        from PyApex.Constantes import APXXXX_ERROR_ARGUMENT_TYPE, APXXXX_ERROR_ARGUMENT_VALUE
        from PyApex.Errors import ApexError
        
        if not isinstance(PhaseWrapping, (int, str)):
            raise ApexError(APXXXX_ERROR_ARGUMENT_TYPE, "PhaseWrapping")
            sys.exit()
        
        if isinstance(PhaseWrapping, str):
            if PhaseWrapping.lower() == "basic":
                PhaseWrapping = 1
            elif GraphType.lower() == "linear":
                PhaseWrapping = 2
            else:
                PhaseWrapping = 0
        
        if not PhaseWrapping in [0, 1, 2]:
            raise ApexError(APXXXX_ERROR_ARGUMENT_VALUE, "PhaseWrapping")
            sys.exit()
        
        if not isinstance(GraphType, (int, str)):
            raise ApexError(APXXXX_ERROR_ARGUMENT_TYPE, "GraphType")
            sys.exit()
        
        if isinstance(GraphType, str):
            if GraphType.lower() == "spectrum":
                GraphType = 1
            elif GraphType.lower() == "temporal":
                GraphType = 2
            else:
                GraphType = 0
        
        if not GraphType in [0, 1, 2]:
            raise ApexError(APXXXX_ERROR_ARGUMENT_VALUE, "GraphType")
            sys.exit()
        
        if not self.__Simulation:
            if GraphType == 0 or GraphType == 1:
                Command = "CSPWRAPPHIF" + str(PhaseWrapping) + "\n"
                Send(self.__Connexion, Command)
            if GraphType == 0 or GraphType == 2:
                Command = "CSPWRAPPHIT" + str(PhaseWrapping) + "\n"
                Send(self.__Connexion, Command)
    
    
    def GetPhaseWrapping(self, GraphType = "all"):
        '''
        Get the the phase wrapping for spectrum and / or temporal graphs
        Phase wrapping is a string which can be:
            - "no": No wrapping is applied (default)
            - "basic": A basic wrapping is applied
            - "linear": A linear wrapping is applied
        GraphType is an integer or a string:
            - "all" or 0: PhaseOrigin of both spectrum and temporal graphs (default)
            - "spectrum" or 1: Phase wrapping of spectrum graphs only
            - "temporal" or 2: Phase wrapping of temporal graphs only
        If GraphType = "all" (or 0), the two phase origins are returned in the list:
            - index 0: Phase wrapping of spectrum graphs
            - index 1: Phase wrapping of temporal graphs
        '''
        from PyApex.Constantes import APXXXX_ERROR_ARGUMENT_TYPE, APXXXX_ERROR_ARGUMENT_VALUE
        from PyApex.Errors import ApexError
        
        if not isinstance(GraphType, (int, str)):
            raise ApexError(APXXXX_ERROR_ARGUMENT_TYPE, "GraphType")
            sys.exit()
        
        if isinstance(GraphType, str):
            if GraphType.lower() == "spectrum":
                GraphType = 1
            elif GraphType.lower() == "temporal":
                GraphType = 2
            else:
                GraphType = 0
        
        if not GraphType in [0, 1, 2]:
            raise ApexError(APXXXX_ERROR_ARGUMENT_VALUE, "GraphType")
            sys.exit()
        
        if self.__Simulation:
            if GraphType == 0:
                PhaseWrapping = ["no", "no"]
            else:
                PhaseWrapping = ["no"]
        else:
            PhaseWrapping = []
            if GraphType == 0 or GraphType == 1:
                Command = "CSPWRAPPHIF?\n"
                Send(self.__Connexion, Command)
                Wrapping = int(Receive(self.__Connexion)[:-1])
                if Wrapping == 0:
                    PhaseWrapping.append("no")
                elif Wrapping == 1:
                    PhaseWrapping.append("basic")
                elif Wrapping == 2:
                    PhaseWrapping.append("linear")
            if GraphType == 0 or GraphType == 2:
                Command = "CSPWRAPPHIT?\n"
                Send(self.__Connexion, Command)
                Wrapping = int(Receive(self.__Connexion)[:-1])
                if Wrapping == 0:
                    PhaseWrapping.append("no")
                elif Wrapping == 1:
                    PhaseWrapping.append("basic")
                elif Wrapping == 2:
                    PhaseWrapping.append("linear")
        
        return PhaseWrapping
    
    
    def SetGraphNumber(self, Number):
        '''
        Set the number of graphs in the O.C.S.A. mode
        Number is an integer which can be:
            - 1 : Solo screen mode
            - 2 : Dual screens mode
            - 3 : Trio screens mode
            - 4 : Quatro screens mode
            - 6 : Hexa screens mode
            - 10 : Deca screens mode
        '''
        from PyApex.Constantes import APXXXX_ERROR_ARGUMENT_TYPE, APXXXX_ERROR_ARGUMENT_VALUE
        from PyApex.Errors import ApexError
        
        if not isinstance(Number, int):
            raise ApexError(APXXXX_ERROR_ARGUMENT_TYPE, "Number")
            sys.exit()
        
        if not Number in self.__ValidScreensMode:
            raise ApexError(APXXXX_ERROR_ARGUMENT_VALUE, "Number")
            sys.exit()
        
        if not self.__Simulation:
            Command = "CSPGRAPHNB" + str(Number) + "\n"
            Send(self.__Connexion, Command)
    
    
    def GetGraphNumber(self):
        '''
        Get the number of graphs in the O.C.S.A. mode
        '''
        
        if self.__Simulation:
            Number = 10
        else:
            Command = "CSPGRAPHNB?\n"
            Send(self.__Connexion, Command)
            Number = int(Receive(self.__Connexion)[:-1])

        return Number
    
    
    def SetGraphType(self, Number, Type, Polar = 0):
        '''
        Set the type of the specified graph
        Number is an integer representing the graph number (between 1 and 10)
        Type is an integer or string which can be:
            - 0 or "spectrum power": graph is set to the Spectrum Power type
            - 1 or "spectrum phase": graph is set to the Spectrum Phase type
            - 2 or "temporal power": graph is set to the Temporal Power type
            - 3 or "temporal phase": graph is set to the Temporal Phase type
            - 4 or "temporal chirp": graph is set to the Temporal Chirp type
            - 5 or "temporal alpha": graph is set to the Temporal Alpha type
            - 6 or "constellation": graph is set to the Constellation type
            - 7 or "eye power": graph is set to the Eye Power type
            - 8 or "eye phase": graph is set to the Eye Phase type
        Polar is an integer or string which can be:
            - 0 or "1+2": Polarization 1 + 2 is selected
            - 1 or "1": Polarization 1 is selected
            - 2 or "2": Polarization 1 is selected
        '''
        from PyApex.Constantes import APXXXX_ERROR_ARGUMENT_TYPE, APXXXX_ERROR_ARGUMENT_VALUE
        from PyApex.Errors import ApexError
        
        if not isinstance(Number, int):
            raise ApexError(APXXXX_ERROR_ARGUMENT_TYPE, "Number")
            sys.exit()
        
        if Number > self.GetGraphNumber():
            raise ApexError(APXXXX_ERROR_ARGUMENT_VALUE, "Number")
            return
        
        if not isinstance(Type, (int, str)):
            raise ApexError(APXXXX_ERROR_ARGUMENT_TYPE, "Type")
            sys.exit()
        
        if isinstance(Type, str):
            for i in range(len(self.__ValidScreenType)):
                if Type.lower() == self.__ValidScreenType[i]:
                    Type = i
                    break
        
        if isinstance(Type, int):
            if Type < 0 or Type >= len(self.__ValidScreenType):
                raise ApexError(APXXXX_ERROR_ARGUMENT_VALUE, "Type")
                sys.exit()
        
        if not isinstance(Polar, (int, str)):
            raise ApexError(APXXXX_ERROR_ARGUMENT_TYPE, "Polar")
            sys.exit()
        
        if isinstance(Polar, str):
            for i in range(len(self.__ValidPolarType)):
                if Polar.lower() == self.__ValidPolarType[i]:
                    Polar = i
                    break
        
        if isinstance(Polar, int):
            if Polar < 0 or Polar >= len(self.__ValidPolarType):
                raise ApexError(APXXXX_ERROR_ARGUMENT_VALUE, "Polar")
                sys.exit()
            
        if not self.__Simulation:
            Command = "CSPGRAPHTYPE" + str(Number) + "," + str(Type) + "," + str(Polar) + "\n"
            Send(self.__Connexion, Command)
    
    
    def GetGraphType(self, Number, type = 's'):
        '''
        Get the type and the polar of the specified graph.
        The data are returned in a list: [Type, Polar]
        Number is an integer representing the graph number (between 1 and 10)
        type is a character which can be:
            - 's': the returned data are string (default)
            - 'i': the returned data are integer
        '''
        from PyApex.Constantes import APXXXX_ERROR_ARGUMENT_TYPE, APXXXX_ERROR_ARGUMENT_VALUE
        from PyApex.Errors import ApexError
        from random import randint
        
        if not isinstance(Number, int):
            raise ApexError(APXXXX_ERROR_ARGUMENT_TYPE, "Number")
            sys.exit()
        
        if Number > self.GetGraphNumber():
            raise ApexError(APXXXX_ERROR_ARGUMENT_VALUE, "Number")
            sys.exit()
            
        if self.__Simulation:
            Type = randint(0, len(self.__ValidScreenType))
            Polar = randint(0, len(self.__ValidPolarType))
        else:
            Command = "CSPGRAPHTYPE" + str(Number) + "?\n"
            Send(self.__Connexion, Command)
            RecString = Receive(self.__Connexion)[:-1]
            try:
                Type = int(RecString.split(",")[0])
                Polar = int(RecString.split(",")[1])
            except:
                return "Error"
            
        if type.lower() == 's':
            Type = self.__ValidScreenType[Type]
            Polar = self.__ValidPolarType[Polar]

        return [Type, Polar]
    
    
    def Run(self, Type="single"):
        '''
        Runs a measurement and returns the trace of the measurement (between 1 and 6)
        If Type is
            - "single" or 1, a single measurement is running (default)
            - "repeat" or 2, a repeat measurement is running
        In this function, the connection timeout is disabled and enabled after the
        execution of the function
        '''
        
        if self.__Simulation:
            trace = 1
        else:
            TimeOut = self.__Connexion.gettimeout()
            self.__Connexion.settimeout(None)
            
            if isinstance(Type, str):                  
                if Type.lower() == "repeat":
                    Command = "CSPSWP2\n"
                else:
                    Command = "CSPSWP1\n"
            else:
                if Type == 2:
                    Command = "CSPSWP2\n"
                else:
                    Command = "CSPSWP1\n"
            
            
            Send(self.__Connexion, Command)
            try:
                trace = int(Receive(self.__Connexion))
            except:
                trace = -1
        
            self.__Connexion.settimeout(TimeOut)
            
        return trace
    
    
    def GetSpectrum(self, XScale = "nm", YScale = "log", Polar = "1+2", TraceNumber = 1):
        '''
        Get the complex spectrum data of a measurement
        returns a 2D list [Power Data, Phase Data, X-Axis Data]
        XScale is a string which can be :
            - "nm" : get the X-Axis Data in nm (default)
            - "GHz" : get the X-Axis Data in GHz
        YScale is a string which can be :
            - "log" : get the Y-Axis Power Data in dBm (default)
            - "lin" : get the Y-Axis Power Data in mW
        Polar is a string which can be :
            - "1+2" : get the data from Polarization 1+2 (default)
            - "1" : get the data from Polarization 1
            - "2" : get the data from Polarization 2
        The Y-Axis Phase Data are always in degrees
        TraceNumber is an integer between 1 (default) and 6
        '''
        from random import random
        from math import log10
        from PyApex.Constantes import SimuAP2XXX_StartWavelength, SimuAP2XXX_StopWavelength
        from PyApex.Constantes import APXXXX_ERROR_ARGUMENT_TYPE, APXXXX_ERROR_ARGUMENT_VALUE 
        from PyApex.Errors import ApexError
        from time import sleep
        
        if not isinstance(XScale, str):
            raise ApexError(APXXXX_ERROR_ARGUMENT_TYPE, "XScale")
            sys.exit()
        
        if not isinstance(YScale, str):
            raise ApexError(APXXXX_ERROR_ARGUMENT_TYPE, "YScale")
            sys.exit()
        
        if not isinstance(Polar, (str, int)):
            raise ApexError(APXXXX_ERROR_ARGUMENT_TYPE, "Polar")
            sys.exit()
            
        if not isinstance(TraceNumber, (float, int)):
            raise ApexError(APXXXX_ERROR_ARGUMENT_TYPE, "TraceNumber")
            sys.exit()
            
        if not TraceNumber in self.__Validtracenumbers:
            raise ApexError(APXXXX_ERROR_ARGUMENT_VALUE, "TraceNumber")
            sys.exit()
        
        if Polar == 1 or Polar == "1":
            Polar = 1
        elif Polar == 2 or Polar == "2":
            Polar = 2
        else:
            Polar = 0
        
        NPoints = self.GetNbModesBeforeCarrier() + self.GetNbModesAfterCarrier() + 1
        if not self.__Simulation:
            PowerData = []
            PhaseData = []
            XData = []
            
            sleep(0.1)
            if YScale.lower() == "lin":
                Command = "CSPSPECTRL" + str(int(TraceNumber)) + "," + str(Polar) + "\n"
            else:
                Command = "CSPSPECTRD" + str(int(TraceNumber)) + "," + str(Polar) + "\n"
            Send(self.__Connexion, Command)
            YStr = ReceiveUntilChar(self.__Connexion)[:-1]
            YStr = YStr.split(" ")
            for s in YStr:
                try:
                    PowerData.append(float(s))
                except:
                    PowerData.append(0.0)
            
            sleep(0.1)
            Command = "CSPSPECTRPHI" + str(int(TraceNumber)) + "," + str(Polar) + "\n"           
            Send(self.__Connexion, Command)
            YStr = ReceiveUntilChar(self.__Connexion)[:-1]
            YStr = YStr.split(" ")
            for s in YStr:
                try:
                    PhaseData.append(float(s))
                except:
                    PhaseData.append(0.0)
            
            sleep(0.1)
            if XScale.lower() == "nm":
                Command = "CSPSPECTRWL" + str(int(TraceNumber)) + "," + str(Polar) + "\n"
            else:
                Command = "CSPSPECTRF" + str(int(TraceNumber)) + "," + str(Polar) + "\n"            
            Send(self.__Connexion, Command)
            XStr = ReceiveUntilChar(self.__Connexion)[:-1]
            XStr = XStr.split(" ")
            for s in XStr:
                try:
                    XData.append(float(s))
                except:
                    XData.append(0.0)
        else:
            PowerData = [NPoints]
            PhaseData = [NPoints]
            XData = [NPoints]       
            DeltaX = (self.__StopWavelength - self.__StartWavelength) / NPoints
            for i in range(0, NPoints):
                if Scale.lower() == "lin":
                    PowerData.append(random())
                else:
                    PowerData.append(80.0 * random() - 70.0)
                PhaseData.append(360.0 * random())
                XData.append(self.__StartWavelength + i * DeltaX)
                
        return [PowerData[1:], PhaseData[1:], XData[1:]]
    
    
    def Stop(self):
        '''
        Stops a measurement
        '''
        if not self.__Simulation:
            Command = "CSPSWP3\n"
            Send(self.__Connexion, Command)
    
    
    def LockTrace(self, TraceNumber, Lock):
        '''
        Lock or unlock a trace
        TraceNumber is an integer between 1 and 6
        Lock is a boolean:
            - True: the trace TraceNumber is locked
            - False: the trace TraceNumber is unlocked
        '''
        from PyApex.Constantes import APXXXX_ERROR_ARGUMENT_TYPE, APXXXX_ERROR_ARGUMENT_VALUE
        from PyApex.Errors import ApexError

        if not isinstance(TraceNumber, int):
            raise ApexError(APXXXX_ERROR_ARGUMENT_TYPE, "TraceNumber")
            sys.exit()

        if not TraceNumber in self.__Validtracenumbers:
            raise ApexError(APXXXX_ERROR_ARGUMENT_VALUE, "TraceNumber")
            sys.exit()

        if Lock:
            Lock = True
        else:
            Lock = False

        if not self.__Simulation:
            if Lock:
                Command = "CSPTRLOCK" + str(TraceNumber) + "\n"
            else:
                Command = "CSPTRUNLOCK" + str(TraceNumber) + "\n"
            Send(self.__Connexion, Command)


    def SetScrollMode(self, Enable):
        '''
        Enable or disable the screll mode
        Enable is a boolean:
            - True: the scroll mode is enabled
            - False: the scroll mode is disabled
        '''

        if Enable:
            Enable = 1
        else:
            Enable = 0

        if not self.__Simulation:
            Command = "CSPTRSCROLL" + str(Enable) + "\n"
            Send(self.__Connexion, Command)
    
    
    def DeleteAll(self):
        '''
        Clear all traces
        '''
        
        if not self.__Simulation:
            Command = "CSPTRDELAL\n"
            Send(self.__Connexion, Command)
    
    
    def DeleteTrace(self, TraceNumber):
        '''
        Clear the selected trace
        TraceNumber is an integer between 1 and 6
        '''
        from PyApex.Constantes import APXXXX_ERROR_ARGUMENT_TYPE, APXXXX_ERROR_ARGUMENT_VALUE
        from PyApex.Errors import ApexError

        if not isinstance(TraceNumber, int):
            raise ApexError(APXXXX_ERROR_ARGUMENT_TYPE, "TraceNumber")
            sys.exit()

        if not TraceNumber in self.__Validtracenumbers:
            raise ApexError(APXXXX_ERROR_ARGUMENT_VALUE, "TraceNumber")
            sys.exit()
        
        if not self.__Simulation:
            Command = "CSPTRDEL" + str(TraceNumber) + "\n"
            Send(self.__Connexion, Command)
    
    
    def SaveToFile(self, FileName, TraceNumber = 1, Type = "spectrum"):
        '''
        Save a trace on local hard disk
        FileName is a string representing the path of the file to save
        TraceNumber is an integer between 1 (default) and 6
        Type is the type of the file to save
        Type is a string between the following values:
            - Type = "SPECTRUM" : data are saved in the ComplexSpectrum format
            - Type = "TIME" : data are saved in the TimeProfile format
            - Type = "ANALYSIS" : data are saved in the AnalysisData format
            - Type = "DATA" : data are saved in the SpectrumData format
        '''
        from PyApex.Constantes import APXXXX_ERROR_ARGUMENT_TYPE, APXXXX_ERROR_ARGUMENT_VALUE, APXXXX_ERROR_BAD_FILENAME
        from PyApex.Errors import ApexError
        from os.path import isdir, dirname
        
        if not isinstance(TraceNumber, int):
            raise ApexError(APXXXX_ERROR_ARGUMENT_TYPE, "TraceNumber")
            sys.exit()
        
        if not TraceNumber in self.__Validtracenumbers:
            raise ApexError(APXXXX_ERROR_ARGUMENT_VALUE, "TraceNumber")
            sys.exit()
        
        if not isdir(dirname(FileName)):
            raise ApexError(APXXXX_ERROR_BAD_FILENAME, str(FileName))
            sys.exit()
        
        if str(Type).lower() == "spectrum":
            Type = "A"
        elif str(Type).lower() == "time":
            Type = "B"
        elif str(Type).lower() == "analysis":
            Type = "C"
        elif str(Type).lower() == "data":
            Type = "D"
        
        if not self.__Simulation:
            Command = "CSPSAVE" + str(Type) + str(TraceNumber) + "_" + str(FileName) + "\n"
            Send(self.__Connexion, Command)
    
    
    def LoadFromFile(self, FileName):
        '''
        Load a file with O.C.S.A. data
        FileName is a string representing the path of the data file
        '''
        from PyApex.Constantes import APXXXX_ERROR_BAD_FILENAME
        from PyApex.Errors import ApexError
        from os.path import isdir, dirname
        
        if not isdir(dirname(FileName)):
            raise ApexError(APXXXX_ERROR_BAD_FILENAME, str(FileName))
            sys.exit()
        
        if not self.__Simulation:
            Command = "CSPLOAD_" + str(FileName) + "\n"
            Send(self.__Connexion, Command)
    
