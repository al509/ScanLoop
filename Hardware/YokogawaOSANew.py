# -*- coding: utf-8 -*-
"""
Created on Wed Nov 13 13:31:09 2019

@author: Adm
"""

#!/usr/bin/env python
import socket
import getopt, sys, datetime
import locale
#from string import atof, atoi
# import atexit
import re
import time
import os
import numpy as np
import traceback

from PyQt5.QtCore import QObject, QThread, pyqtSignal

class OSA_AQ6370(QObject,socket.socket):
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
        self.osa=Yokogawa_AQ6370_socket(host, command_port,timeout_long,timeout_short)
        self.osa.set_resolution(20)
        self.osa.set_sampling_step(4)
        self.osa.wait_long()
        self.wavelengtharray=self.osa.get_X_values()
        self.spectrum=None
        self.channel_num=0
        self.range=[self.osa.get_start_wavelength(),self.osa.get_stop_wavelength()]



    def acquire_spectrum(self):
        self.osa.single_scan()
        self.spectrum= self.osa.get_Y_values()
        self.wavelengtharray=self.osa.get_X_values()
        self.received_spectrum.emit(self.wavelengtharray,list([self.spectrum]),[0])


    def acquire_spectra(self):
        self.osa.single_scan()
        self.spectrum= self.osa.get_Y_values()
        self.wavelengtharray=self.osa.get_X_values()
        self.received_spectrum.emit(self.spectrum,self.wavelengtharray)

    def set_span(self,start_wavelength=None,stop_wavelength=None):
        self.osa.set_span(start_wavelength,stop_wavelength)



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
        except socket.error(code, message):
            raise self.OSError(str(host) + ":" + str(port) + ": " + message)
        self.settimeout(timeout_long)
        self.timeout_long=timeout_long
        self.timeout_short=timeout_short
        self.send(b"OPEN \"anonymous\"\n\n")
        try:
            self.recv(1024)
        except socket.timeout:
            pass
        self.send(b":ABORt\n")
		# check whether we connect to an OSA
        self.send(b"*IDN?\n")
        try:
            data = self.recv(1024).strip()
        except socket.timeout:
            raise self.Error(b"OSA responce timeout")
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
        osa.send(b':TRACe:ACTIVE?\n')
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
            print('Did non get any data from the OSA')
        return np.array(strData,dtype='f')*1e9

    def get_Y_values(self,Trace='A'):
        Command = ':TRACe:Y? TR'+Trace+'\n'
        self.send(Command.encode('utf-8'))
        strData = self.recieve_whole_message()
        strData = strData.split(',')
        if not strData:
                    print('Did non get any data from the OSA')
        return np.array(strData,dtype='f')

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
    import matplotlib.pyplot as plt
    try:
        HOST = '10.2.60.30'
        PORT = 10001
        timeout_short = 0.2
        timeout_long = 10
        osa=Yokogawa_AQ6370_socket(HOST, PORT, timeout_long,timeout_short)
        osa.single_scan()
        X = osa.get_X_values()
        Y=osa.get_Y_values()
        print(osa.get_stop_wavelength())
#        osa.set_span(start_wavelength=1543,stop_wavelength=1544)
        osa.close()
    except Exception as e:
        traceback.print_exc()
        osa.close()


