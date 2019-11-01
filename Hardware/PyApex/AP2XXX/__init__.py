import socket
import os, sys, re

from Hardware.PyApex.Common import Send, Receive

class AP2XXX():
    '''
    DESCRIPTION
        Elementary functions to communicate with Apex AP2XXX equipment (OSA and OCSA)
        This class can control :
            - The heterodyne OSA
            - The polarimeter without spectrum (option)
            - The optical filter (option)
            - The filters OSA (option)
            - The powermeter
            - The tunable laser in static mode (option)

    VERSION
        2.0

    CONTRIBUTORS
        Maxime FONTAINE
        Khalil KECHAOU
        Vincent PERNET
    '''
#    Connexion = socket.socket(socket.AF_INET , socket.SOCK_STREAM)
    def __init__(self, IPaddress, PortNumber=5900, Simulation=False):
        '''
        Constructor of AP2XXX equipment.z
        IPaddress is the IP address (string) of the equipment.
        PortNumber is by default 5900. It's an integer
        Simulation is a boolean to indicate to the program if it has to run in simulation mode or not
        '''

        self.__IPAddress = IPaddress
        self.__PortNumber = PortNumber
        self.__Simulation = Simulation
        self.__Connected = False
        self.Connexion = socket.socket(socket.AF_INET , socket.SOCK_STREAM)
        # Connexion to the equipment
        self.Open()


    def Reconnect(self):
        self.Close()
        self.Open()
    
    def Open(self):
        '''
        Open connexion to AP2XXX equipment.
        This method is called by the constructor of AP2XXX class
        '''
        self.Connexion = socket.socket(socket.AF_INET , socket.SOCK_STREAM)
        self.Connexion.settimeout(10.0)

        if self.__Simulation:
            self.__Connected = True
            print("Connected successfully to the equipment")
        else:
            try:
                self.Connexion.connect((self.__IPAddress, self.__PortNumber))
                self.__Connected = True
                print("Connected successfully to the equipment")
            except:
                print("Cannot connect to the equipment")


    def Close(self):
        '''
        Close connexion to AP2XXX equipment
        '''
        from Hardware.PyApex.Constantes import APXXXX_ERROR_COMMUNICATION
        from Hardware.PyApex.Errors import ApexError

        if self.__Simulation:
            self.__Connected = False
        else:
            try:
                self.Connexion.close()
                self.__Connected = False
            except:
                raise ApexError(APXXXX_ERROR_COMMUNICATION, self.Connexion.getsockname()[0])
                sys.exit()


    def IsConnected(self):
        '''
        Returns the status of the connection. True if an equipment
        is connected, False otherwise.
        '''
        return self.__Connected


    def SetTimeOut(self, TimeOut):
        '''
        Set the timeout of the Ethernet connection
        TimeOut is expressed in seconds
        In some functions like 'OSA.Run()', the timeout is disabled
        '''
        from Hardware.PyApex.Constantes import APXXXX_ERROR_ARGUMENT_TYPE

        if not isinstance(TimeOut, (int, float)):
            raise ApexError(APXXXX_ERROR_ARGUMENT_TYPE, "TimeOut")

        self.Connexion.settimeout(TimeOut)


    def GetTimeOut(self):
        '''
        Get the timeout of the Ethernet connection
        The returned value is expressed in seconds
        '''

        TimeOut = self.Connexion.gettimeout()
        return TimeOut


    def GetID(self):
        '''
        Return string ID of AP2XXX equipment
        '''
        from Hardware.PyApex.Constantes import SimuAP2XXX_ID

        if self.__Simulation:
            return SimuAP2XXX_ID
        else:
            Send(self.Connexion, "*IDN?\n")
            ID = Receive(self.Connexion)
            return ID


    def GetType(self):
        '''
        Return the type of the OSA. For example "AP2061" for an AP2061
        '''
        from Hardware.PyApex.Errors import ApexError
        import re

        Type = self.GetID()
        Type = self.__ID.split("/")[1]
        Type = "AP" + Type
        return Type


    def ListModes(self):
        '''
        Gets a list of all modes in the AP2XXX equipment.
        These modes are expressed as string. The index of the element in the list
        follows the list in the AP2XXX menu box
        '''

        if self.__Simulation:
            Modes = ["Apex Start", "General Settings", "Powermeter", "T.L.S", "O.S.A."]
        else:
            Send(self.Connexion, "LSMODES?\n")
            Modes = Receive(self.Connexion)[:-1]
            Modes = Modes.split(",")
            for i in range(len(Modes)):
                Modes[i] = Modes[i].strip()

        return Modes


    def SetMode(self, Mode):
        '''
        Changes the screen mode of the AP2XXX equipment (Apex Start, O.S.A., Powermeter)
        Mode is an integer representing the index of the mode to display.
        By convention, the "APEX Start" mode is always 0 index. The index follows the
        list in the AP2XXX menu box.
        '''
        from Hardware.PyApex.Constantes import APXXXX_ERROR_ARGUMENT_TYPE

        TimeOut = self.Connexion.gettimeout()
        self.Connexion.settimeout(None)

        if not isinstance(Mode, (int)):
            raise ApexError(APXXXX_ERROR_ARGUMENT_TYPE, "Mode")

        if not self.__Simulation:
            Send(self.Connexion, "CHMOD" + str(Mode) + "\n")

        self.Connexion.settimeout(TimeOut)


    def GetMode(self):
        '''
        Gets the actual mode of the AP2XXX equipment (Apex Start, O.S.A., Powermeter...)
        The returned mode is an integer representing the index of the displayed mode.
        The mode string can be defined by finding the element in the list returned by
        the function ListModes()
        '''
        from random import randint

        if self.__Simulation:
            Mode = randint(0, 6)
        else:
            Send(self.Connexion, "CHMOD?\n")
            Mode = Receive(self.Connexion)[:-1]
            try:
                Mode = int(Mode)
            except:
                Mode = 0

        return Mode


    def DisplayScreen(self, Display):
        '''
        Displays or not the "Remote" window on the AP2XXX equipment.
        Display is a boolean:
            - True: the window is displayed
            - False: the window is hidden
        '''

        if Display == False:
            Display = 0
        else:
            Display = 1

        if not self.__Simulation:
            Send(self.Connexion, "REMSCREEN" + str(Display) + "\n")


    def ListBands(self):
        '''
        Gets a list of all optical bands in the AP2XXX equipment.
        The optical band choice is only available for AP2X8X
        '''

        if self.__Simulation:
            Bands = ["O", "C&L"]
        else:
            Send(self.Connexion, "LSBANDS?\n")
            Bands = Receive(self.Connexion)[:-1]
            Bands = Bands.split(",")
            for i in range(len(Bands)):
                Bands[i] = Bands[i].replace("&&", "&")
                Bands[i] = Bands[i].strip()

        return Bands


    def GetOpticalBand(self):
        '''
        Gets the actual optical band. The band can be:
            - O
            - C&L
        The optical band choice is only available for AP2X8X
        '''
        from random import randint

        if self.__Simulation:
            Bands = ["0", "C&L"]
            Band = Bands[randint(0, 1)]
        else:
            Send(self.Connexion, "CHBAND?\n")
            Band = Receive(self.Connexion)[:-1]
            Band = Band.replace("&&", "&")

        return Band


    def SetOpticalBand(self, Band):
        '''
        Sets the optical band. The band can be:
        The available bands can be listed by the 'ListBands' command
        The optical band choice is only available for AP2X8X
        '''
        from Hardware.PyApex.Constantes import APXXXX_ERROR_ARGUMENT_TYPE

        if not isinstance(Band, (str)):
            raise ApexError(APXXXX_ERROR_ARGUMENT_TYPE, "Band")

        ValidBands = self.ListBands()
        index = -1
        for vb in ValidBands:
            if Band.lower() == vb.lower():
                index = ValidBands.index(vb)

        if not self.__Simulation and index >= 0:
            Send(self.Connexion, "CHBAND" + str(index) + "\n")


#
#    def OSA(self):
#        '''
#        Return an OSA object for using the Heterodyne AP2XXX OSA
#        '''
#        from Hardware.PyApex.AP2XXX.osa import OSA
#        return OSA(self, self.__Simulation)
#
#
#    def OCSA(self):
#        '''
#        Return an OCSA object for using the Heterodyne AP2XXX OCSA
#        '''
#        from Hardware.PyApex.AP2XXX.ocsa import OCSA
#        return OCSA(self, self.__Simulation)
#
#
#    def TLS(self):
#        '''
#        Return a TLS object for using the Tunable Laser Source of the AP2XXX
#        '''
#        from Hardware.PyApex.AP2XXX.tls import TunableLaser
#        return TunableLaser(self, self.__Simulation)
#
#
#    def Powermeter(self):
#        '''
#        Return a Powermeter object for using the embedded powermeter of the AP2XXX
#        '''
#        from Hardware.PyApex.AP2XXX.powermeter import Powermeter
#        return Powermeter(self, self.__Simulation)
#
#
#    def OsaFs(self):
#        '''
#        Return an OSA Fast-Sweep object for using the OSA Fast Sweep of the AP207X
#        Only available with the AP207X equipment
#        '''
#        from Hardware.PyApex.AP2XXX.osafs import OsaFs
#        return OsaFs(self, self.__Simulation)
#
#
#    def Polarimeter(self):
#        '''
#        Return a Polarimeter object for using the embedded polarimeter of the AP2XXX
#        Available only with the option OSA-12
#        '''
#        from Hardware.PyApex.AP2XXX.polarimeter import Polarimeter
#        return Polarimeter(self, self.__Simulation)
#
#
#    def Filter(self):
#        '''
#        Return a Filter object for using the embedded optical filter of the AP2XXX
#        Available only with the option OSA-12
#        '''
#        from Hardware.PyApex.AP2XXX.filter import Filter
#        return Filter(self, self.__Simulation)
#
#
#
#



