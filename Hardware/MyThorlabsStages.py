# -*- coding: utf-8 -*-
"""
Created on Tue Feb  4 15:08:47 2020

@author: Ilya
"""


'''
NOTE that positions are in steps 2/5 micron each!
'''


from PyQt5.QtCore import QObject,  pyqtSignal
import sys
import os
import numpy as np
import Hardware.thorlabs_apt as apt

class ThorlabsStages(QObject):
    connected = pyqtSignal()
    stopped = pyqtSignal()
#    StepSize={'X':10,'Y':10,'Z':10}
    Stage_key={'X':None,'Y':None,'Z':None}
    position={'X':0,'Y':0,'Z':0}

    def __init__(self):
        super().__init__()

#
        try:
            self.Stage_key['X'] = apt.Motor(27255020)
        except Exception as e:
            print('Error while initializing Cub 27255020 stage: ' + str(e))
        try:
            self.Stage_key['X'].backlash_distance(0)
            self.Stage_key['X'].set_velocity_parameters(0, 1, 2.4)
            self.Stage_key['X'].set_move_home_parameters(2, 1, 2.0, 0.0001)
            self.Stage_key['X'].move_home(True)
        except Exception as e:
            print('Error while configuring Cub 27255020 stage: '+ str(e))
        try:
            self.Stage_key['Z'] = apt.Motor()
        except Exception as e:
            print('Error while initializing NRT 90864301 stage: ' + str(e))
        try:
            self.Stage_key['Z'].backlash_distance(0)
            self.Stage_key['Z'].set_move_home_parameters(2, 1, 2.0, 0.0001)
            self.Stage_key['Z'].move_home(False)
        except Exception as e:
            print('Error while configuring NRT 90864301 stage: '+ str(e))
        
        try:
            self.position['X']=self.get_position('X')
            self.position['Z']=self.get_position('Z')
        except Exception as e:
            print('cannot take positions of stages: ' + str(e))
        self.IsConnected=1


    def get_position(self, key):
        #for the sage of uniformity, distance is shown in steps 2.5 um each
        motor=self.Stage_key[key]
        return round(motor.position*1e3/2.5)

    def shiftOnArbitrary(self, key:str, distance:int):
        #for the sage of uniformity, distance is shown in steps 2.5 um each
        device=self.Stage_key[key]
        device.move_by(distance*2.5e-3, True)
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
    d=0.5
    stages.shiftOnArbitrary('X',d)

    del stages

#################################### CLOSE CONNECTION #######################################



#plt.grid(True)
#plt.plot(Data[1], Data[0])
#plt.xlabel("Wavelength (nm)")
#plt.ylabel("Power (dBm)")
#plt.show()
