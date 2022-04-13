# -*- coding: utf-8 -*-
"""
Created on Fri May 28 13:02:47 2021

@author: Ilya
"""
import pyvisa as visa
from PyQt5.QtCore import QObject, pyqtSignal
import time


class PowerMeter(QObject):
    """
    Thorlabs PM100D power meter
    NOTE: You may need to switch drivers through  Thorlabs Optical Power Monitor program
    
    uses the PyVISA library to communicate over USB.
    """
    power_received=pyqtSignal(float,float)
    
    def __init__(self,SerialNumber):
        
        
        def FindDevice(SerialNumber) : #SerialNumber of Console
            rm = visa.ResourceManager()
            a=rm.list_resources()	
            for b in a :
                if b.find('USB') > -1  :
                    h=rm.open_resource(b)
                    h.write("*IDN?")
                    if ((h.read()).split(',')[2]==SerialNumber): 
                        print('connected to powermeter')
                        return h
                    else: continue	
            print('No desirable device found')
            return None
        
        super().__init__()
        self.device=FindDevice(SerialNumber)
        

        
     
    def get_power(self):
        self.device.write("READ?")
        power=float(self.device.read())
        self.power_received.emit(power,time.time())
        return power
    
if __name__=='__main__':
    PM=PowerMeter('P0015055')
    print(PM.get_power())
    
    
        