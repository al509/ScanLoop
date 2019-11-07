import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import time
from scipy.fftpack import rfft, irfft, fftfreq
from scipy import interpolate
from scipy import signal
from PyQt5.QtCore import QObject, QThread, pyqtSignal

class ProcessSpectraWithAveraging(QObject):
    ProcessedDataFolder='ProcessedData\\'
    skip_Header=3
    LowFreqEdge=0.000 ##For FFT filter. Set <0 to avoid
    HighFreqEdge=30 ##For FFT filter. Set >1 to avoid
    StepSize=30*2.5 # um, Step in Z direction

    MinimumPeakDepth=2  ## For peak searching
    MinimumPeakDistance=500 ## For peak searching
    file_naming_style='new'
    axis_to_plot_along='X'

    AccuracyOfWavelength=0.008 # in nm. Maximum expected shift to define the correlation window
#    
    def define_file_naming_style(self,FileName):
        if FileName.find('X=')==-1:
            self.file_naming_style='old'
        else:
            self.file_naming_style='new'
        
    def find_between( s, first, last ): ## local function to find the substring between two given strings
        try:
            start = s.index( first ) + len( first )
            end = s.index( last, start )
            return s[start:end]
        except ValueError:
            return ""

    def KeyFunctionForSortingFileList(self,string,axis='X'):
        if self.file_naming_style=='old':
            string=string.split('_');
            return float(string[2])
        else:
            if axis=='X':
                return float(self.find_between(string,'X=','_'))
            if axis=='Y':
                return float(self.find_between(string,'Y=','_'))
            if axis=='Z':
                return float(self.find_between(string,'Z=','.txt'))


    def Create2DListOfFiles(self,FileList,axis='X'):  #Find all files which acqured at the same point
        NewFileList=[]
        ## if Files are named with X position then Using new 
        if self.file_naming_style=='old':
            while FileList:
                Name=FileList[0]
                s=Name[:Name.rfind('_')+1]
                 #s=s[2] # take signature of the position,  etc
                Temp=[T for T in FileList if s in T]  # take all 'signature' + 'i' instances
                NewFileList.append(Temp)
                FileList=[T for T in FileList if not (T in Temp)]
            return NewFileList
        else:
            Position=[]
            while FileList:
                Name=FileList[0]
                s=axis+'='+str(self.KeyFunctionForSortingFileList(Name,axis=axis))
                 #s=s[2] # take signature of the position,  etc
                Temp=[T for T in FileList if s in T]  # take all 'signature' + 'i' instances
                NewFileList.append(Temp)
                Positions.append([self.KeyFunctionForSortingFileList(Name,axis='X'),
                                  self.KeyFunctionForSortingFileList(Name,axis='Y'),
                                  self.KeyFunctionForSortingFileList(Name,axis='Z')])
                FileList=[T for T in FileList if not (T in Temp)]
            return NewFileList
            



    def InterpolateInDesiredPoint(self, YArray,XOldArray,XNewarray):
        f=interpolate.interp1d(XOldArray,YArray,fill_value='extrapolate')
        Output=f(XNewarray)
        if np.isinf(Output[0]):
            Output[0]=np.mean(Output[1:-1])
        if np.isinf(Output[-1]):
            Output[-1]=np.mean(Output[1:-1])
        return Output



    def run(self,StepSize,Averaging:bool,Shifting:bool,DirName):
        AccuracyOfWavelength=self.AccuracyOfWavelength
        time1=time.time()
        FileList=os.listdir(DirName)
        self.define_file_naming_style(FileList[0])
        FileList=sorted(FileList,key=self.KeyFunctionForSortingFileList)
        StructuredFileList=self.Create2DListOfFiles(FileList)
        NumberOfPointsZ=len(StructuredFileList)
        #Data = np.loadtxt(DirName+ '\\Signal' + '\\' +FileList[0])
        print(DirName+ '\\' +FileList[0])
        Data = np.genfromtxt(DirName+ '\\' +FileList[0],skip_header=self.skip_Header)
        MainWavelengths=np.arange(np.min(Data[:,0]),np.max(Data[:,0]),np.max(np.abs(np.diff(Data[:,0]))))
        NumberOfWavelengthPoints=len(MainWavelengths)
        SignalArray=np.zeros((NumberOfWavelengthPoints,NumberOfPointsZ))
        WavelengthStep=MainWavelengths[1]-MainWavelengths[0]
        for ii,FileNameListAtPoint in enumerate(StructuredFileList):
            NumberOfArraysToAverage=len(FileNameListAtPoint)
            SmallSignalArray=np.zeros((NumberOfWavelengthPoints,NumberOfArraysToAverage))
            ShiftIndexesMatrix=np.zeros((NumberOfArraysToAverage,NumberOfArraysToAverage))
            print(FileNameListAtPoint[0])
            for jj, FileName in enumerate(FileNameListAtPoint):
                Data = np.genfromtxt(DirName+ '\\' +FileName,skip_header=self.skip_Header)
                SmallSignalArray[:,jj]=self.InterpolateInDesiredPoint(Data[:,1],Data[:,0],MainWavelengths)
            SignalLog=np.zeros(NumberOfWavelengthPoints)
            MeanLevel=np.mean(SmallSignalArray)
            ShiftArray=np.zeros(NumberOfArraysToAverage)
            if Averaging or Shifting:
                if Shifting:    
                    for jj, FileName in enumerate(FileNameListAtPoint):
                        for kk, FileName in enumerate(FileNameListAtPoint):
                            if jj<kk:
                                Temp=np.correlate(SmallSignalArray[int(AccuracyOfWavelength/WavelengthStep):-int(AccuracyOfWavelength/WavelengthStep),kk],SmallSignalArray[:,jj], mode='valid')/np.sum(SmallSignalArray[int(AccuracyOfWavelength/WavelengthStep):-int(AccuracyOfWavelength/WavelengthStep),jj]**2)
                                ShiftIndexesMatrix[jj,kk]=np.argmax(Temp)-np.floor(AccuracyOfWavelength/WavelengthStep)
                                ShiftIndexesMatrix[kk,jj]=-ShiftIndexesMatrix[jj,kk]
                    ShiftArray=(np.mean(ShiftIndexesMatrix,1))
                if Averaging:
                    for jj, FileName in enumerate(FileNameListAtPoint):
                        Temp=np.ones(NumberOfWavelengthPoints)*MeanLevel
                        Temp[int(AccuracyOfWavelength/WavelengthStep)+int(ShiftArray[jj]):-int(AccuracyOfWavelength/WavelengthStep)+int(ShiftArray[jj])]=SmallSignalArray[int(AccuracyOfWavelength/WavelengthStep):-int(AccuracyOfWavelength/WavelengthStep),jj]
                        SignalLog+=Temp
                    SignalArray[:,ii]=SignalLog/NumberOfArraysToAverage#-np.nanmax(SignalLog)
                elif Shifting:
                    Temp=np.ones(NumberOfWavelengthPoints)*MeanLevel
                    Temp[int(AccuracyOfWavelength/WavelengthStep)+int(ShiftArray[0]):-int(AccuracyOfWavelength/WavelengthStep)+int(ShiftArray[0])]=SmallSignalArray[int(AccuracyOfWavelength/WavelengthStep):-int(AccuracyOfWavelength/WavelengthStep),0]
                    SignalArray[:,ii]=Temp    
            else:
                SignalArray[:,ii]=SmallSignalArray[:,0]


        np.savetxt(self.ProcessedDataFolder+'SignalArray.txt',SignalArray)
        np.savetxt(self.ProcessedDataFolder+'WavelengthArray.txt', MainWavelengths)

        #plt.ylim(1547.2,1547.5)
        plt.figure()
        plt.clf()
        ImGraph=plt.imshow(SignalArray, interpolation = 'bilinear',aspect='auto',cmap='RdBu_r',extent=[0,StepSize*NumberOfPointsZ,MainWavelengths[0],MainWavelengths[-1]],origin='lower')# vmax=0, vmin=-1)

        plt.show()
        plt.colorbar()
        plt.xlabel('Position, steps (2.5 um each)')
        plt.ylabel('Wavelength, nm')
        ax2=(plt.gca()).twiny()
        ax2.set_xlabel('Distance, um')
        ax2.set_xlim([0,StepSize*NumberOfPointsZ*2.5])
        plt.savefig(self.ProcessedDataFolder+'Scanned WGM spectra')
        #plt.plot(TimeArray,CorrelationArray)
        #np.savetxt('Correlation'+DirName+'.txt',np.column_stack((TimeArray,CorrelationArray)))#np.hstack([X,CorrelationArray]))

        time2=time.time()
        print('Time used =', time2-time1 ,' s')

if __name__ == "__main__":
    ProcessSpectra=ProcessSpectraWithAveraging()
    ProcessSpectra.run(StepSize=20,Shifting=False, Averaging=False)