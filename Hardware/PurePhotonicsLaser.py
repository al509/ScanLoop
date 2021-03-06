import serial
from Hardware import ITLA
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
        self.maximum_tuning=199 # in pm


    def setOn(self):
        return ITLA.ITLA(self, ITLA.REG_Resena, 8, ITLA.WRITE)
    def setOff(self):
        return ITLA.ITLA(self, ITLA.REG_Resena, 0, ITLA.WRITE)
    def setPower(self,Power): # in 0.01 dB
        return ITLA.ITLA(self, ITLA.REG_Power, Power, ITLA.WRITE)
    def setMode(self, ModeKey):
        ModeKeys={
                'Dither':0,
                'Nodither':1,
                'Whisper':2}
        Command=ModeKeys[ModeKey]
        return ITLA.ITLA(self, ITLA.REG_Mode, Command, ITLA.WRITE)

    def setWavelength(self, nm: float): # in nm, accuracy: 0.001 nm
        freq = nmToDGHz(nm)
        THz = freq // 10000
        dGHz = freq % 10000
        ITLA.ITLA(self, ITLA.REG_Fcf1, THz, ITLA.WRITE)
        ITLA.ITLA(self, ITLA.REG_Fcf2, dGHz, ITLA.WRITE)
        return

    def fineTuning(self, pm: int): # in pm, accuracy : 0.01 pm
        C = 299792458
        THz = ITLA.ITLA(self, ITLA.REG_Lf1, 0, ITLA.READ)
        dGHz = ITLA.ITLA(self, ITLA.REG_Lf2, 0, ITLA.READ)
        l1 =  C / (THz + (dGHz * 10 ** (-4)))
        df = -1 * C * pm / (l1 * (l1 + pm))
        dfe = df * (10 ** (6))
        return ITLA.ITLA(self, ITLA.REG_Ftf, np.uint16(dfe), ITLA.WRITE)




if __name__=='__main__':
    laser=Laser('COM8')
    del laser



