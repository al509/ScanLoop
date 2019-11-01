from PyQt5.QtCore import QObject, QThread, pyqtSignal
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import time
from scipy.fftpack import rfft, irfft, fftfreq
from scipy import interpolate
import os
#To process files from Astro, saved in two columns format
#Signal files are taken from 'Signal' subfolder of DirName,
#Noise files- from 'Noise' subfolder
#Interoplation used to plot all signals for the same wavelength array
#FFT filter can be applied to Signal
class ProcessSpectra(QObject):
    #DirNameList=['first try']#,'200 mA 2T']
    DirName='SavedData'
    #DirName='After Annealing step=62'
    HighFreqEdge=1 ##For FFT filter. Set 0 to avoid
    Colormap='jet'
    
    def KeyFunctionForSortingFileList(self,string):
        S=(string.split('.txt'))[0]
        string=S.split('_')
        return int(string[2])

    def CheckIfWavelengthsInside(self,FileName):
        data = np.loadtxt(FileName)
        Size=np.shape(data)
        if Size[1]==4:
            return True
        else:
            return False

    def FFT_filter(self,y_array,HighFreqEdge):
        W=fftfreq(y_array.size)
        f_array = rfft(y_array)
        f_array[(abs(W)<HighFreqEdge)] = 0
        return irfft(f_array)

    def InterpolateInDesiredPoint(self,YArray,XOldArray,XNewarray):
        f=interpolate.interp1d(XOldArray,YArray,bounds_error=False,fill_value=np.nan)
        return f(XNewarray)

    def AverageAndShrinkDataArray(self,Xarr,Yarr):
        Signal=[]
        MainWavelengths=[]
        Diff=np.diff(Xarr)
        NonZeroDiff=[ind for ind in range(0,len(Xarr)-1) if Diff[ind]!=0]
        for ind in range(0,len(NonZeroDiff)):
            if ind==0:
                Mean=np.mean(Yarr[0:NonZeroDiff[0]])
            else:
                Mean=np.mean(Yarr[NonZeroDiff[ind-1]:NonZeroDiff[ind]])
            Signal.append(Mean)
            MainWavelengths.append(Xarr[NonZeroDiff[ind]-1])
        return np.array(MainWavelengths), np.array(Signal)

    def run(self,StepSize,HighFreqEdge=None,IsHighRes=False, DoesSpanVary=False,
            IsHighResolution=False):
        DirName=self.DirName
        time1=time.time()
        #for DirName in DirNameList:
        FileList=os.listdir(DirName)
        if len(FileList)==0:
            print('There is no saved data')
            exit()
        
        FileList=sorted(FileList,key=self.KeyFunctionForSortingFileList)
        NumberOfFiles=len(FileList)
        NumberOfPointsZ=np.arange(1,NumberOfFiles+1)*StepSize

        if DoesSpanVary:
            if IsHighRes:
                Resolution=4e-5
            else:
                Resolution=1.12e-3
            WavelengthList=[]
            SignalList=[]
            for FileName in FileList:
                Data = np.loadtxt(DirName+'\\'+FileName)
                Wavelengths, Signal=self.AverageAndShrinkDataArray(Data[:,0], Data[:,1])
                WavelengthList.append(Wavelengths)
                SignalList.append(Signal)
            WavelengthStep=Resolution/2
            MinWavelength=np.min(WavelengthList[0])
            MaxWavelength=np.max(WavelengthList[0])
            fmin=lambda x,y: x if x<y else y
            fmax=lambda x,y: x if x>y else y
            for x in WavelengthList:
                MinWavelength=fmin(MinWavelength,np.min(x))
                MaxWavelength=fmax(MaxWavelength,np.max(x))
            MainWavelengths=np.linspace(MinWavelength, MaxWavelength,int((MaxWavelength-MinWavelength)/WavelengthStep))
            NumberOfWavelengthPoints=len(MainWavelengths)
            SignalArray=np.zeros((NumberOfWavelengthPoints,NumberOfFiles))
            for ind, Signal in enumerate(SignalList):
                print(ind)
                SignalArray[:,ind]=self.InterpolateInDesiredPoint(Signal,WavelengthList[ind],MainWavelengths)
        else:
            Data = np.loadtxt(DirName+'\\'+FileList[0])
        #PointsToCut=2  # Number of points in wavelength array to be avoided in all files to allow interpolation process
        #MainWavelengths=Data[PointsToCut:len(Data[:,0])-PointsToCut,0]
            MainWavelengths=Data[:,0]
            NumberOfWavelengthPoints=len(MainWavelengths)
            SignalArray=np.zeros((NumberOfWavelengthPoints,NumberOfFiles))
            ii=0
        
            for FileName in FileList:
                print(DirName+'\\ '+FileName +' ' + str(FileList[NumberOfFiles-1]))
                Temp=np.loadtxt(DirName+'\\'+ FileName)
                if IsHighRes:
                    CurrentWavelengths,RawSignalLog=self.AverageAndShrinkDataArray(Temp[:,0],Temp[:,1])
                    SignalLog=self.InterpolateInDesiredPoint(RawSignalLog,CurrentWavelengths,MainWavelengths)
                else:
                    CurrentWavelengths=Temp[:,0]
                    RawSignalLog=Temp[:,1]
                    SignalLog=self.InterpolateInDesiredPoint(RawSignalLog,CurrentWavelengths,MainWavelengths)
            #                SignalArray[:,ii]=self.FFT_filter(SignalLog,HighFreqEdge)   # Uncomment this to use FFT filter
                SignalArray[:,ii]=SignalLog-np.nanmean(SignalLog)
            #    SignalArray[:,ii]=FFT_filter(SignalLog,LowFreqEdge,HighFreqEdge)   # Uncomment this to use FFT filter
                ii+=1


        np.savetxt('SignalArray.txt',SignalArray)
        np.savetxt('WavelengthArray.txt', MainWavelengths)

        #plt.ylim(1547.2,1547.5)
        plt.figure(2)
        plt.clf()
        ImGraph=plt.imshow(SignalArray, interpolation = 'bilinear',aspect='auto',cmap=self.Colormap,extent=[0,StepSize*NumberOfFiles,MainWavelengths[0],MainWavelengths[-1]],origin='lower')# vmax=0, vmin=-1)
        plt.xlabel('Position, steps (2.5 um each)')
        plt.ylabel('Wavelength, nm')
        ax2=(plt.gca()).twiny()
        ax2.set_xlabel('Distance, um')
        ax2.set_xlim([0,StepSize*NumberOfFiles*2.5])
        plt.show()
#        plt.colorbar(ImGraph)

        plt.savefig('Scanned WGM spectra ')
        #plt.plot(TimeArray,CorrelationArray)
        #np.savetxt('Correlation'+DirName+'.txt',np.column_stack((TimeArray,CorrelationArray)))#np.hstack([X,CorrelationArray]))

        time2=time.time()
        print('Time elapsed to process and plot data =', time2-time1 ,' s')

if __name__ == "__main__":
    ProcessSpectra=ProcessSpectra()
    ProcessSpectra.run(StepSize=60,HighFreqEdge=60,DoesSpanVary=True)