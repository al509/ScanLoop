# -*- coding: utf-8 -*-
"""
Created on Tue Jun  9 16:58:51 2020

@author: User
"""

# -*- coding: utf-8 -*-
"""
Created on Tue Nov 20 19:09:12 2018

Version Nov 22 2019
@author: Ilya
"""

from PyQt5.QtCore import pyqtSignal, QObject
import numpy as np
import time



class LaserScanningProcess(QObject):
    is_running=False  ## Variable is "True" during scanning process. Pushing on "scanning" button in main window sets is_running True and start scanning process.

    S_updateCurrentWavelength=pyqtSignal(str) #signal to initiate update the index of the current file in lineEdit_CurrentFile of main window
    S_saveData=pyqtSignal(object,str) #signal to initiate saving measured spectrum to a file
    S_finished=pyqtSignal()  # signal to finish


    def __init__(self,
                 OSA:QObject,
                 laser:QObject,
                 laser_power:float,
                 scanstep:float,
                 wavelength_start:float,
                 wavelength_stop:float):
        super().__init__()
        self.OSA=OSA
        self.step=scanstep
        self.wavelength=wavelength_start
        self.wavelength_stop=wavelength_stop
        self.laser=laser
        self.Power=laser_power

        self.short_pause=0.5
        self.long_pause=10

    def run(self):
        self.is_running=True
        self.laser.setPower(self.Power)
        self.laser.setMode('Whisper')
        self.laser.setWavelength(self.wavelength)
        self.laser.setOn()
        time.sleep(self.long_pause)
        tuning=0
        while self.is_running and self.wavelength<self.wavelength_stop:
            print(self.wavelength)
            wavelengthdata, spectrum=self.OSA.acquire_spectrum()
            time.sleep(0.05)
            Data=np.stack((wavelengthdata, spectrum),axis=1)
            self.S_saveData.emit(Data,'W='+str(self.wavelength)) # save spectrum to file
            if not self.is_running:
                self.laser.setOff()
                break
            tuning+=self.step
            self.wavelength+=self.step*1e-3
            if tuning<self.laser.maximum_tuning:
                self.laser.fineTuning(tuning)
                time.sleep(self.short_pause)
            else:
                tuning=0
                self.laser.setOff()
                self.laser.setWavelength(self.wavelength)
                self.laser.fineTuning(0)
                self.laser.setOn()
                time.sleep(self.long_pause)
            self.S_updateCurrentWavelength.emit(str(self.wavelength))

            if self.is_running and self.wavelength>self.wavelength_stop:
                self.is_running=False
                print('\nScanning finished\n')
                self.laser.setOff()
        self.S_finished.emit()
        self.laser.setOff()

    def __del__(self):
        print('Closing scanning object...')
        
        
        
class LaserSweepingProcess(QObject):
    is_running=False  ## Variable is "True" during scanning process. Pushing on "scanning" button in main window sets is_running True and start scanning process.

    S_updateCurrentWavelength=pyqtSignal(str) #signal to initiate update the index of the current file in lineEdit_CurrentFile of main window
    S_saveData=pyqtSignal(object,str) #signal to initiate saving measured spectrum to a file
    S_finished=pyqtSignal()  # signal to finish


    def __init__(self,
                 laser:QObject,
                 laser_power:float,
                 scanstep:float,
                 wavelength_central:float,
                 max_detuning:float,
                 delay: float):
        super().__init__()
        self.step=scanstep
        self.wavelength_central=wavelength_central
        self.max_detuning=max_detuning
        self.laser=laser
        self.Power=laser_power
        self.delay=delay

        self.short_pause=0.005
        self.long_pause=10
        
        self.detuning_array=np.arange(-max_detuning,max_detuning,scanstep)
        
    def run(self):
        self.is_running=True
        self.laser.setPower(self.Power)
        self.laser.setMode('Whisper')
        self.laser.setWavelength(self.wavelength_central)
        self.laser.setOn()
        time.sleep(self.long_pause)
       
        while self.is_running:
            if self.is_running:
                for detuning in self.detuning_array:
                    self.laser.fineTuning(detuning)
                    time.sleep(self.delay)
                    self.S_updateCurrentWavelength.emit(str(self.detuning))
                    if not self.is_running:
                        break
            else:
                break           
        self.laser.setOff()
        self.S_finished.emit()
        

    def __del__(self):
        print('Closing scanning object...')

if __name__ == "__main__":

       ScanningProcess=ScanningProcess(None,None,1,1,1,1,1,1,1,1,1,1,1)