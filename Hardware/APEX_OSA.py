"""
Version Oct 18 2019
@author: Ilya
"""

import socket
import os, sys, re
import numpy as np
from PyQt5.QtCore import QObject, QThread, pyqtSignal
from os.path import isdir, dirname
from random import random
from math import log10
import time

from Hardware.PyApex.AP2XXX import AP2XXX
from Hardware.PyApex.AP2XXX.osa import OSA


class APEX_OSA_with_additional_features(OSA,QObject):
    received_wavelengths = pyqtSignal(object)
    received_spectra = pyqtSignal(object,object)
    received_spectrum = pyqtSignal(np.ndarray,list,list)
    connected = pyqtSignal(int)

    def __init__(self,host: str):
        QObject.__init__(self)
        OSA.__init__(self,host)


        self.__SamplingRateForHighRes=20e-6 # in nm
        self.__SamplingRateForLowRes=3e-4 # in nm
        

        temp= np.array(self.GetData())
        self.spectrum=temp[0,::-1]
        self.wavelengtharray=temp[1,::-1]
        self.channel_num=0

        self.SetAutoPointNumberSelection(True)
 
        if abs(self.GetXResolution()-4e-5)<1e-6:
            self.SetNPoints(int((self._StopWavelength-self._StartWavelength)/self.__SamplingRateForHighRes))
            self.IsHighRes=True
        else:
            self.SetNPoints(int((self._StopWavelength-self._StartWavelength)/self.__SamplingRateForLowRes))
            self.IsHighRes=False


    def acquire_spectrum(self):
        a=time.time()
        self.Run(Type='single')
        print('Time elapsed for a single scan is ', time.time()-a)
        temp= (np.array(self.GetData()))
        self.spectrum=temp[0,::-1]
        self.wavelengtharray=temp[1,::-1]
        self.received_spectrum.emit(self.wavelengtharray,list([self.spectrum]),[0])
        return self.wavelengtharray, self.spectrum


    def change_range(self,start_wavelength=None,stop_wavelength=None):
        if start_wavelength is not None:
            self.SetStartWavelength(start_wavelength)
            time.sleep(0.1)
        if stop_wavelength is not None:
            self.SetStopWavelength(stop_wavelength)
            time.sleep(0.1)
        if self.IsHighRes:
            self.SetNPoints(int((self._StopWavelength-self._StartWavelength)/self.__SamplingRateForHighRes))
        else:
            self.SetNPoints(int((self._StopWavelength-self._StartWavelength)/self.__SamplingRateForLowRes))
            
    def SetWavelengthResolution(self,Res:str):
        if Res=='Low':
            self.SetXResolution(0.00112)
            self.SetNPoints(int((self._StopWavelength-self._StartWavelength)/self.__SamplingRateForLowRes))
            self.IsHighRes=False
        elif Res=='High':
            self.SetXResolution(0.00004)
            self.SetNPoints(int((self._StopWavelength-self._StartWavelength)/self.__SamplingRateForHighRes))
            self.IsHighRes=True
            
 


if '__name__'=='__main__':
    OSA = APEX_OSA_with_additional_features('10.2.60.25')
    print(OSA.GetMode())
