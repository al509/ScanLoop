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
    DirName='SavedData'
    skip_Header=3
    LowFreqEdge=0.000 ##For FFT filter. Set <0 to avoid
    HighFreqEdge=30 ##For FFT filter. Set >1 to avoid
    StepSize=30*2.5 # um, Step in Z direction

    MinimumPeakDepth=2  ## For peak searching
    MinimumPeakDistance=500 ## For peak searching


    AccuracyOfWavelength=0.008 # in nm. Maximum expected shift to define the correlation window

    def KeyFunctionForSortingFileList(self,string):
        string=string.split('_');
        return float(string[2])



    def InterpolateInDesiredPoint(self, YArray,XOldArray,XNewarray):
        f=interpolate.interp1d(XOldArray,YArray,fill_value='extrapolate')
        Output=f(XNewarray)
        if np.isinf(Output[0]):
            Output[0]=np.mean(Output[1:-1])
        if np.isinf(Output[-1]):
            Output[-1]=np.mean(Output[1:-1])
        return Output



    def Create2DListOfFiles(self,FileList):  #Find all files which acqured at the same point
        NewFileList=[]
        while FileList:
            Name=FileList[0]
            s=Name[:Name.rfind('_')+1]
             #s=s[2] # take signature of the position,  etc
            Temp=[T for T in FileList if s in T]  # take all 'signature' + 'i' instances
            NewFileList.append(Temp)
            FileList=[T for T in FileList if not (T in Temp)]
        return NewFileList





    def run(self,StepSize,Averaging:bool):
        AccuracyOfWavelength=self.AccuracyOfWavelength
        time1=time.time()
        FileList=os.listdir(self.DirName)
        FileList=sorted(FileList,key=self.KeyFunctionForSortingFileList)
        StructuredFileList=self.Create2DListOfFiles(FileList)
        NumberOfPointsZ=len(StructuredFileList)
        #Data = np.loadtxt(DirName+ '\\Signal' + '\\' +FileList[0])
        print(self.DirName+ '\\' +FileList[0])
        Data = np.genfromtxt(self.DirName+ '\\' +FileList[0],skip_header=self.skip_Header)
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
                Data = np.genfromtxt(self.DirName+ '\\' +FileName,skip_header=self.skip_Header)
                SmallSignalArray[:,jj]=self.InterpolateInDesiredPoint(Data[:,1],Data[:,0],MainWavelengths)
            for jj, FileName in enumerate(FileNameListAtPoint):
                for kk, FileName in enumerate(FileNameListAtPoint):
                    if jj<kk:
                        Temp=np.correlate(SmallSignalArray[int(AccuracyOfWavelength/WavelengthStep):-int(AccuracyOfWavelength/WavelengthStep),kk],SmallSignalArray[:,jj], mode='valid')/np.sum(SmallSignalArray[int(AccuracyOfWavelength/WavelengthStep):-int(AccuracyOfWavelength/WavelengthStep),jj]**2)
                        ShiftIndexesMatrix[jj,kk]=np.argmax(Temp)-np.floor(AccuracyOfWavelength/WavelengthStep)
                        ShiftIndexesMatrix[kk,jj]=-ShiftIndexesMatrix[jj,kk]

            ShiftArray=(np.mean(ShiftIndexesMatrix,1))
            SignalLog=np.zeros(NumberOfWavelengthPoints)
            MeanLevel=np.mean(SmallSignalArray)
            if Averaging:
                for jj, FileName in enumerate(FileNameListAtPoint):
                    Temp=np.ones(NumberOfWavelengthPoints)*MeanLevel
                    Temp[int(AccuracyOfWavelength/WavelengthStep)+int(ShiftArray[jj]):-int(AccuracyOfWavelength/WavelengthStep)+int(ShiftArray[jj])]=SmallSignalArray[int(AccuracyOfWavelength/WavelengthStep):-int(AccuracyOfWavelength/WavelengthStep),jj]
                    SignalLog+=Temp
                SignalArray[:,ii]=SignalLog/NumberOfArraysToAverage#-np.nanmax(SignalLog)
            else:
                Temp=np.ones(NumberOfWavelengthPoints)*MeanLevel
                Temp[int(AccuracyOfWavelength/WavelengthStep)+int(ShiftArray[0]):-int(AccuracyOfWavelength/WavelengthStep)+int(ShiftArray[0])]=SmallSignalArray[int(AccuracyOfWavelength/WavelengthStep):-int(AccuracyOfWavelength/WavelengthStep),0]
                SignalArray[:,ii]=Temp


        np.savetxt('SignalArray.txt',SignalArray)
        np.savetxt('WavelengthArray.txt', MainWavelengths)

        #plt.ylim(1547.2,1547.5)
        plt.figure(4)
        plt.clf()
        ImGraph=plt.imshow(SignalArray, interpolation = 'bilinear',aspect='auto',cmap='RdBu_r',extent=[0,StepSize*NumberOfPointsZ,MainWavelengths[0],MainWavelengths[-1]],origin='lower')# vmax=0, vmin=-1)

        plt.show()
        plt.colorbar()
        plt.xlabel('Position, steps (2.5 um each)')
        plt.ylabel('Wavelength, nm')
        ax2=(plt.gca()).twiny()
        ax2.set_xlabel('Distance, um')
        ax2.set_xlim([0,StepSize*NumberOfPointsZ*2.5])
        plt.savefig('Scanned WGM spectra ')
        #plt.plot(TimeArray,CorrelationArray)
        #np.savetxt('Correlation'+DirName+'.txt',np.column_stack((TimeArray,CorrelationArray)))#np.hstack([X,CorrelationArray]))

        time2=time.time()
        print('Time used =', time2-time1 ,' s')

if __name__ == "__main__":
    ProcessSpectra=ProcessSpectra()
    ProcessSpectra.run(StepSize=20)