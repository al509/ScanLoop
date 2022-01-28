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
from Common.Consts import Consts


class APEX_OSA_with_additional_features(OSA,QObject):
    received_wavelengths = pyqtSignal(object)
    received_spectra = pyqtSignal(object,object)
    received_spectrum = pyqtSignal(np.ndarray,list,list)
    connected = pyqtSignal(int)
    

    def __init__(self,host: str):
        QObject.__init__(self)
        OSA.__init__(self,host)

        
        self.min_wavelength=1526
        self.max_wavelength=1567
        
        self.__SamplingRateForHighRes=20e-6 # in nm
        self.__SamplingRateForLowRes=3e-4 # in nm
        

        temp= np.array(self.GetData())
        self.spectrum=temp[0,::-1]
        self.wavelengtharray=temp[1,::-1]
        self.channel_num=0

        self.SetAutoPointNumberSelection(True)
 
        if self.GetXResolution()<1e-3:
            self.SetNPoints(int((self._StopWavelength-self._StartWavelength)/self.__SamplingRateForHighRes))
            self.IsHighRes=True
        else:
            self.SetNPoints(int((self._StopWavelength-self._StartWavelength)/self.__SamplingRateForLowRes))
            self.IsHighRes=False


    def acquire_spectrum(self):
        a=time.time()
        self.Run(Type='single')
        print('Time elapsed for a single scan is ', time.time()-a)
        if self.IsHighRes:
            self.SaveToFile("D:temp", Type="txt")
            temp = np.loadtxt('//' + Consts.APEX.HOST + '/d/temp_spectrum.txt', skiprows=3, dtype=np.float64)
            self.spectrum=temp[:,1]
            self.wavelengtharray=temp[:,0]
        else:
            temp= (np.array(self.GetData()))
            self.spectrum=temp[0,::-1]
            self.wavelengtharray=temp[1,::-1]
        self.received_spectrum.emit(self.wavelengtharray,list([self.spectrum]),[0])
        return self.wavelengtharray, self.spectrum


    def change_range(self,start_wavelength=None,stop_wavelength=None):
        if (start_wavelength is not None) and (start_wavelength>=self.min_wavelength):
            self.SetStartWavelength(start_wavelength)
            time.sleep(0.1)
        if (stop_wavelength is not None) and (stop_wavelength<=self.max_wavelength):
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
            
 


if __name__=='__main__':
    print(1)
    OSA = APEX_OSA_with_additional_features('10.2.60.25')
    a=OSA.GetMode()
    OSA.ListModes()
    print(a)