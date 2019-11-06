# -*- coding: utf-8 -*-
"""
Created on Tue Nov 20 19:09:12 2018

Version Oct 18 2019
@author: Ilya
"""

from PyQt5.QtCore import pyqtSignal, QThread, QState, QStateMachine, QObject
import numpy as np
import winsound
import time
from abc import ABC, abstractmethod

class ScanGeometry(ABC):
                                   

    @abstractmethod
    def searchContact(self):
        pass
    
    @abstractmethod
    def loseContact(self):
        pass
    
    @abstractmethod
    def doStep(self, scanstep):
        pass

class AxisScan(ScanGeometry):

    AxisToScan=''          # 'X',or 'Y', or 'Z'. Axis to scan along
    
    AxisToGetContact=''    # 'X',or 'Y', or 'Z'. The script will be searching 
                            ## for contactbetween the taper and the 
                            ##microresonator with moving along AxisToGetContact
                    
    
    def searchContact(self):
        pass
    
    def loseContact(self):
        pass
    
    def doStep(self, scanstep):
        pass

class LoopScan(ScanGeometry):
    
    def searchContact(self):
        pass
    
    def loseContact(self):
        pass
    
    def doStep(self, scanstep):
        pass

    

class ScanningProcess(QObject):

    ##Defining inner variables (which are parameters when fuction calls) 
    
    ScanStep=0                      # in stage steps, Step to move stage
    
    BackStep=0                      # in stage steps, Step to move stage 
                                    ## AxisToGetContact to loose the contact
    
    SeekContactStep=0               # in stage steps, Step to move stage
                                    ##  to find the contact
    
    LevelToDistinctContact=0        # dBm, used to determine if there is 
                                    ## contact between the taper and the sample
                                    ## See function checkIfContact for details
    
    
    CurrentFileIndex=0 
    StopFileIndex=0
    
    SqueezeSpanWhileSearchingContact=False  # if true, span is set to small 
                                            ## value of "SpanForScanning" each 
                                            ##time when contact is being sought
                                            
    SpanForScanning=0    # nm, Value of span in searching_contact function. 
                            ## Used if SqueezeSpanWhileSearchingContact==True
    
      
    NumberOfScans=0 # Number of spectra acquired at each point along the sample
    
    IsHighRes=False # if true and high resolution of OSA is used, spectra have
                    ## to be saved on OSA hardDrive
                    
    IsInContact=False               # True - when taper is in contact with
                                    ## the sample 
                                    
    is_running=False                # Variable is "True" during scanning proces
    
    
    S_updateCurrentFileName=pyqtSignal(str) #signal to initiate update the 
                                            ## index of the current file in
                                            ## lineEdit_CurrentFile of
                                            ## main window
                                                
    S_saveSpectrum=pyqtSignal(object,str)   # signal to initiate saving 
                                            ## measured spectrum to a file
                                            
    S_saveSpectrumToOSA=pyqtSignal(str)     # signal used if high resolution 
                                            ## needed. Initiate saving spectral 
                                            ## data to inner hard drive of OSA
                                            
    S_addPosition_and_FilePrefix=pyqtSignal(str)    #signal to initiate saving 
                                                    ## current position of the 
                                                    ## stages and current file 
                                                    ## index to file
                                                    ## "Positions.txt"
    
    S_finished=pyqtSignal()                         # signal to finish
    

    def __init__(self,
                 OSA:QObject,
                 Stages:QObject,
                 scanstep:int,seekcontactstep:int,backstep:int,
                 seekcontactvalue:float,ScanningType:int,
                 SqueezeSpanWhileSearchingContact:bool,
                 CurrentFileIndex:int,StopFileIndex:int,numberofscans:int):
        super().__init__()
        self.OSA=OSA        # add Optical Spectral Analyzer
        self.FullSpan=self.OSA._Span

        self.stages=Stages  # add all three stages
        self.set_ScanningType(ScanningType) 

        self.ScanStep=scanstep
        self.SeekContactStep=seekcontactstep
        self.BackStep=-1*backstep
        self.LevelToDistinctContact=seekcontactvalue
        self.CurrentFileIndex=CurrentFileIndex
        self.StopFileIndex=StopFileIndex
        self.SqueezeSpanWhileSearchingContact=SqueezeSpanWhileSearchingContact
        self.NumberOfScans=numberofscans



    def set_ScanningType(self,ScanningType:int):    # set axis depending on  
                                                    ## choice in MainWindow
        if ScanningType==0:
            self.AxisToScan='Z'
            self.AxisToGetContact='X'
        elif ScanningType==1:
            self.AxisToScan='Y'
            self.AxisToGetContact='X'
        elif ScanningType==2:
            self.AxisToScan='Y'
            self.AxisToGetContact='Z'
    
    
    
    def set_OSA_to_Searching_Contact_State(self):   #set rough resolution and 
                                                    ## narrowband span 
        print(self.OSA._Span)
        self._FullSpan=self.OSA._Span
        self.IsHighRes=self.OSA.IsHighRes   

        self.OSA.SetMode(3)     # set APEX OSA to O.S.A. mode - it works faster   
        self.OSA.SetSpan(self.SpanForScanning)

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

    def search_contact(self):   # move taper towards sample until contact 
                                ## has been obtained
        wavelengthdata, spectrum=self.OSA.acquire_spectrum()
        time.sleep(0.05)
        self.IsInContact=self.checkIfContact(spectrum)  #check if there is 
                                                        #contact already
        while not self.IsInContact:
            self.stages.shiftOnArbitrary(self.AxisToGetContact,
                                         self.SeekContactStep)
            print('Moved to Sample')
            wavelengthdata, spectrum=self.OSA.acquire_spectrum()
            time.sleep(0.05)
            self.IsInContact=self.checkIfContact(spectrum)
            if not self.is_running :    # if scanning process is interrupted,
                                        ## stop searching contact
                if self.SqueezeSpanWhileSearchingContact:
                    self.set_OSA_to_Measuring_State()
                    self.OSA.acquire_spectrum()
                return 0
        print('\nContact found\n')
        winsound.Beep(1000, 500)
            
    def losing_contact(self): # move taper away from sample until contact lost
        while self.IsInContact:
            self.stages.shiftOnArbitrary(self.AxisToGetContact,self.BackStep)
            print('Moved Back from Sample')
            wavelengthdata,spectrum=self.OSA.acquire_spectrum()
            time.sleep(0.05)
            self.IsInContact=self.checkIfContact(spectrum)
            if not self.is_running :    # if scanning process is interrupted,
                                        # stop searching contact
                if self.SqueezeSpanWhileSearchingContact:
                    self.set_OSA_to_Measuring_State()
                    self.OSA.acquire_spectrum()
                return 0
        print('\nContact lost\n')
 
    def checkIfContact(self, spectrum): # take measured spectrum and decide 
                                        # if there is contact between the taper 
                                        # and the sample
        Min=np.min(spectrum)
        if Min<self.LevelToDistinctContact:
            return True
        else:
            return False   
  
    
    """
    Main function
    """
    def run(self):
        time.sleep(0.05)
        self.is_running=True 
       
        ### main loop
        if self.SqueezeSpanWhileSearchingContact:   # to speed up the process 
                                                    ## of the getting contact, 
                                                    ## the very narrow span of
                                                    ## OSA can be set 
            self.set_OSA_to_Searching_Contact_State()  
        while self.is_running and self.CurrentFileIndex<self.StopFileIndex+1:
            time0=time.time()
            ## Getting in contact between the taper and the sample
            # 1:
            self.search_contact() 
            
            if self.SqueezeSpanWhileSearchingContact:   # after contact is 
                                                        ## found, set the span 
                                                        ## of OSA back to span 
                                                        ## of interest
                self.set_OSA_to_Measuring_State()
                
            ## Acquring and saving data 
            for jj in range(0,self.NumberOfScans):
                print('saving sweep # ', jj+1)
                wavelengthdata, spectrum=self.OSA.acquire_spectrum()
                time.sleep(0.05)
                Data=np.stack((wavelengthdata, spectrum),axis=1)
                self.S_saveSpectrum.emit(Data,str(self.CurrentFileIndex)+
                                         '_'+str(jj))   # save spectrum to file
                if self.IsHighRes:  # if true and high resolution of OSA is  
                                    ## used, spectra have to be saved on OSA 
                                    ## hardDrive to preserve full resolution
                    self.S_saveSpectrumToOSA.emit(str(self.CurrentFileIndex)+
                                                  '_'+str(jj))
                if not self.is_running: break
            
            #update indeces in MainWindow and save positions into
            ## "Positions.txt"
            self.S_addPosition_and_FilePrefix.emit(str(self.CurrentFileIndex))


            
            ## Loosing contact between the taper and the sample
            if not self.is_running: 
                break
        
            if self.SqueezeSpanWhileSearchingContact:   # to speed up the 
                                                        ## process of losing 
                                                        ## contact, the very 
                                                        ## narrow span of OSA 
                                                        ## can be set  
                self.set_OSA_to_Searching_Contact_State()
       
            # 2:
            self.losing_contact()
                

            ##  move sample along scanning axis
            if not self.is_running: 
                if self.SqueezeSpanWhileSearchingContact:   ##  set the span of 
                                                            ## OSA back to span
                                                            ## of interest
                    self.set_OSA_to_Measuring_State()
                break
            
            # 3:
            self.stages.shiftOnArbitrary(self.AxisToScan,self.ScanStep)
            
            self.CurrentFileIndex+=1
            self.S_updateCurrentFileName.emit(str(self.CurrentFileIndex))
            print('\n Shifted along the scanning axis\n')

            print('Time elapsed for measuring at single point is ', time.time()
            -time0,'\n')
            
    # if scanning finishes because all points along scanning axis are measured  
        if self.is_running and self.CurrentFileIndex>self.StopFileIndex:
            self.is_running=False
            if self.SqueezeSpanWhileSearchingContact:
                self.set_OSA_to_Measuring_State()
            print('\nScanning finished\n')
            self.S_finished.emit()



    def __del__(self):
        print('Closing scanning object...')

if __name__ == "__main__":

       ScanningProcess=ScanningProcess(None,None,1,1,1,1,1,1,1,1,1)