# -*- coding: utf-8 -*-
"""
Created on Thu Nov 28 17:01:51 2019

@author: Ilya
This script is used to find peaks in processed 2D spectrograms and extract ERV shape and linewidth
"""

import os
import numpy as np
import matplotlib.pyplot as plt
import time
from PyQt5.QtCore import QObject
from Scripts.detect_peaks import detect_peaks

class AnalyzerForSpectrogram(QObject):
    ProcessedDataFolder='ProcessedData\\'
    MinimumPeakDistance=10  ## For peak searching 
    IndexOfPeakOfInterest=0 ## Zero is for deepest peak within the range, one is for next after deepest etc
    AreaToSearch=200 # This is to calculate peak linewidth
    SignalFileName=ProcessedDataFolder+'SpectraArray.txt'
    WavelengthFileName=ProcessedDataFolder+'WavelengthArray.txt'
    PositionsFileName=ProcessedDataFolder+'Sp_Positions.txt'
    number_of_axis={'X':0,'Y':1,'Z':2}
    Cmap='jet'
    
    def CalculateLinewidth(self,Xarray,Yarray,IndexOfMinimum,AreaToSearch):
        Ymin=Yarray[IndexOfMinimum]
        NewYarray=Yarray[IndexOfMinimum-AreaToSearch:IndexOfMinimum+AreaToSearch]
        Edges=np.argsort(abs(NewYarray-(Ymin+3)))
        if len(Edges)>0:
            LineWidths=np.diff(Xarray[Edges[0:5]])
            return np.max(LineWidths)
        else:
            return 0
        
    def plot_sample_shape(self):
        from mpl_toolkits.mplot3d import Axes3D
        Positions=np.loadtxt(self.PositionsFileName)
        plt.figure()
        ax = plt.axes(projection='3d')
        ax.plot(Positions[:,2],Positions[:,0],Positions[:,1])
        ax.set_xlabel('Z,steps')
        ax.set_ylabel('X,steps')
        ax.set_zlabel('Y,steps')
        plt.gca().invert_zaxis()
        plt.gca().invert_xaxis()
    
    def plot2D(self,axis_to_process='Z'):
        Data=np.loadtxt(self.SignalFileName)
        WavelengthArray=np.loadtxt(self.WavelengthFileName)
        Positions=np.loadtxt(self.PositionsFileName)
        index=self.number_of_axis[axis_to_process]
        Positions=Positions[:,index]
        plt.figure()
        plt.contourf(Positions,WavelengthArray,Data,200,cmap=self.Cmap)
        plt.xlabel('Position, steps (2.5 um each)')
        plt.ylabel('Wavelength, nm')
        ax2=(plt.gca()).twiny()
        ax2.set_xlabel('Distance, um')
        ax2.set_xlim([0,(np.max(Positions)-np.min(Positions))*2.5])
        plt.tight_layout()
    
    def plotSlice(self,position, MinimumPeakDepth,axis_to_process='Z'):
        Data=np.loadtxt(self.SignalFileName)
        WavelengthArray=np.loadtxt(self.WavelengthFileName)
        Positions=np.loadtxt(self.PositionsFileName)
        Positions=Positions[:,self.number_of_axis[axis_to_process]]
        i=np.argmin(abs(Positions-position))
        SignalData=Data[:,i]
        plt.figure()
        plt.clf()
        plt.plot(WavelengthArray,SignalData)
        plt.title('Position=' + str(Positions[i])+ ' steps along axis '+axis_to_process) 
        peakind2=detect_peaks(SignalData, MinimumPeakDepth, self.MinimumPeakDistance, valley=True, show=False)
        plt.plot(WavelengthArray[peakind2], SignalData[peakind2], '.')
        plt.tight_layout()
        
    def extractERV(self,MinimumPeakDepth,MinWavelength,MaxWavelength,axis_to_process='Z'):
        time1=time.time()
        Data=np.loadtxt(self.SignalFileName)
        WavelengthArray=np.loadtxt(self.WavelengthFileName)
        Positions=np.loadtxt(self.PositionsFileName)
        Positions=Positions[:,self.number_of_axis[axis_to_process]]
        
        NumberOfWavelength,Number_of_positions = Data.shape
        LineWidthArray=np.zeros(Number_of_positions)
        PeakWavelengthArray=np.zeros(Number_of_positions)
        PeakWavelengthMatrix=np.zeros(np.shape(Data))
        PeakWavelengthMatrix[:]=np.nan
    
        
        
        for Zind, Z in enumerate(range(0,Number_of_positions)):
            print(Z,Zind)
            peakind=detect_peaks(Data[:,Zind],MinimumPeakDepth , self.MinimumPeakDistance, valley=True, show=False)
            NewPeakind=np.extract((WavelengthArray[peakind]>MinWavelength) & (WavelengthArray[peakind]<MaxWavelength),peakind)
            NewPeakind=NewPeakind[np.argsort(-WavelengthArray[NewPeakind])] ##sort in wavelength decreasing
        #    peakind2=np.argsort(-Data[peakind1,Zind])
            if len(NewPeakind)>self.IndexOfPeakOfInterest:
                LineWidthArray[Zind]=self.CalculateLinewidth(WavelengthArray,Data[:,Zind],NewPeakind[self.IndexOfPeakOfInterest],self.AreaToSearch)
                PeakWavelengthArray[Zind]=WavelengthArray[NewPeakind[self.IndexOfPeakOfInterest]]
                PeakWavelengthMatrix[NewPeakind[self.IndexOfPeakOfInterest],Zind]=-Data[NewPeakind[self.IndexOfPeakOfInterest],Zind]
            else:
                PeakWavelengthArray[Zind]=np.nan
                LineWidthArray[Zind]=np.nan
        
        DirName=os.path.basename(self.ProcessedDataFolder)
        np.savetxt(self.ProcessedDataFolder+'\\ERVs_'+DirName+'.txt',np.transpose(np.stack((Positions,PeakWavelengthArray,LineWidthArray))))
        
        time2=time.time()
        print('Time used =', time2-time1 ,' s')
        plt.figure()
        plt.clf()
        plt.plot(Positions,LineWidthArray)
        plt.xlabel('Step Number')
        plt.ylabel('Linewidth, nm')
        plt.figure()
        plt.clf()
        plt.plot(Positions,PeakWavelengthArray,'.')
        plt.xlabel('Step Number')
        plt.ylabel('Wavelength, nm')
        plt.figure()
        plt.clf()
        plt.contourf(Positions,WavelengthArray,Data,200,cmap='jet')
        plt.pcolormesh(Positions,WavelengthArray,PeakWavelengthMatrix)
        plt.tight_layout()
        
if __name__ == "__main__":
    os.chdir('..')
    AnalyzerForSpectrogram=AnalyzerForSpectrogram()

#    AnalyzerForSpectrogram.plotSlice(100)
    AnalyzerForSpectrogram.plot2D()
#    AnalyzerForSpectrogram.extractERV(20,1552,1553)
    
