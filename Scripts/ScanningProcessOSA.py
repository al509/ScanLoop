# -*- coding: utf-8 -*-
"""
Created on Tue Nov 20 19:09:12 2018


@author: Ilya
"""

__data__='2022.03.31'

from PyQt5.QtCore import pyqtSignal, QObject
import numpy as np
import winsound
import time



class ScanningProcess(QObject):
  

    S_update_status=pyqtSignal(str) #signal to initiate update the index of the current file in lineEdit_CurrentFile of main window
    S_saveData=pyqtSignal(object,str) #signal to initiate saving measured spectrum to a file
    S_saveSpectrumToOSA=pyqtSignal(str) # signal used if high resolution needed. Initiate saving spectral data to inner hard drive of OSA
    S_addPosition_and_FilePrefix=pyqtSignal(str) #signal to initiate saving current position of the stages and current file index to file "Positions.txt"
    S_finished=pyqtSignal()  # signal to finish

    minimumPeakHight=1

    def __init__(self):
        super().__init__()
        self.OSA=None # add Optical Spectral Analyzer
        self.stages=None # add all three stages
        self.FullSpan=10
        self.IsHighRes=False

        self.scanning_step=30
        self.seeking_step=30
        self.backstep=30    #in microns, to move stage axis_to_get_contact to loose the contact
        self.level_to_detect_contact=-3  # dBm, used to determine if there is contact between the taper and the sample. see function checkIfContact for details
        self.current_file_index=1
        self.stop_file_index=100
        self.number_of_scans_at_point=1
        self.is_squeeze_span=False
        self.is_seeking_contact=False
        self.is_follow_peak=False
        
        self.save_out_of_contact=False
        self.LunaJonesMeasurement=False
        
        self.scanning_type='Along Z, get contact along X'
        self.axis_to_scan='Z'
        self.axis_to_get_contact='X'
        
        self.is_running=False  ## Variable is "True" during scanning process. Pushing on "scanning" button in main window sets is_running True and start scanning process.
    ### Another pushing on "scanning" button during the scanning proccess set is_running to "False" and interrupt the scanning process

        span_for_scanning=0.05 #nm, Value of span in searching_contact function. Used if is_squeeze_span==True

        IsInContact=False # True - when taper is in contact with the sample
        
    def set_parameters(self,dictionary):
        for key in dictionary:
            try:
                self.__setattr__(key, dictionary[key])
            except:
                pass
        self.set_axes()
                
    def get_parameters(self)->dict:
        '''
        Returns
        -------
        Seriazible attributes of the object
        '''
        d=dict(vars(self)).copy() #make a copy of the vars dictionary
        del d['stages']
        del d['OSA']
        return d
    
    def update_OSA_parameters(self):
        try:
            self.FullSpan=self.OSA._Span
        except:
            pass
        try:
            self.IsHighRes=self.OSA.IsHighRes
        except:
            self.IsHighRes=False

    def set_axes(self): # set axis depending on choice in MainWindow
        s=self.scanning_type
        self.axis_to_get_contact=s.split(', get contact along ')[1]
        self.axis_to_scan=s.split(', get contact along ')[0].split('Along ')[1]
       

    def set_OSA_to_Searching_Contact_State(self): #set rough resolution and narrowband span
        print(self.OSA._Span)
        self._FullSpan=self.OSA._Span
        self.IsHighRes=self.OSA.IsHighRes

        self.OSA.SetMode(3) # set APEX OSA to O.S.A. mode - it works faster
        self.OSA.SetSpan(self.span_for_scanning)

        if self.IsHighRes:
            self.OSA.SetWavelengthResolution('Low')
        time.sleep(0.05)
        print("OSA's range is squeezed")

    def set_OSA_to_Measuring_State(self): #set back  resolution and preset span
        self.OSA.SetMode(4) # set APEX OSA to Tracking Generator mode back
        self.OSA.SetSpan(self._FullSpan)
        if self.IsHighRes:
            self.OSA.SetWavelengthResolution('High')

        time.sleep(0.05)
        print("OSA's range is set to initial")

    def search_contact(self): ## move taper towards sample until contact has been obtained
        wavelengthdata, spectrum=self.OSA.acquire_spectrum()
        time.sleep(0.05)
        self.IsInContact=self.checkIfContact(spectrum) #check if there is contact already
        while not self.IsInContact:
            self.stages.shiftOnArbitrary(self.axis_to_get_contact,self.seeking_step)
            print('Moved to Sample')
            wavelengthdata, spectrum=self.OSA.acquire_spectrum()
            time.sleep(0.05)
            self.IsInContact=self.checkIfContact(spectrum)
            if not self.is_running : ##if scanning process is interrupted,stop searching contact
                if self.is_squeeze_span:
                    self.set_OSA_to_Measuring_State()
                    self.OSA.acquire_spectrum()
                return 0
        print('\nContact found\n')
        winsound.Beep(1000, 500)

    def losing_contact(self): ##move taper away from sample until contact is lost
        while self.IsInContact:
            self.stages.shiftOnArbitrary(self.axis_to_get_contact,-self.backstep)
            print('Moved Back from Sample')
            wavelengthdata,spectrum=self.OSA.acquire_spectrum()
            time.sleep(0.05)
            self.IsInContact=self.checkIfContact(spectrum)
            if not self.is_running : ##if scanning process is interrupted,stop searching contact
                if self.is_squeeze_span:
                    self.set_OSA_to_Measuring_State()
                    self.OSA.acquire_spectrum()
                return 0
        print('\nContact lost\n')

    def checkIfContact(self, spectrum):  ## take measured spectrum and decide if there is contact between the taper and the sample
        mean=np.mean(spectrum)
        print(mean)
        if mean<self.level_to_detect_contact:
            return True
        else:
            return False


    """
    Main function
    """
    def run(self):
        time.sleep(0.05)
        ### main loop
        self.set_axes()
        self.update_OSA_parameters()
        if self.is_squeeze_span:  ## to speed up the process of the getting contact, the very narrow span of OSA can be set
            self.set_OSA_to_Searching_Contact_State()
        while self.is_running and self.current_file_index<self.stop_file_index+1:
            self.S_update_status.emit('Step {} of {}'.format(self.current_file_index,self.stop_file_index))
            if self.save_out_of_contact:
                wavelengths_background,background_signal=self.OSA.acquire_spectrum()
                self.S_saveData.emit(np.stack((wavelengths_background, background_signal),axis=1),'p='+str(self.current_file_index)+'_out_of_contact') # save Jones matrixes to Luna for out of contact
                                

            time0=time.time()
            ## Getting in contact between the taper and the sample
            if self.is_seeking_contact:
                self.search_contact()
            else:
                self.stages.shiftOnArbitrary(self.axis_to_get_contact,self.seeking_step)

            if self.is_squeeze_span:   ## after contact is found, set the span of OSA back to span of interest
                self.set_OSA_to_Measuring_State()

            ## Acquring and saving data
            for jj in range(0,self.number_of_scans_at_point):
                print('saving sweep # ', jj+1)
                wavelengthdata, spectrum=self.OSA.acquire_spectrum()
                time.sleep(0.05)
                
                Data=np.stack((wavelengthdata, spectrum),axis=1)
                self.S_saveData.emit(Data,'p='+str(self.current_file_index)+'_j='+str(jj)) # save spectrum to file
                if not self.is_running: break

            #update indexes in MainWindow and save positions into "Positions.txt"

            if self.is_follow_peak and max(spectrum)-min(spectrum)>self.minimumPeakHight:
                self.OSA.SetCenter(wavelengthdata[np.argmin(spectrum)])



            ## Loosing contact between the taper and the sample
            if not self.is_running:
                break

            if self.is_squeeze_span: ## to speed up the process of losing contact, the very narrow span of OSA can be set
                self.set_OSA_to_Searching_Contact_State()

            if self.is_seeking_contact:
                self.losing_contact()
            else:
                self.stages.shiftOnArbitrary(self.axis_to_get_contact,-self.seeking_step)



            ##  move sample along scanning axis
            if not self.is_running: # if we stop scanning
                if self.is_squeeze_span:   ##  set the span of OSA back to span of interest
                    self.set_OSA_to_Measuring_State()
                    self.OSA.acquire_spectrum()
                break

            self.stages.shiftOnArbitrary(self.axis_to_scan,self.scanning_step)
            self.current_file_index+=1

            print('\n Shifted along the scanning axis\n')

            print('Time elapsed for measuring at single point is ', time.time()-time0,'\n')

        # if scanning finishes because all points along scanning axis are measured
        if self.is_running and self.current_file_index>self.stop_file_index:
            self.is_running=False
            print('\nScanning finished\n')
        if self.is_squeeze_span:
            self.set_OSA_to_Measuring_State()
            self.OSA.acquire_spectrum()
        self.S_finished.emit()

    def __del__(self):
        print('Closing scanning object...')

if __name__ == "__main__":

       ScanningProcess=ScanningProcess(None,None)