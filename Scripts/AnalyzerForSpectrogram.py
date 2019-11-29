# -*- coding: utf-8 -*-
"""
Created on Thu Nov 28 17:01:51 2019

@author: Ilya
This script is used to find peaks in processed 2D spectrograms and extract ERV shape and linewidth
"""

import os
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.colors as colors
from mpl_toolkits.axes_grid1.parasite_axes import SubplotHost
import matplotlib.transforms as mtransforms
import time
import math
from PyQt5.QtCore import QObject
from Scripts.detect_peaks import detect_peaks

class AnalyzerForSpectrogram(QObject):
    ProcessedDataFolder='ProcessedData\\'
    MinimumPeakDistance=20  ## For peak searching 
    IndexOfPeakOfInterest=0 ## Zero is for deepest peak within the range, one is for next after deepest etc
    AreaToSearch=200 # This is to calculate peak linewidth
    SignalFileName=ProcessedDataFolder+'SpectraArray.txt'
    WavelengthFileName=ProcessedDataFolder+'WavelengthArray.txt'
    PositionsFileName=ProcessedDataFolder+'Sp_Positions.txt'
    number_of_axis={'X':0,'Y':1,'Z':2}
    
    def CalculateLinewidth(self,Xarray,Yarray,IndexOfMinimum,AreaToSearch):
        Ymin=Yarray[IndexOfMinimum]
        NewYarray=Yarray[IndexOfMinimum-AreaToSearch:IndexOfMinimum+AreaToSearch]
        Edges=np.argsort(abs(NewYarray-(Ymin+3)))
        LineWidths=np.diff(Xarray[Edges[0:5]])
        return np.max(LineWidths)
    
    def plotSlice(self,position, MinimumPeakDepth,axis_to_process='Z'):
        Data=np.loadtxt(self.SignalFileName)
        WavelengthArray=np.loadtxt(self.WavelengthFileName)
        Positions=np.loadtxt(self.PositionsFileName)
        Positions=Positions[:,self.number_of_axis[axis_to_process]]
        i=np.argmin(abs(Positions-position))
        SignalData=Data[:,i]
        Fig=plt.figure(10)
        plt.clf()
        plt.plot(WavelengthArray,SignalData)
        plt.title('Position=' + str(Positions[i])+ ' steps along axis '+axis_to_process) 
        peakind2=detect_peaks(SignalData, MinimumPeakDepth, self.MinimumPeakDistance, valley=True, show=False)
        plt.plot(WavelengthArray[peakind2], SignalData[peakind2], '.')
        
    def extractERV(self,MinimumPeakDepth,MinWavelength,MaxWavelength,axis_to_process='Z'):
        time1=time.time()
        Data=np.loadtxt(self.SignalFileName)
        WavelengthArray=np.loadtxt(self.WavelengthFileName)
        Positions=np.loadtxt(self.PositionsFileName)
        Positions=Positions[:,self.number_of_axis[axis_to_process]]
        
        NumberOfWavelength,Number_of_positions = Data.shape
        LineWidthArray=np.zeros(Number_of_positions)
        PeakWavelengthArray=np.zeros(Number_of_positions)
#        PeakWavelengthMatrix=np.zeros(np.shape(Data))
#        PeakWavelengthMatrix[:]=np.nan
    
        
        
        for Zind, Z in enumerate(range(0,Number_of_positions)):
            print(Z,Zind)
            peakind=detect_peaks(Data[:,Zind],MinimumPeakDepth , self.MinimumPeakDistance, valley=True, show=False)
            NewPeakind=np.extract((WavelengthArray[peakind]>MinWavelength) & (WavelengthArray[peakind]<MaxWavelength),peakind)
            NewPeakind=NewPeakind[np.argsort(Data[NewPeakind,Zind])]
        #    peakind2=np.argsort(-Data[peakind1,Zind])
            if len(NewPeakind)>self.IndexOfPeakOfInterest:
                LineWidthArray[Zind]=self.CalculateLinewidth(WavelengthArray,Data[:,Zind],NewPeakind[self.IndexOfPeakOfInterest],self.AreaToSearch)
                PeakWavelengthArray[Zind]=WavelengthArray[NewPeakind[self.IndexOfPeakOfInterest]]
#                PeakWavelengthMatrix[NewPeakind[self.IndexOfPeakOfInterest],Zind]=-Data[NewPeakind[self.IndexOfPeakOfInterest],Zind]
            else:
                PeakWavelengthArray[Zind]=np.nan
                LineWidthArray[Zind]=np.nan
        
        
        np.savetxt(self.ProcessedDataFolder+'PeakWavelengths.txt',np.transpose(np.stack((Positions,PeakWavelengthArray,LineWidthArray))))
        
        time2=time.time()
        print('Time used =', time2-time1 ,' s')
        Fig=plt.figure(2)
        plt.clf()
        plt.plot(Positions,LineWidthArray)
        plt.xlabel('Step Number')
        plt.ylabel('Linewidth, nm')
        Fig2=plt.figure(3)
        plt.clf()
        plt.plot(Positions,PeakWavelengthArray,'.')
        plt.xlabel('Step Number')
        plt.ylabel('Wavelength, nm')
#        Fig3=plt.figure(3)
#        plt.clf()
#        Data=Data[IndexMaxWavelength:IndexMinWavelength,0:Number_of_positions]
#        ImGraph=plt.imshow(Data,  interpolation = 'bilinear',aspect='auto',cmap='jet',extent=[0,Number_of_positions,WavelengthArray[IndexMinWavelength],WavelengthArray[IndexMaxWavelength]])#, vmin=-1, vmax=0)
#        plt.pcolormesh(np.arange(0,Number_of_positions),WavelengthArray[IndexMaxWavelength:IndexMinWavelength],PeakWavelengthMatrix[IndexMaxWavelength:IndexMinWavelength,:])
        
if __name__ == "__main__":
    os.chdir('..')
    AnalyzerForSpectrogram=AnalyzerForSpectrogram()

#    AnalyzerForSpectrogram.plotSlice(100)
    AnalyzerForSpectrogram.plotSlice(100,20)
    AnalyzerForSpectrogram.extractERV(15,1549.6,1549.7)
    
