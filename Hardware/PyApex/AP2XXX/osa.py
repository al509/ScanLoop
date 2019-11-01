from Hardware.PyApex.Common import Send, Receive, ReceiveUntilChar
import sys
from Hardware.PyApex.Constantes import *
from Hardware.PyApex.Errors import ApexError
from random import random
from math import log10
from Hardware.PyApex.Constantes import SimuAP2XXX_StartWavelength, SimuAP2XXX_StopWavelength
from Hardware.PyApex.Constantes import APXXXX_ERROR_ARGUMENT_TYPE
from Hardware.PyApex.Errors import ApexError
from Hardware.PyApex.AP2XXX import AP2XXX

class OSA(AP2XXX):
    def __init__(self,host, Simulation=False):
        '''
        Constructor of a Heterodyne OSA equipment.
        Equipment is the AP2XXX class of the equipment
        Simulation is a boolean to indicate to the program if it has to run in simulation mode or not
        '''
        AP2XXX.__init__(self,host)
        self.__Connexion = self.Connexion
        self.__Simulation = Simulation
        self.__ID = self.GetID()
        self.__Type = self.GetType()

        # Variables and constants of the equipment

        self.__SweepResolution = 1.12
        self.__ValidSweepResolutions = [0 , 1 , 2]
        self.__NPoints = 1000
        self.__NoiseMaskValue = -70
        self.__ValidScaleUnits = [0 , 1]
        self.__ScaleXUnit = 1
        self.__ScaleYUnit = 1
        self.__ValidPolarizationModes = [0 , 1 , 2 , 3]
        self.__PolarizationMode = 0
        self.__Validtracenumbers = [0 , 1 , 2 , 3 , 4 , 5 , 6]
        self.__tracenumber = 1
        self.__NAverageOSA = 5
        
        
        self._StartWavelength = self.GetStartWavelength()
        self._StopWavelength = self.GetStopWavelength()
        self._Span = self._StopWavelength  - self._StartWavelength
        self._Center = self._StartWavelength + (self._Span / 2)

             

    
    def SetAutoPointNumberSelection(self, IsAuto=True):
        '''
        '''
        if not self.__Simulation:
            if IsAuto:
                Command = 'SPAUTONBPT1\n'
            else:
                Command = 'SPAUTONBPT0\n'
            Send(self.__Connexion, Command)

    def __str__(self):
        '''
        Return the equipment type and the AP2XXX ID
        '''
        return "Heterodyne OSA " + str(self.__ID)


    def GetType(self):
        '''
        Return the type of the OSA. For example "AP2061" for an AP2061
        '''
        from Hardware.PyApex.Errors import ApexError
        import re

        Type = self.__ID.split("/")[1]
        Type = "AP" + Type
        return Type


    def SetStartWavelength(self, Wavelength):
        '''
        Set the start wavelength of the measurement span
        Wavelength is expressed in nm
        '''
        from Hardware.PyApex.Constantes import APXXXX_ERROR_ARGUMENT_TYPE, APXXXX_ERROR_ARGUMENT_VALUE
        from Hardware.PyApex.Errors import ApexError

        if not isinstance(Wavelength, (float, int)):
            raise ApexError(APXXXX_ERROR_ARGUMENT_TYPE, "Wavelength")
            sys.exit()

        if not self.__Simulation:
            Command = "SPSTRTWL" + str(Wavelength) + "\n"
            Send(self.__Connexion, Command)

        self._StartWavelength = Wavelength
        self._Span = self._StopWavelength - self._StartWavelength
        self._Center = self._StartWavelength + (self._Span / 2)


    def GetStartWavelength(self):
        '''
        Get the start wavelength of the measurement span
        Wavelength is expressed in nm
        '''

        if not self.__Simulation:
            Command = "SPSTRTWL?\n"
            Send(self.__Connexion, Command)
            self._StartWavelength = float(Receive(self.__Connexion)[:-1])

        return self._StartWavelength


    def SetStopWavelength(self, Wavelength):
        '''
        Set the stop wavelength of the measurement span
        Wavelength is expressed in nm
        '''
        from Hardware.PyApex.Constantes import APXXXX_ERROR_ARGUMENT_TYPE, APXXXX_ERROR_ARGUMENT_VALUE
        from Hardware.PyApex.Errors import ApexError

        if not isinstance(Wavelength, (float, int)):
            raise ApexError(APXXXX_ERROR_ARGUMENT_TYPE, "Wavelength")
            sys.exit()

        if not self.__Simulation:
            Command = "SPSTOPWL" + str(Wavelength) + "\n"
            Send(self.__Connexion, Command)

        self._StopWavelength = Wavelength
        self._Span = self._StopWavelength - self._StartWavelength
        self._Center = self._StartWavelength + (self._Span / 2)


    def GetStopWavelength(self):
        '''
        Get the stop wavelength of the measurement span
        Wavelength is expressed in nm
        '''

        if not self.__Simulation:
            Command = "SPSTOPWL?\n"
            Send(self.__Connexion, Command)
            self._StopWavelength = float(Receive(self.__Connexion)[:-1])

        return self._StopWavelength


    def SetSpan(self, Span):
        '''
        Set the wavelength measurement span
        Span is expressed in nm
        '''
        from Hardware.PyApex.Constantes import APXXXX_ERROR_ARGUMENT_TYPE, APXXXX_ERROR_ARGUMENT_VALUE
        from Hardware.PyApex.Errors import ApexError

        if not isinstance(Span, (float, int)):
            raise ApexError(APXXXX_ERROR_ARGUMENT_TYPE, "Span")
            sys.exit()

        if not self.__Simulation:
            Command = "SPSPANWL" + str(Span) + "\n"
            Send(self.__Connexion, Command)

        self._Span = Span
        self._StopWavelength = self._Center + (self._Span / 2)
        self._StartWavelength = self._Center - (self._Span / 2)


    def GetSpan(self):
        '''
        Get the wavelength measurement span
        Span is expressed in nm
        '''

        if not self.__Simulation:
            Command = "SPSPANWL?\n"
            Send(self.__Connexion, Command)
            self._Span = float(Receive(self.__Connexion)[:-1])

        return self._Span


    def SetCenter(self, Center):
        '''
        Set the wavelength measurement center
        Center is expressed in nm
        '''
        from Hardware.PyApex.Constantes import APXXXX_ERROR_ARGUMENT_TYPE, APXXXX_ERROR_ARGUMENT_VALUE
        from Hardware.PyApex.Errors import ApexError

        if not isinstance(Center, (float, int)):
            raise ApexError(APXXXX_ERROR_ARGUMENT_TYPE, "Center")
            sys.exit()

        if not self.__Simulation:
            Command = "SPCTRWL" + str(Center) + "\n"
            Send(self.__Connexion, Command)

        self._Center = Center
        self._StopWavelength = self._Center + (self._Span / 2)
        self._StartWavelength = self._Center - (self._Span / 2)


    def GetCenter(self):
        '''
        Get the wavelength measurement center
        Center is expressed in nm
        '''

        if not self.__Simulation:
            Command = "SPCTRWL?\n"
            Send(self.__Connexion, Command)
            self._Center = float(Receive(self.__Connexion)[:-1])

        return self._Center


    def SetXResolution(self, Resolution):
        '''
        Set the wavelength measurement resolution
        Resolution is expressed in the value of 'ScaleXUnit'
        '''
        if not self.__Simulation:
            Command = "SPSWPRES" + str(Resolution) + "\n"
            Send(self.__Connexion, Command)

        self.__SweepResolution = Resolution


    def GetXResolution(self):
        '''
        Get the wavelength measurement resolution
        Resolution is expressed in the value of 'ScaleXUnit'
        '''

        if not self.__Simulation:
            Command = "SPSWPRES?\n"
            Send(self.__Connexion, Command)
            self.__SweepResolution = float(Receive(self.__Connexion)[:-1])
        return self.__SweepResolution


    def SetYResolution(self, Resolution):
        '''
        Set the Y-axis power per division value
        Resolution is expressed in the value of 'ScaleYUnit'
        '''
        from Hardware.PyApex.Constantes import APXXXX_ERROR_ARGUMENT_TYPE, APXXXX_ERROR_ARGUMENT_VALUE
        from Hardware.PyApex.Constantes import AP2XXX_MINYRES, AP2XXX_MAXYRES
        from Hardware.PyApex.Errors import ApexError

        if not isinstance(Resolution, (float, int)):
            raise ApexError(APXXXX_ERROR_ARGUMENT_TYPE, "Resolution")
            sys.exit()
        if Resolution < AP2XXX_MINYRES or Resolution > AP2XXX_MAXYRES:
            raise ApexError(APXXXX_ERROR_ARGUMENT_VALUE, "Resolution")
            sys.exit()

        if not self.__Simulation:
            Command = "SPDIVY" + str(Resolution) + "\n"
            Send(self.__Connexion, Command)


    def GetYResolution(self):
        '''
        Get the Y-axis power per division value
        Resolution is expressed in the value of 'ScaleYUnit'
        '''

        if not self.__Simulation:
            Command = "SPDIVY?\n"
            Send(self.__Connexion, Command)
            Resolution = Receive(self.__Connexion)

        return float(Resolution[:-1])


    def SetNPoints(self, NPoints):
        '''
        Set the number of points for the measurement
        '''

        if not isinstance(NPoints, int):
            raise ApexError(APXXXX_ERROR_ARGUMENT_TYPE, "NPoints")
            sys.exit()
        if NPoints < AP2XXX_MINNPTS or NPoints > AP2XXX_MAXNPTS:
            raise ApexError(APXXXX_ERROR_ARGUMENT_VALUE, "NPoints")
            sys.exit()
        
        if not self.__Simulation:
            Command = "SPNBPTSWP" + str(NPoints) + "\n"
            Send(self.__Connexion, Command)

        self.__NPoints = NPoints


    def GetNPoints(self):
        '''
        Get the number of points for the measurement
        '''

        if not self.__Simulation:
            
            Command = "SPNBPTSWP?\n"
            Send(self.__Connexion, Command)
            try:
                self.__NPoints = int(Receive(self.__Connexion)[:-1])
            except ValueError: #this is 
                self.Reconnect()
        return self.__NPoints


    def Run(self, Type="single"):
        '''
        Runs a measurement and returns the trace of the measurement (between 1 and 6)
        If Type is
            - "auto" or 0, an auto-measurement is running
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
                if Type.lower() == "auto":
                    Command = "SPSWP0\n"
                elif Type.lower() == "repeat":
                    Command = "SPSWP2\n"
                else:
                    Command = "SPSWP1\n"
            else:
                if Type == 0:
                    Command = "SPSWP0\n"
                elif Type == 2:
                    Command = "SPSWP2\n"
                else:
                    Command = "SPSWP1\n"


            Send(self.__Connexion, Command)
            try:
                trace = int(Receive(self.__Connexion))
            except:
                trace = 0

            self.__Connexion.settimeout(TimeOut)

        return trace


    def Stop(self):
        '''
        Stops a measurement
        '''
        if not self.__Simulation:
            Command = "SPSWP3\n"
            Send(self.__Connexion, Command)


    def GetData(self, ScaleX = "nm", ScaleY = "log", TraceNumber = 1):
        '''
        Get the spectrum data of a measurement
        returns a 2D list [Y-axis Data, X-Axis Data]
        ScaleX is a string which can be :
            - "nm" : get the X-Axis Data in nm (default)
            - "GHz": get the X-Axis Data in GHz
        ScaleY is a string which can be :
            - "log" : get the Y-Axis Data in dBm (default)
            - "lin" : get the Y-Axis Data in mW
        TraceNumber is an integer between 1 (default) and 6
        '''


        if not isinstance(ScaleX, str):
            raise ApexError(APXXXX_ERROR_ARGUMENT_TYPE, "ScaleX")
            sys.exit()

        if not isinstance(ScaleY, str):
            raise ApexError(APXXXX_ERROR_ARGUMENT_TYPE, "ScaleY")
            sys.exit()

        if not isinstance(TraceNumber, (float, int)):
            raise ApexError(APXXXX_ERROR_ARGUMENT_TYPE, "TraceNumber")
            sys.exit()

        self.__NPoints = self.GetNPoints()
        if not self.__Simulation:
            YData = []
            XData = []

            if ScaleY.lower() == "lin":
                Command = "SPDATAL" + str(int(TraceNumber)) + "\n"
            else:
                Command = "SPDATAD" + str(int(TraceNumber)) + "\n"
            Send(self.__Connexion, Command)
            YStr = ReceiveUntilChar(self.__Connexion)[:-1]
            YStr = YStr.split(" ")
            for s in YStr:
                try:
                    YData.append(float(s))
                except:
                    YData.append(0.0)

            if ScaleX.lower() == "ghz":
                Command = "SPDATAF" + str(int(TraceNumber)) + "\n"
            else:
                Command = "SPDATAWL" + str(int(TraceNumber)) + "\n"
            Send(self.__Connexion, Command)
            XStr = ReceiveUntilChar(self.__Connexion)[:-1]
            XStr = XStr.split(" ")
            for s in XStr:
                try:
                    XData.append(float(s))
                except:
                    XData.append(0.0)
        else:
            YData = [self.__NPoints]
            XData = [self.__NPoints]
            DeltaX = (self._StopWavelength - self._StartWavelength) / self.__NPoints
            for i in range(0, self.__NPoints):
                if Scale.lower() == "lin":
                    YData.append(random())
                else:
                    YData.append(80.0 * random() - 70.0)
                XData.append(self._StartWavelength + i * DeltaX)

        return [YData[1:], XData[1:]]


    def SetNoiseMask(self, NoiseMaskValue):
        '''
        Set the noise mask of the signal (values under this mask are set to this value)
        Noise mask is expressed in the value of 'ScaleYUnit'
        '''
        from Hardware.PyApex.Constantes import APXXXX_ERROR_ARGUMENT_TYPE
        from Hardware.PyApex.Errors import ApexError

        if not isinstance(NoiseMaskValue, (float, int)):
            raise ApexError(APXXXX_ERROR_ARGUMENT_TYPE, "NoiseMaskValue")
            sys.exit()

        if not self.__Simulation:
            Command = "SPSWPMSK" + str(NoiseMaskValue) + "\n"
            Send(self.__Connexion, Command)

        self.__NoiseMaskValue = NoiseMaskValue


    def SetScaleXUnit(self, ScaleXUnit=0):
        '''
        Defines the unit of the X-Axis
        ScaleXUnit can be a string or an integer
        If ScaleXUnit is :
            - "GHz" or 0, X-Axis unit is in GHz (default)
            - "nm" or 1, X-Axis unit is in nm
        '''
        from Hardware.PyApex.Constantes import APXXXX_ERROR_ARGUMENT_TYPE, APXXXX_ERROR_ARGUMENT_VALUE
        from Hardware.PyApex.Errors import ApexError

        if isinstance(ScaleXUnit, str):
            if ScaleXUnit.lower() == "nm":
                ScaleXUnit = 1
            else:
                ScaleXUnit = 0

        if not isinstance(ScaleXUnit, int):
            raise ApexError(APXXXX_ERROR_ARGUMENT_TYPE, "ScaleXUnit")
            sys.exit()

        if not ScaleXUnit in self.__ValidScaleUnits:
            raise ApexError(APXXXX_ERROR_ARGUMENT_VALUE, "ScaleXUnit")
            sys.exit()

        if not self.__Simulation:
            Command = "SPXUNT" + str(ScaleXUnit) + "\n"
            Send(self.__Connexion, Command)

        self.__ScaleXUnit = ScaleXUnit


    def SetScaleYUnit(self, ScaleYUnit=0):
        '''
        Defines the unit of the Y-Axis
        ScaleXUnit can be a string or an integer
        If ScaleYUnit is :
            - "lin" or 0, Y-Axis unit is in mW (default)
            - "log" or 1, Y-Axis unit is in dBm or dBm
        '''
        from Hardware.PyApex.Constantes import APXXXX_ERROR_ARGUMENT_TYPE, APXXXX_ERROR_ARGUMENT_VALUE
        from Hardware.PyApex.Errors import ApexError

        if isinstance(ScaleYUnit, str):
            if ScaleYUnit.lower() == "log":
                ScaleYUnit = 1
            else:
                ScaleYUnit = 0

        if not isinstance(ScaleYUnit, int):
            raise ApexError(APXXXX_ERROR_ARGUMENT_TYPE, "ScaleYUnit")
            sys.exit()

        if not ScaleYUnit in self.__ValidScaleUnits:
            raise ApexError(APXXXX_ERROR_ARGUMENT_VALUE, "ScaleYUnit")
            sys.exit()

        if not self.__Simulation:
            Command = "SPLINSC" + str(ScaleYUnit) + "\n"
            Send(self.__Connexion, Command)

        self.__ScaleYUnit = ScaleYUnit


    def SetPolarizationMode(self, PolarizationMode):
        '''
        Defines the measured polarization channels
        PolarizationMode can be a string or an integer
        If PolarizationMode is :
            - "1+2" or 0, the total power is measured (default)
            - "1&2" or 1, one measure is done for each polarization channel
            - "1" or 2, just the polarization channel 1 is measured
            - "2" or 3, just the polarization channel 2 is measured
        '''
        from Hardware.PyApex.Constantes import APXXXX_ERROR_ARGUMENT_TYPE, APXXXX_ERROR_ARGUMENT_VALUE
        from Hardware.PyApex.Errors import ApexError

        if isinstance(PolarizationMode, str):
            if PolarizationMode.lower() == "1&2":
                PolarizationMode = 1
            elif PolarizationMode.lower() == "1":
                PolarizationMode = 2
            elif PolarizationMode.lower() == "2":
                PolarizationMode = 3
            else:
                PolarizationMode = 0

        if not isinstance(PolarizationMode, int):
            raise ApexError(APXXXX_ERROR_ARGUMENT_TYPE, "PolarizationMode")
            sys.exit()

        if not PolarizationMode in self.__ValidPolarizationModes:
            raise ApexError(APXXXX_ERROR_ARGUMENT_VALUE, "PolarizationMode")
            sys.exit()

        if not self.__Simulation:
            Command = "SPPOLAR" + str(PolarizationMode) + "\n"
            Send(self.__Connexion, Command)

        self.__PolarizationMode = PolarizationMode


    def GetPolarizationMode(self):
        '''
        Gets the measured polarization channels
        The returned polarization mode can is a string which can be
            - "1+2" : the total power is measured (default)
            - "1&2" : one measure is done for each polarization channel
            - "1" : just the polarization channel 1 is measured
            - "2" : just the polarization channel 2 is measured
        '''

        if self.__PolarizationMode == 0:
            PolarizationMode = "1+2"
        elif self.__PolarizationMode == 1:
            PolarizationMode = "1&2"
        elif self.__PolarizationMode == 2:
            PolarizationMode = "1"
        elif self.__PolarizationMode == 3:
            PolarizationMode = "2"

        return PolarizationMode


    def WavelengthCalib(self):
        '''
        Performs a wavelength calibration.
        If a measurement is running, it is previously stopped
        '''
        if not self.__Simulation:
            Command = "SPWLCALM\n"
            Send(self.__Connexion, Command)


    def DeleteAll(self):
        '''
        Clear all traces
        '''
        if not self.__Simulation:
            Command = "SPTRDELAL\n"
            Send(self.__Connexion, Command)


    def ActivateAutoNPoints(self):
        '''
        Activates the automatic number of points for measurements
        '''
        if not self.__Simulation:
            Command = "SPAUTONBPT1\n"
            Send(self.__Connexion, Command)


    def DeactivateAutoNPoints(self):
        '''
        Deactivates the automatic number of points for measurements
        '''
        if not self.__Simulation:
            Command = "SPAUTONBPT0\n"
            Send(self.__Connexion, Command)


    def FindPeak(self, TraceNumber=1, ThresholdValue=20.0, Axis='X', Find="max"):
        '''
        Find the peaks in the selected trace
        TraceNumber is an integer between 1 (default) and 6
        ThresholdValue is a float expressed in dB
        Axis is a string or an integer for selecting the axis:
            Axis = 0 or 'X' : get the X-axis values of the markers (default)
            Axis = 1 or 'Y' : get the Y-axis values of the markers
            Axis = 2 or 'XY': get the X-axis and Y-axis values of the markers
        Find is a string between the following values:
            - Find = "MAX" : only the max peak is returned (default)
            - Find = "MIN" : only the min peak is returned
            - Find = "ALL" : all peaks are returned in a list
            - Find = "MEAN" : a mean value of all peaks is returned
        '''
        from Hardware.PyApex.Constantes import APXXXX_ERROR_ARGUMENT_TYPE, APXXXX_ERROR_ARGUMENT_VALUE
        from Hardware.PyApex.Errors import ApexError

        if not isinstance(TraceNumber, int):
            raise ApexError(APXXXX_ERROR_ARGUMENT_TYPE, "TraceNumber")
            sys.exit()

        if not Axis in [0, 1, 2] and not str(Axis).lower() in ['x', 'y', 'xy'] :
            raise ApexError(APXXXX_ERROR_ARGUMENT_VALUE, "Axis")
            sys.exit()

        if not TraceNumber in self.__Validtracenumbers:
            raise ApexError(APXXXX_ERROR_ARGUMENT_VALUE, "TraceNumber")
            sys.exit()

        if not isinstance(ThresholdValue, (int, float)):
            raise ApexError(APXXXX_ERROR_ARGUMENT_TYPE, "ThresholdValue")
            sys.exit()

        if not self.__Simulation:
            Command = "SPPKFIND" + str(TraceNumber) + "_" + str(ThresholdValue) + "\n"
            Send(self.__Connexion, Command)
            Peaks = self.GetMarkers(TraceNumber, Axis=Axis)

        Dual = False
        if Axis == 2 or str(Axis).lower() == 'xy':
            Dual = True

        else:
            Peaks = [1545.000, 1550.000, 1555.000]

        if str(Find).lower() == "all":
            return Peaks

        elif str(Find).lower() == "mean":
            Length = len(Peaks)
            if Dual:
                Length = len(Peaks[0])
            if Length > 0:
                if Dual:
                    Mean = [0.0, 0.0]
                    for i in Length:
                        Mean[0] += Peaks[0][i]
                        Mean[1] += Peaks[1][i]
                    Mean[0] /= Length
                    Mean[1] /= Length
                    return Mean
                else:
                    Sum = 0.0
                    for p in Peaks:
                        Sum += p
                    return Sum / len(Peaks)
            else:
                if Dual:
                    return [0.0, 0.0]
                else:
                    return 0.0

        elif str(Find).lower() == "min":
            Length = len(Peaks)
            if Dual:
                Length = len(Peaks[0])
            if Length > 0:
                if Dual:
                    Index = Peaks[0].index(min(Peaks[0]))
                    Min = [Peaks[0][Index], Peaks[1][Index]]
                else:
                    Min = min(Peaks)
                return Min
            else:
                if Dual:
                    return [0.0, 0.0]
                else:
                    return 0.0

        else:
            Length = len(Peaks)
            if Dual:
                Length = len(Peaks[0])
            if Length > 0:
                if Dual:
                    Index = Peaks[0].index(max(Peaks[0]))
                    Max = [Peaks[0][Index], Peaks[1][Index]]
                else:
                    Max = max(Peaks)
                return Max
            else:
                if Dual:
                    return [0.0, 0.0]
                else:
                    return 0.0

        self.__tracenumber = TraceNumber
        return Peak


    def ActivateAverageMode(self):
        '''
        Activates the average mode
        '''
        if not self.__Simulation:
            Command = "SPAVERAGE1\n"
            Send(self.__Connexion, Command)


    def DeactivateAverageMode(self):
        '''
        Deactivates the average mode
        '''
        if not self.__Simulation:
            Command = "SPAVERAGE0\n"
            Send(self.__Connexion, Command)


    def AutoMeasure(self, TraceNumber=1, NbAverage=1):
        '''
        Auto measurement which performs a single and looks for the maximum peak
        If a peak is detected, this method selects the spectral range and modify the span
        TraceNumber is an integer between 1 (default) and 6
        NbAverage is the number of average to perform after the span selection (no average by default)
        '''
        from Hardware.PyApex.Constantes import APXXXX_ERROR_ARGUMENT_TYPE, APXXXX_ERROR_ARGUMENT_VALUE
        from Hardware.PyApex.Constantes import AP2XXX_WLMIN, AP2XXX_WLMAX
        from Hardware.PyApex.Errors import ApexError

        if not isinstance(TraceNumber, int):
            raise ApexError(APXXXX_ERROR_ARGUMENT_TYPE, "TraceNumber")
            sys.exit()

        if not isinstance(NbAverage, (int, float)):
            raise ApexError(APXXXX_ERROR_ARGUMENT_TYPE, "NbAverage")
            sys.exit()

        if int(NbAverage) < 1:
            NbAverage = 1

        if not TraceNumber in self.__Validtracenumbers:
            raise ApexError(APXXXX_ERROR_ARGUMENT_VALUE, "TraceNumber")
            sys.exit()

        self.DeleteAll()
        self.SetStartWavelength(AP2XXX_WLMIN)
        self.SetStopWavelength(AP2XXX_WLMAX)
        self.Run()

        PeakValue = self.FindPeak(TraceNumber, ThresholdValue=20.0, Find="Max")

        if PeakValue != 0.0:
            if self.ScaleXUnit == 0:
                self.SetSpan(125.0)
            else:
                self.SetSpan(1.0)
            self.SetCenter(PeakValue)

            self.DeleteAll()
            self.DelAllMarkers(TraceNumber)

            if int(NbAverage) > 1:
                self.ActivateAverageMode()
            for i in range(NbAverage):
                self.Run()
            if int(NbAverage) > 1:
                self.DesactivateAverageMode()


    def AddMarker(self, Position, TraceNumber=1):
        '''
        Add a marker
        TraceNumber is an integer between 1 (default) and 6
        Position is the X-axis position of the marker expressed in the value of 'ScaleXUnit'
        '''
        from Hardware.PyApex.Constantes import APXXXX_ERROR_ARGUMENT_TYPE, APXXXX_ERROR_ARGUMENT_VALUE
        from Hardware.PyApex.Errors import ApexError

        if not isinstance(TraceNumber, int):
            raise ApexError(APXXXX_ERROR_ARGUMENT_TYPE, "TraceNumber")
            sys.exit()

        if not isinstance(Position, (int, float)):
            raise ApexError(APXXXX_ERROR_ARGUMENT_TYPE, "Position")
            sys.exit()

        if not TraceNumber in self.__Validtracenumbers:
            raise ApexError(APXXXX_ERROR_ARGUMENT_VALUE, "TraceNumber")
            sys.exit()

        if not self.__Simulation:
            Command = "SPMKRAD" + str(TraceNumber) + "_" + str(Position) + "\n"
            Send(self.__Connexion, Command)


    def GetMarkers(self, TraceNumber=1, Axis='y'):
        '''
        Gets the X-axis or Y-axis markers of a selected trace
        TraceNumber is an integer between 1 (default) and 6
        Axis is a string or an integer for selecting the axis:
            Axis = 0 or 'X' : get the X-axis values of the markers
            Axis = 1 or 'Y' : get the Y-axis values of the markers (default)
            Axis = 2 or 'XY': get the X-axis and Y-axis values of the markers
        '''
        from Hardware.PyApex.Constantes import APXXXX_ERROR_ARGUMENT_TYPE, APXXXX_ERROR_ARGUMENT_VALUE
        from Hardware.PyApex.Errors import ApexError

        if not isinstance(Axis, (int, str)):
            raise ApexError(APXXXX_ERROR_ARGUMENT_TYPE, "Axis")
            sys.exit()

        if not Axis in [0, 1, 2] and not str(Axis).lower() in ['x', 'y', 'xy'] :
            raise ApexError(APXXXX_ERROR_ARGUMENT_VALUE, "Axis")
            sys.exit()

        if not isinstance(TraceNumber, int):
            raise ApexError(APXXXX_ERROR_ARGUMENT_TYPE, "TraceNumber")
            sys.exit()

        if not TraceNumber in self.__Validtracenumbers:
            raise ApexError(APXXXX_ERROR_ARGUMENT_VALUE, "TraceNumber")
            sys.exit()

        if str(Axis).lower() == 'x':
            Axis = 0
        elif str(Axis).lower() == 'xy':
            Axis = 2
        else:
            Axis = 1

        if Axis == 2:
            XYMarkers = [[], []]

        Markers = []
        if not self.__Simulation:
            Markers = []
            if Axis in [1, 2]:
                Command = "SPDATAMKRX" + str(TraceNumber) + "\n"
                Send(self.__Connexion, Command)
                Str = Receive(self.__Connexion, 64)[:-1]
                Str = Str.split(" ")
                Str = Str[1:]

                for v in Str:
                    if v.lower() not in ["nm", "ghz"]:
                        try:
                            Markers.append(float(v))
                        except:
                            pass

            if Axis == 2:
                XYMarkers[0] = Markers

            Markers = []
            if Axis in [0, 2]:
                Command = "SPDATAMKRY" + str(TraceNumber) + "\n"
                Send(self.__Connexion, Command)
                Str = Receive(self.__Connexion, 64)[:-1]
                Str = Str.split(" ")
                Str = Str[1:]

                for v in Str:
                    if v.lower() not in ["dbm", "mw"]:
                        try:
                            Markers.append(float(v))
                        except:
                            pass

            if Axis == 2:
                XYMarkers[1] = Markers
                Markers = XYMarkers

        return Markers


    def DelAllMarkers(self, TraceNumber=1):
        '''
        Deletes all markers of a selected trace
        TraceNumber is an integer between 1 (default) and 6
        '''
        from Hardware.PyApex.Constantes import APXXXX_ERROR_ARGUMENT_TYPE, APXXXX_ERROR_ARGUMENT_VALUE
        from Hardware.PyApex.Errors import ApexError

        if not isinstance(TraceNumber, int):
            raise ApexError(APXXXX_ERROR_ARGUMENT_TYPE, "TraceNumber")
            sys.exit()

        if not TraceNumber in self.__Validtracenumbers:
            raise ApexError(APXXXX_ERROR_ARGUMENT_VALUE, "TraceNumber")
            sys.exit()

        Markers = []
        if not self.__Simulation:
            Command = "SPMKRDELAL" + str(TraceNumber) + "\n"
            Send(self.__Connexion, Command)


    def LineWidth(self, TraceNumber=1, Get="width"):
        '''
        Gets the 3-db line width of the selected trace
        TraceNumber is an integer between 1 (default) and 6
        ThresholdValue is a float expressed in dB
        Get is a string between the following values:
            - Get = "WIDTH" : only the line width is returned (default)
            - Get = "CENTER" : only the line width center is returned
            - Get = "LEVEL" : only the line width peak level is returned
            - Get = "ALL" : all line width values are returned in a list
        '''
        from Hardware.PyApex.Constantes import APXXXX_ERROR_ARGUMENT_TYPE, APXXXX_ERROR_ARGUMENT_VALUE
        from Hardware.PyApex.Errors import ApexError

        if not isinstance(TraceNumber, int):
            raise ApexError(APXXXX_ERROR_ARGUMENT_TYPE, "TraceNumber")
            sys.exit()

        if not TraceNumber in self.__Validtracenumbers:
            raise ApexError(APXXXX_ERROR_ARGUMENT_VALUE, "TraceNumber")
            sys.exit()

        if not self.__Simulation:
            Command = "SPLWTH" + str(TraceNumber) + "_3.0\n"
            Send(self.__Connexion, Command)
            Str = Receive(self.__Connexion, 64)[:-1]
            Values = []
            Str = Str.split("_")

            for s in Str:
                for v in s.split(" "):
                    if v.lower() not in ["dbm", "mw", "nm", "ghz"]:
                        try:
                            Values.append(float(v))
                        except:
                            pass
            while len(Values) < 3:
                Values.append(0.0)

        else:
            Values = [0.100, 1550.000, 2.25]

        if str(Get).lower() == "all":
            return Values

        elif str(Get).lower() == "center":
            return Values[1]

        elif str(Get).lower() == "level":
            return Values[2]

        else:
            return Values[0]


    def SaveToFile(self, FileName, TraceNumber=1, Type="dat"):
        '''
        Save a trace on local hard disk
        FileName is a string representing the path of the file to save
        TraceNumber is an integer between 1 (default) and 6
        Type is the type of the file to save
        Type is a string between the following values:
            - Type = "DAT" : data are saved in a binary format (default)
            - Type = "TXT" : data are saved in a text format
        '''
        from Hardware.PyApex.Constantes import APXXXX_ERROR_ARGUMENT_TYPE, APXXXX_ERROR_ARGUMENT_VALUE, APXXXX_ERROR_BAD_FILENAME
        from Hardware.PyApex.Errors import ApexError
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

        if str(Type).lower() == "txt":
            Type = 1
        else:
            Type = 0

        if not self.__Simulation:
            if Type:
                Command = "SPSAVEB" + str(TraceNumber) + "_" + str(FileName) + "\n"
            else:
                Command = "SPSAVEA" + str(TraceNumber) + "_" + str(FileName) + "\n"
            Send(self.__Connexion, Command)
        print('Data saved to APEX hard drive')


    def LockTrace(self, TraceNumber, Lock):
        '''
        Lock or unlock a trace
        TraceNumber is an integer between 1 and 6
        Lock is a boolean:
            - True: the trace TraceNumber is locked
            - False: the trace TraceNumber is unlocked
        '''
        from Hardware.PyApex.Constantes import APXXXX_ERROR_ARGUMENT_TYPE, APXXXX_ERROR_ARGUMENT_VALUE, APXXXX_ERROR_BAD_FILENAME
        from Hardware.PyApex.Errors import ApexError

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
                Command = "SPTRLOCK" + str(TraceNumber) + "\n"
            else:
                Command = "SPTRUNLOCK" + str(TraceNumber) + "\n"
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
            Command = "SPTRSCROLL" + str(Enable) + "\n"
            Send(self.__Connexion, Command)

