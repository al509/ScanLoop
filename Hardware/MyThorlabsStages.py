# -*- coding: utf-8 -*-
"""
Created on Tue Feb  4 15:08:47 2020

@author: Ilya
"""

from PyQt5.QtCore import QObject,  pyqtSignal
import sys
import os
import numpy as np
import thorlabs_apt as apt

class ThorlabsStages(QObject):
    connected = pyqtSignal()
    stopped = pyqtSignal()
#    StepSize={'X':10,'Y':10,'Z':10}
    Stage_key={'X':None,'Y':None,'Z':None}
    position={'X':0,'Y':0,'Z':0}

    def __init__(self):
        super().__init__()
        
#       
        self.Stage_key['Z'] = apt.Motor(90864301)
        self.Stage_key['X'] = apt.Motor(27255020)

        self.position['X']=self.get_position(self.Stage_key['X'])
        self.position['Z']=self.get_position(self.Stage_key['Z'])

 
    def get_position(self, motor):
        return motor.position

    def shiftOnArbitrary(self, key:str, distance:int):
        device=self.Stage_key[key]
        device.move_by(distance, True)
#        if (result>-1):
        self.position[key]=self.get_position(key)
        self.stopped.emit()



#    def wait_for_stop(self, device_id, interval):
#        print("\nWaiting for stop")
#        result = self.lib.command_wait_for_stop(device_id, interval)
#        print("Result: " + repr(result+1))


    def __del__(self):
        apt.atexit._clear()


if __name__ == "__main__":
    stages=ThorlabsStages()
    d=5
    stages.shiftOnArbitrary('X',d)

    del stages

#################################### CLOSE CONNECTION #######################################



#plt.grid(True)
#plt.plot(Data[1], Data[0])
#plt.xlabel("Wavelength (nm)")
#plt.ylabel("Power (dBm)")
#plt.show()
