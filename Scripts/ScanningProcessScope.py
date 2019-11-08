# -*- coding: utf-8 -*-
"""
Created on Tue Nov 20 19:09:12 2018

Version Oct 18 2019
@author: Ilya
"""

from PyQt5.QtCore import pyqtSignal,  QObject
import numpy as np
import winsound
import time



class ScanningProcess(QObject):
    is_running=False  ## Variable is "True" during scanning process. Pushing on "scanning" button in main window sets is_running True and start scanning process.  
    ### Another pushing on "scanning" button during the scanning proccess set is_running to "False" and interrupt the scanning process
    
    AxisToScan='Z' # 'X',or 'Y', or 'Z'. Axis to scan along
    AxisToGetContact='X' # 'X',or 'Y', or 'Z'. The script will be searching for contactbetween the taper and the microresonator with moving along AxisToGetContact
    
    LevelToDistinctContact=0.004 # V, used to determine if there is contact between the taper and the sample. see function checkIfContact for details
     
    ScanStep=30 #in stage steps, Step to move stage "AxisToScan" 
    SeekContactStep=30 #in stage steps, Step to move stage AxisToGetContact to find the contact
    BackStep=50   #in stage steps, Step to move stage AxisToGetContact to loose the contact
    
    CurrentFileIndex=1 
    StopFileIndex=100
    
      
    IsInContact=False # True - when taper is in contact with the sample 
    
    NumberOfScans=1 # Number of spectra acquired at each point along the sample
    
    
    
    S_updateCurrentFileName=pyqtSignal(str) #signal to initiate update the index of the current file in lineEdit_CurrentFile of main window
    S_saveData=pyqtSignal(object,str) #signal to initiate saving measured spectrum to a file
    S_addPosition_and_FilePrefix=pyqtSignal(str) #signal to initiate saving current position of the stages and current file index to file "Positions.txt"
    S_finished=pyqtSignal()  # signal to finish
    

    def __init__(self,
                 Scope:QObject,
                 Stages:QObject,
                 scanstep:int,seekcontactstep:int,backstep:int,seekcontactvalue:float,ScanningType:int,
                 CurrentFileIndex:int,StopFileIndex:int,numberofscans:int,searchcontact:bool):
        super().__init__()
        self.scope=Scope # add scope
        self.SamplingRate=self.scope.get_sampling_rate()
        self.stages=Stages # add all three stages
        self.set_ScanningType(ScanningType) 
        self.ScanStep=scanstep
        self.SeekContactStep=seekcontactstep
        self.BackStep=-1*backstep
        self.LevelToDistinctContact=seekcontactvalue
        self.CurrentFileIndex=CurrentFileIndex
        self.StopFileIndex=StopFileIndex
        self.NumberOfScans=numberofscans
        

    def set_ScanningType(self,ScanningType:int): # set axis depending on choice in MainWindow
        if ScanningType==0:
            self.AxisToScan='Z'
            self.AxisToGetContact='X'
        elif ScanningType==1:
            self.AxisToScan='Y'
            self.AxisToGetContact='X'
        elif ScanningType==2:
            self.AxisToScan='Y'
            self.AxisToGetContact='Z'

        
    def search_contact(self): ## move taper towards sample until contact has been obtained
        Times,signals,channel_numbers=self.scope.acquire()
        time.sleep(0.05)
        self.IsInContact=self.checkIfContact(signals[0]) #check if there is contact already
        while not self.IsInContact:
            self.stages.shiftOnArbitrary(self.AxisToGetContact,self.SeekContactStep)
            print('Moved to Sample')
            Times,signals,channel_numbers=self.scope.acquire()
            time.sleep(0.05)
            self.IsInContact=self.checkIfContact(signals[0])
            if not self.is_running : ##if scanning process is interrupted,stop searching contact
                return 0
        print('\nContact found\n')
        winsound.Beep(1000, 500)
            
    def losing_contact(self): ##move taper away from sample until contact is lost
      while self.IsInContact:
            self.stages.shiftOnArbitrary(self.AxisToGetContact,self.BackStep)
            print('Moved Back from Sample')
            time.sleep(0.05)
            Times,signals,channel_numbers=self.scope.acquire()
            self.IsInContact=self.checkIfContact(signals[0])
            if not self.is_running : ##if scanning process is interrupted,stop searching contact
                return 0
            
 
    def checkIfContact(self, signal):  ## take measured spectrum and decide if there is contact between the taper and the sample
        Max=np.max(signal)
        if Max>self.LevelToDistinctContact:
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
        while self.is_running and self.CurrentFileIndex<self.StopFileIndex+1:
            time0=time.time()
            
            ## Getting in contact between the taper and the sample
            if self.searchcontact:
                self.search_contact() 
            else:
                self.stages.shiftOnArbitrary(self.AxisToGetContact,self.SeekContactStep)
            
            ## Acquring and saving data 
            for jj in range(0,self.NumberOfScans):
                print('saving sweep # ', jj+1)
                Times,signal,channel_number=self.scope.acquire() # signal consists of all active traces data
                time.sleep(0.05)
                self.S_saveData.emit(signal,'SR='+self.SamplingRate+'_p='+str(self.CurrentFileIndex)+'_j='+str(jj)) # save data to file
                if not self.is_running: break
            
            #update indexes in MainWindow and save positions into "Positions.txt"
            self.S_addPosition_and_FilePrefix.emit(str(self.CurrentFileIndex))

            
            ## Loosing contact between the taper and the sample
            if not self.is_running: break
            if self.searchcontact:    
                self.losing_contact()
            else:
                self.stages.shiftOnArbitrary(self.AxisToGetContact,-self.SeekContactStep)
            
            
            ##  move sample along scanning axis
            if not self.is_running: break
            self.stages.shiftOnArbitrary(self.AxisToScan,self.ScanStep)
            self.CurrentFileIndex+=1
            self.S_updateCurrentFileName.emit(str(self.CurrentFileIndex))
            print('\n Shifted along the scanning axis\n')

            print('Time elapsed is ', time.time()-time0,'\n')
            
        # if scanning finishes because all points along scanning axis are measured  
        if self.is_running and self.CurrentFileIndex>self.StopFileIndex:
            self.is_running=False
            print('\nScanning finished\n')
            self.S_finished.emit()



    def __del__(self):
        print('Closing scanning object...')

if __name__ == "__main__":

       ScanningProcess=ScanningProcess(None,None,1,1,1,1,1,1,1,1,1)