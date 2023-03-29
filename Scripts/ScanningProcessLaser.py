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

__date__='2023.03.29'
__version__='1.3'

from PyQt5.QtCore import pyqtSignal, QObject
import numpy as np
import time



class LaserScanningProcess(QObject):
    
    
    is_running=False  ## Variable is "True" during scanning process. Pushing on "scanning" button in main window sets is_running True and start scanning process.

    S_updateCurrentWavelength=pyqtSignal(str) #signal to initiate update the index of the current file in lineEdit_CurrentFile of main window
    S_update_fine_tune=pyqtSignal(str)  # signal to update the current fine tune value
    S_update_main_wavelength=pyqtSignal(str)
    S_saveData=pyqtSignal(object,str) #signal to initiate saving measured spectrum to a file
    S_finished=pyqtSignal()  # signal to finish
    S_saveSpectrumToOSA=pyqtSignal(str)
    S_add_powers_to_file=pyqtSignal(object) # signal to initiate saving current wavelength and power from powermeter to file
    
    S_print=pyqtSignal(str) # signal used to print into main text browser
    S_print_error=pyqtSignal(str) # signal used to print errors into main text browser

    def __init__(self,
                 OSA:QObject,
                 laser:QObject,
                 powermeter:QObject,
                 step:float, # in pm
                 wavelength_start:float, # in nm
                 detuning:float, # in pm
                 max_detuning:float, # in pm
                 file_to_save:str):
        super().__init__()
        
        self.OSA=OSA
        self.powermeter=powermeter
        self.laser=laser
        self.step=step
        self.wavelength=wavelength_start
        self.max_detuning=max_detuning
        self.wavelength_stop=wavelength_start+self.max_detuning*1e-3
        self.short_pause=0.1
        self.long_pause=45
        self.tuning=detuning
        self.hold_wavelength=False
        self.file_to_save=file_to_save
        
        self.OSA_for_laser_scanning=False
        self.powermeter_for_laser_scanning=False
        
    # def initialize_laser(self):
    #     self.laser.setPower(self.Power)
    #     self.laser.setMode('Whisper')
    #     self.laser.setWavelength(self.wavelength)
    #     self.laser.setOn()
    #     time.sleep(self.long_pause)

    def run(self):
        self.is_running=True
        time_start=time.time()
        file=open(self.file_to_save,'a')
        self.wavelength=self.laser.main_wavelength+self.laser.tuning*1e-3
        self.wavelength_stop=self.wavelength_start+self.max_detuning*1e-3*np.sign(self.step)
        
        while self.is_running and (self.wavelength-self.wavelength_stop)*np.sign(self.step)<0:
            
            if self.OSA_for_laser_scanning and self.OSA is not None:
                wavelengthdata, spectrum=self.OSA.acquire_spectrum()
                time.sleep(0.05)
                Data=np.stack((wavelengthdata, spectrum),axis=1)
                self.S_saveData.emit('Data','W='+str(self.wavelength)) # save spectrum to file
            if self.powermeter_for_laser_scanning and self.powermeter is not None:
                power=self.powermeter.get_power()
                file.write('{}\t{}\t{}\n'.format(time.time()-time_start,self.wavelength,power))
            # if not self.is_running:
            #     self.S_add_powers_to_file.emit(PowerVSWavelength)
            #     self.laser.setOff()
            #     print('Scanning stopped')
            #     self.S_toggle_button.emit()
            #     break
            if not self.hold_wavelength:
                self.tuning+=self.step
                self.wavelength+=self.step*1e-3
                if self.tuning<=self.laser.maximum_tuning:
                    self.laser.fineTuning(self.tuning)
                    time.sleep(self.short_pause)
                else:
                    self.tuning=0
                    self.laser.setOff()
                    self.laser.setWavelength(self.wavelength)
                    self.laser.fineTuning(0)
                    self.laser.setOn()
                    self.S_update_main_wavelength.emit('{:.3f}'.format(self.wavelength))
                    self.S_print.emit('setting new main wavelength... Wait {} s'.format(self.long_pause))
                    time.sleep(self.long_pause)
                    
                self.S_updateCurrentWavelength.emit('{:.5f}'.format(self.wavelength))
                self.S_update_fine_tune.emit('{:.2f}'.format(self.tuning))

            # if self.is_running and (self.wavelength-self.wavelength_stop)*np.sign(self.step)>0:
            #     self.S_add_powers_to_file.emit(PowerVSWavelength)
            #     self.is_running=False
            #     self.S_toggle_button.emit()
            #     print('\nScanning finished\n')
            #     self.laser.setOff()

        # if (self.wavelength-self.wavelength_stop)*np.sign(self.step)>0 : 
            
        # self.laser.setOff()
        file.close()
        self.S_finished.emit()

        self.S_print.emit('\nScanning finished\n')
        
    def __del__(self):
        self.S_print.emit('Closing scanning object...')
        
        
        
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

       ScanningProcess=LaserScanningProcess(None,None,1,1,1,1,1,1,1,1,1,1,1)