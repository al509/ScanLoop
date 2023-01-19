# -*- coding: utf-8 -*-
"""
Created on Sat Dec  3 15:22:02 2022

@author: Илья
Using lib by Artem Kirik and pyvisa

"""


__date__='2022.12.03'

if __name__=='__main__':

    from LaserLibs import itla_pyvisa
else:
    
    from Hardware.LaserLibs import itla_pyvisa
    
import numpy as np

def nmToHz(nm : float):
    return int(299792458 / nm * 1e9)

def dnm_to_dHz(nm:float,d_nm:float):
    return -int(299792458/nm**2*d_nm*1e9)

class Laser():
    
    def __init__(self,COMPort):
        if type(COMPort)==str and 'COM' in COMPort:
            COMPort=int(COMPort.split('COM')[1])
        self.itla=itla_pyvisa.PPCL550(COMPort)
        print('connected to laser')        
        self.maximum_tuning=200.1 # in pm
        self.tuning=0
        self.main_wavelength=1550 # in nm
    
    def setOn(self):
        self.itla.on()
        print('PPCL550 laser is on')
 
    def setOff(self):
        self.itla.off()
        print('PPCL550 laser is off')
    
    def setPower(self,Power): # in 0.01 dB
        self.itla.set_power(int(Power))
        print('PPCL550 laser is  with power {} dBm'.format(Power*0.01))
    
    def setMode(self, ModeKey):
        modes = {
            'dither' : 0,
            'no dither' : 1,
            'whisper' : 2
            }
        error=True
        while error:
            try: 
                self.itla.mode(ModeKey) 
                error=False          
                print('PPCL550 laser mode {} is set'.format(ModeKey))
            except:
                pass
        

    def setWavelength(self, nm: float): # in nm, accuracy: 0.001 nm
        freq = nmToHz(nm)
        self.itla.set_frequency(freq)
        self.main_wavelength=nm
        return

    def fineTuning(self, pm: float): # in pm, accuracy : 0.01 pm
        if pm<self.maximum_tuning:
            dfreq=dnm_to_dHz(self.main_wavelength, pm*1e-3)
            self.itla.set_FTFrequency(dfreq)
            self.tuning=pm
        else:
            print('Tuning larger than max possible')


    
    def state(self):
        super().state()
        self.md = self.ask_value(0x90)
        return self.__dict__


if __name__=='__main__':
    import os
    os.chdir('..')
    # from LaserLibs import itla_pyvisa
    laser=Laser(26)
    laser.setOn()
    laser.setMode('whisper')
    laser.setOff()



