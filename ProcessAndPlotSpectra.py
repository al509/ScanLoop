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
    DirName='SavedSpectra'
    #DirName='After Annealing step=62'
    LowFreqEdge=0.000 ##For FFT filter. Set <0 to avoid 
    HighFreqEdge=30 ##For FFT filter. Set >1 to avoid 
    


    
    

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
    
    def FFT_filter(self,y_array,LowFreqEdge,HighFreqEdge):
        W=fftfreq(y_array.size)
        f_array = rfft(y_array)
        f_array[(abs(W)<LowFreqEdge)] = 0
        f_array[(abs(W)>HighFreqEdge)] = 0
        return irfft(f_array)
    
    def InterpolateInDesiredPoint(self,YArray,XOldArray,XNewarray):
        f=interpolate.interp1d(XOldArray,YArray,fill_value='extrapolate')
        return f(XNewarray)
    


    def run(self,StepSize,LowFreqEdge=None,HighFreqEdge=None):
        DirName=self.DirName
        time1=time.time()
        #for DirName in DirNameList:
        FileList=os.listdir(DirName)
        if len(FileList)>0:
            FileList=sorted(FileList,key=self.KeyFunctionForSortingFileList)
            NumberOfFiles=len(FileList)
            NumberOfPointsZ=np.arange(1,NumberOfFiles+1)*StepSize
            Data = np.loadtxt(DirName+'\\'+FileList[0])
            #PointsToCut=2  # Number of points in wavelength array to be avoided in all files to allow interpolation process 
            #MainWavelengths=Data[PointsToCut:len(Data[:,0])-PointsToCut,0]
            MainWavelengths=Data[:,0]
            NumberOfWavelengthPoints=len(MainWavelengths)
            SignalArray=np.zeros((NumberOfWavelengthPoints,NumberOfFiles))
            ii=0
            for FileName in FileList:
                print(DirName+'\\ '+FileName +' ' + str(FileList[NumberOfFiles-1]))
                SignalLog= np.loadtxt(DirName+'\\'+ FileName)[:,1]
            #    Signal=np.exp(SignalLog/10e4*np.log(10))
                if LowFreqEdge is not None:
                    SignalArray[:,ii]=self.FFT_filter(SignalLog,LowFreqEdge,HighFreqEdge)   # Uncomment this to use FFT filter
                SignalArray[:,ii]=SignalLog-np.mean(SignalLog)
            #    SignalArray[:,ii]=FFT_filter(SignalLog,LowFreqEdge,HighFreqEdge)   # Uncomment this to use FFT filter
                ii+=1
                
            
            np.savetxt('SignalArray.txt',SignalArray)
            np.savetxt('WavelengthArray.txt', MainWavelengths)
            
            #plt.ylim(1547.2,1547.5)
            plt.figure(3)
            plt.clf()
            ImGraph=plt.imshow(SignalArray, interpolation = 'bilinear',aspect='auto',cmap='RdBu_r',extent=[0,StepSize*NumberOfFiles,MainWavelengths[0],MainWavelengths[-1]],origin='lower')# vmax=0, vmin=-1)
            
            plt.show()
            plt.colorbar()  
            plt.xlabel('Position, steps (2.5 um each)')
            plt.ylabel('Wavelength, nm')
            plt.savefig('Scanned WGM spectra '+ DirName)
            #plt.plot(TimeArray,CorrelationArray)
            #np.savetxt('Correlation'+DirName+'.txt',np.column_stack((TimeArray,CorrelationArray)))#np.hstack([X,CorrelationArray]))
            
            time2=time.time()
            print('Time used =', time2-time1 ,' s')
        
if __name__ == "__main__":
    ProcessSpectra=ProcessSpectra()
    ProcessSpectra.run(StepSize=20,LowFreqEdge=4,HighFreqEdge=60)