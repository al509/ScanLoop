# -*- coding: utf-8 -*-
"""
Created on Fri May 28 13:02:47 2021

@author: Ilya
"""
import visa
from PyQt5.QtCore import QObject


class PowerMeter(QObject):
    """
    Thorlabs PM100D power meter
    NOTE: You may need to switch drivers through  Thorlabs Optical Power Monitor program
    
    uses the PyVISA library to communicate over USB.
    """
    
    def __init__(self,SerialNumber):
        
        def FindDevice(SerialNumber) : #SerialNumber of Console
            rm = visa.ResourceManager()
            a=rm.list_resources()	
            print(a)
            for b in a :
                if b.find('USB') > -1  :
                    h=rm.open_resource(b)
                    h.write("*IDN?")
                    if ((h.read()).split(',')[2]==SerialNumber): return h
                    else: continue	
            print('No desirable device found')
            return None
        
        super().__init__()
        self.device=FindDevice(SerialNumber)
        
     
    def get_power(self):
        self.device.write("READ?")
        return float(self.device.read())
    
if __name__=='__main__':
    PM=PowerMeter('P0015055')
    print(PM.get_power())
    
    
        