'''
By Alexandr Nesterok
Using serial interface
'''
__date__='2023.01.19'


import serial
if __name__=='__main__':
    from LaserLibs import ITLA_serial as ITLA
else:
    from Hardware.LaserLibs import ITLA_serial as ITLA
import numpy as np

def nmToDGHz(nm : float):
    return int(299792458 / nm * 10)

class Laser(serial.Serial):

    def __init__(self,COMPort):
        super().__init__(port=COMPort,
             baudrate=9600,
             parity=serial.PARITY_NONE,
             stopbits=serial.STOPBITS_ONE,
             bytesize=serial.EIGHTBITS,
             timeout = 0.4)
        ITLA.ITLAConnect(COMPort)
        self.maximum_tuning=200.1 # in pm
        self.tuning=0
        self.main_wavelength=0 # in nm
        print('Coonected to laser using Serial')


    def setOn(self):
        print('try to set laser on')
        return ITLA.ITLA(self, ITLA.REG_Resena, 8, ITLA.WRITE)

    def setOff(self):
        print('try to set laser off')
        return ITLA.ITLA(self, ITLA.REG_Resena, 0, ITLA.WRITE)
    def setPower(self,Power): # in 0.01 dB
        return ITLA.ITLA(self, ITLA.REG_Power, Power, ITLA.WRITE)
    def setMode(self, ModeKey):
        ModeKeys={
                'dither':0,
                'no dither':1,
                'whisper':2}
        Command=ModeKeys[ModeKey]
        return ITLA.ITLA(self, ITLA.REG_Mode, Command, ITLA.WRITE)

    def setWavelength(self, nm: float): # in nm, accuracy: 0.001 nm
        freq = nmToDGHz(nm)
        THz = freq // 10000
        dGHz = freq % 10000
        ITLA.ITLA(self, ITLA.REG_Fcf1, THz, ITLA.WRITE)
        ITLA.ITLA(self, ITLA.REG_Fcf2, dGHz, ITLA.WRITE)
        self.main_wavelength=nm
        return

    def fineTuning(self, pm: int): # in pm, accuracy : 0.01 pm
        if pm<self.maximum_tuning:
            C = 299792458
            THz = ITLA.ITLA(self, ITLA.REG_Lf1, 0, ITLA.READ)
            dGHz = ITLA.ITLA(self, ITLA.REG_Lf2, 0, ITLA.READ)
            l1 =  C / (THz + (dGHz * 10 ** (-4)))
            df = -1 * C * pm / (l1 * (l1 + pm))
            dfe = df * (10 ** (6))
            self.tuning=pm
            return ITLA.ITLA(self, ITLA.REG_Ftf, np.uint16(dfe), ITLA.WRITE)
        else:
            print('Tuning larger than max possible')



if __name__=='__main__':
    laser=Laser('COM26')
    laser.setOn()
    laser.setOff()
    # del laser



