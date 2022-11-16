#!/usr/bin/env python
import socket
#from string import atof, atoi
# import atexit
import numpy as np

from PyQt5.QtCore import QObject, pyqtSignal

class OSA_AQ6370(QObject):
    received_wavelengths = pyqtSignal(object)
    received_spectra = pyqtSignal(object,object)
    received_spectrum = pyqtSignal(np.ndarray,list,list)
    connected = pyqtSignal(int)

    def __init__(self,
                 parent:QObject,
                 host: str,
                 command_port: int,
                 timeout_long: int,
                 timeout_short: int):
        super().__init__(parent=parent)
        self.device=Yokogawa_AQ6370_socket(host, command_port,timeout_long,timeout_short)
        self.device.set_resolution(20)
        self.device.set_sampling_step(2)
        self.device.wait_long()
        self.acquire_spectrum()
        self.channel_num=0
        self._StartWavelength=self.device.get_start_wavelength()
        self._StopWavelength=self.device.get_stop_wavelength()
        self._Span = self._StopWavelength  - self._StartWavelength
        self._Center = self._StartWavelength + (self._Span / 2)


    def acquire_spectrum(self):
        self.device.single_scan()
        self.spectrum= self.device.get_Y_values()
        self.wavelengtharray=self.device.get_X_values()
        self.received_spectrum.emit(self.wavelengtharray,list([self.spectrum]),[0])
        return self.wavelengtharray,self.spectrum


    def acquire_spectra(self):
        self.device.single_scan()
        self.spectrum= self.device.get_Y_values()
        self.wavelengtharray=self.device.get_X_values()
        self.received_spectrum.emit(self.spectrum,self.wavelengtharray)

    def change_range(self,start_wavelength=None,stop_wavelength=None):
        self.device.set_span(start_wavelength,stop_wavelength)

    def SetWavelengthResolution(self,Res:str):
        print('Yokogawa has no High resolution')

    def close(self):
        self.device.close()


class Yokogawa_AQ6370_socket(socket.socket):
    "Optical Spectrum Analyzer ANDO AQ6370 basic methods"
    class Error:
        def __init__ (self, message):
            self.message = message
        def __str__ (self):
            return self.message
        def __repr__ (self):
            return self.message

    def __init__ (self, host, port,timeout_long,timeout_short):
        self.numberOfPointsInTrace=0
        socket.socket.__init__(self, socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.connect((host,port))
        except Exception:
            raise self.OSError(str(host) + ":" + str(port) + ": Error")
        self.settimeout(timeout_long)
        self.timeout_long=timeout_long
        self.timeout_short=timeout_short
        self.send(b"OPEN \"anonymous\"\n\n")
        try:
            self.recv(1024)
        except socket.timeout:
            pass
        self.send(b":ABORt\n")
		# check whether we connect to an device
        self.send(b"*IDN?\n")
        try:
            self.recv(1024).strip()
        except socket.timeout:
            raise self.Error(b"device responce timeout")
        tr=self.recv(1024)
        print('Connected to ', tr)

    def wait_long(self):
        self.settimeout(self.timeout_long)
        self.send(b"*OPC?\n")
        self.recv(1024)

    def single_scan(self):
        self.send(b":INITiate:IMMediate\n");
        self.wait_long()

    def get_NumberOfPoints(self,Trace:str):
        Command = ':TRACe:SNUM? TR'+Trace+'\n'
        self.send(Command.encode('utf-8'))
        return int(self.recv(1024))

    def get_ActiveTrace(self):
        self.device.send(b':TRACe:ACTIVE?\n')
        return self.recv(1024)

    def recieve_whole_message(self):
        self.settimeout(self.timeout_short)
        message = ''
        while True:
            try:
                chunk = self.recv(4096)
            except socket.timeout:
                break
            message+=str(chunk)
        message=message.replace("'","")
        message=message.replace("b","")
        message=message.replace('\\',"")
        message=message.replace('r',"")
        message=message.replace('n',"")
        self.settimeout(self.timeout_long)
        return message


    def get_X_values(self,Trace='A'):
        Command = ':TRACe:X? TR'+Trace+'\n'
        self.send(Command.encode('utf-8'))
        strData=self.recieve_whole_message()
        strData=strData.split(',')
        if not strData:
            print('Did non get any data from the device')
        try:
            X_values=np.array(strData,dtype='f')*1e9
        except:
            print('Error while getting X data')
            X_values=0
        return X_values


    def get_Y_values(self,Trace='A'):
        self.wait_long()
        Command = ':TRACe:Y? TR'+Trace+'\n'
        self.send(Command.encode('utf-8'))
        strData = self.recieve_whole_message()
        strData = strData.split(',')
        if not strData:
                    print('Did non get any data from the device')
        try:
            Y_values=np.array(strData,dtype='f')
        except:
            print('Error while getting Y data')
            Y_values=0
        return Y_values

    def get_start_wavelength(self):
        Command = ':SENSe:WAVelength:STARt?\n'
        self.send(Command.encode('utf-8'))
        return float(self.recv(1024))*1e9

    def get_stop_wavelength(self):
        Command = ':SENSe:WAVelength:STOP?\n'
        self.send(Command.encode('utf-8'))
        return float(self.recv(1024))*1e9

    def set_span(self,start_wavelength=None,stop_wavelength=None):
        if start_wavelength is not None:
            Command = ':SENSe:WAVelength:STARt '+f'{start_wavelength:.3f}'+'NM\n'
            self.send(Command.encode('utf-8'))
        if stop_wavelength is not None:
            Command = ':SENSe:WAVelength:STOP '+f'{stop_wavelength:.3f}'+'NM\n'
            self.send(Command.encode('utf-8'))

    def set_resolution(self,resolution:int):
        Command = ':SENSE:BANDWIDTH:RESOLUTION '+str(resolution)+'PM\n'
        self.send(Command.encode('utf-8'))

    def set_sampling_step(self,step_in_pm=int):
        Command = ':SENSe:SWEep:STEP '+str(step_in_pm)+'PM\n'
        self.send(Command.encode('utf-8'))
#
if __name__ == "__main__":
    try:
        HOST = '10.2.60.20'
        PORT = 10001
        timeout_short = 0.2
        timeout_long = 3
#        device=Yokogawa_AQ6370_socket(HOST, PORT, timeout_long,timeout_short)
        osa=OSA_AQ6370(None,HOST, PORT, timeout_long,timeout_short)
        X,Y=osa.acquire_spectrum()
        osa.change_range(1550.1,1550.2)
        osa.close()
    except:
        print('Error')