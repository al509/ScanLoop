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
    S_toggle_button=pyqtSignal()  # signal to finish
    S_saveSpectrumToOSA=pyqtSignal(str)
    S_add_powers_to_file=pyqtSignal(object) # signal to initiate saving current wavelength and power from powermeter to file

    def __init__(self,
                 OSA:QObject,
                 laser:QObject,
                 powermeter:QObject,
                 laser_power:float,
                 scanstep:float,
                 wavelength_start:float,
                 wavelength_stop:float,
                 file_to_save:str):
        super().__init__()
        
        self.OSA=OSA
        self.step=scanstep
        self.wavelength=wavelength_start
        self.wavelength_stop=wavelength_stop
        self.laser=laser
        self.Power=laser_power
        self.powermeter=powermeter
        self.short_pause=0.1
        self.long_pause=2
        self.tuning=0
        self.hold_wavelength=False
        self.file_to_save=file_to_save
        
    def initialize_laser(self):
        self.laser.setPower(self.Power)
        self.laser.setMode('Whisper')
        self.laser.setWavelength(self.wavelength)
        self.laser.setOn()
        time.sleep(self.long_pause)

    def run(self):
        self.is_running=True
        self.tuning=0
        PowerVSWavelength=[]
        time_start=time.time()
        file=open(self.file_to_save,'a')
        
        while self.is_running and (self.wavelength-self.wavelength_stop)*np.sign(self.step)<0:
            print(self.wavelength)
            if self.OSA is not None:
                wavelengthdata, spectrum=self.OSA.acquire_spectrum()
                time.sleep(0.05)
                Data=np.stack((wavelengthdata, spectrum),axis=1)
                self.S_saveData.emit(Data,'W='+str(self.wavelength)) # save spectrum to file
            if self.powermeter is not None:
                Data=np.stack((time.time()-time_start,self.wavelength, self.powermeter.get_power()))
                file.write(str(Data))
            # if not self.is_running:
            #     self.S_add_powers_to_file.emit(PowerVSWavelength)
            #     self.laser.setOff()
            #     print('Scanning stopped')
            #     self.S_toggle_button.emit()
            #     break
            if not self.hold_wavelength:
                self.tuning+=self.step
                self.wavelength+=self.step*1e-3
                if self.tuning<self.laser.maximum_tuning:
                    self.laser.fineTuning(self.tuning)
                    time.sleep(self.short_pause)
                else:
                    self.tuning=0
                    self.laser.setOff()
                    self.laser.setWavelength(self.wavelength)
                    self.laser.fineTuning(0)
                    self.laser.setOn()
                    time.sleep(self.long_pause)
                self.S_updateCurrentWavelength.emit(str(self.wavelength))

            # if self.is_running and (self.wavelength-self.wavelength_stop)*np.sign(self.step)>0:
            #     self.S_add_powers_to_file.emit(PowerVSWavelength)
            #     self.is_running=False
            #     self.S_toggle_button.emit()
            #     print('\nScanning finished\n')
            #     self.laser.setOff()

        if (self.wavelength-self.wavelength_stop)*np.sign(self.step)>0 : self.S_toggle_button.emit()
        self.laser.setOff()
        print('\nScanning finished\n')
        
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
        self.long_pause=4
        
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
                    if not self.is_running:
                        break
                    self.laser.fineTuning(detuning)
                    time.sleep(self.delay)
                    self.S_updateCurrentWavelength.emit(str(self.wavelength_central+detuning*1e-3))
            else:
                break           
        self.laser.setOff()
        self.S_finished.emit()
        

    def __del__(self):
        print('Closing scanning object...')

if __name__ == "__main__":

       ScanningProcess=ScanningProcess(None,None,1,1,1,1,1,1,1,1,1,1,1)