# -*- coding: utf-8 -*-
"""
Created on Sat Dec  3 15:22:02 2022

@author: Илья
Using lib by Artem Kirik and pyvisa

"""


__date__='2022.12.03'


from Hardware.LaserLibs import itla_pyvisa
import numpy as np

def nmToHz(nm : float):
    return int(299792458 / nm * 1e9)

def dnm_to_dHz(nm:float,d_nm:float):
    return int(299792458/nm**2*d_nm*1e9)

class Laser(serial.Serial):
    
    def __init__(self,COMPort):
        if 'COM' in COMPort:
            COMPort=int(COMPort.split('COM')[1])
        self.itla=itla.PPCL550(COMPort)
        
        self.maximum_tuning=200.1 # in pm
        self.tuning=0
        self.main_wavelength=0 # in nm
    
    def setOn(self):
        self.itla.on()
        print('PPCL550 laser is on')
 
    def setOff(self):
        self.itla.off()
        print('PPCL550 laser is off')
    
    def setPower(self,Power): # in 0.01 dB
        self.itla.set_power(Power)
        print('PPCL550 laser is  with power {} dBm'.format(power*0.01))
    
    def setMode(self, ModeKey):
        modes = {
            'dither' : 0,
            'no dither' : 1,
            'whisper' : 2
            }
        error=True
        while error:
            try: 
                if not (self.ask_value(0x32) & 8):
                    raise ITLA_Error('can be used only when emitting')
                error=False
                return self.talk(1,0x90,0, modes[ModeKey])
            except:
                pass
        

    def setWavelength(self, nm: float): # in nm, accuracy: 0.001 nm
        freq = nmToDGHz(nm)
        self.itla.set_frequency(freq)
        self.main_wavelength=nm
        return

    def fineTuning(self, pm: int): # in pm, accuracy : 0.01 pm
        if pm<self.maximum_tuning:
            dfreq=dnm_to_dHz(self.main_wavelength, pm*1e-3)
            self.itla.set_FTFrequency(dfreq)
            self.tuning=pm
        else:
            print('Tuning larger than max possible')


      def __init__(self, port, timeout = 2000, backend = None):
        super().__init__(port, timeout, backend)
        self.md = self.ask_value(0x90)
    
    def state(self):
        super().state()
        self.md = self.ask_value(0x90)
        return self.__dict__


if __name__=='__main__':
    laser=Laser('COM8')
    del laser



