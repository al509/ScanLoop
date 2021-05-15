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
import pickle
from scipy.signal import find_peaks

class AnalyzerForSpectrogram(QObject):
    
    refractive_index=1.45
    
    def __init__(self, path:str):
        super().__init__(None)
        self.single_spectrum_path=None
        self.FilePath=path
        self.MinimumPeakDistance=10  ## For peak searching 
        self.IndexOfPeakOfInterest=0 ## Zero is for deepest peak within the range, one is for next after deepest etc
        self.AreaToSearch=200 # This is to calculate peak linewidth
        self.number_of_axis={'X':0,'Y':1,'Z':2,'W':3,'p':4}
        self.Cmap='jet'
    
        self.Radius=62.5e3
        self.lambda_0=1530.5
        
        self.axis=None
        self.Positions=None
        self.WavelengthArray=None
        self.Data=None
    
    def load_data(self):
        file_name=self.FilePath
        print('loading data for analyzer from ',file_name)
        f=open(file_name,'rb')
        D=(pickle.load(f))
        f.close()
        self.axis=D['axis']
        self.Positions=np.array(D['Positions'])
        self.WavelengthArray,self.Data=D['Wavelengths'],D['Signal']

    def save_cropped_data(self):
        x_lim=self.axis_of_2D_plot.get_xlim()
        wave_lim=self.axis_of_2D_plot.get_ylim()
        index=self.number_of_axis[self.axis]
        x=self.Positions[:,index]
        waves=self.WavelengthArray
        i_x_min=np.argmin(abs(x-x_lim[0]))
        i_x_max=np.argmin(abs(x-x_lim[1]))
        
        i_w_min=np.argmin(abs(waves-wave_lim[0]))
        i_w_max=np.argmin(abs(waves-wave_lim[1]))
        
        path,FileName = os.path.split(self.FilePath)
        NewFileName=path+'\\'+FileName.split('.pkl')[0]+'_cropped.pkl'
        f=open(NewFileName,'wb')
        D={}
        D['axis']=self.axis
        D['Positions']=self.Positions[i_x_min:i_x_max,:]
        D['Wavelengths']=waves[i_w_min:i_w_max]
        D['Signal']=self.Data[i_w_min:i_w_max,i_x_min:i_x_max]
        pickle.dump(D,f)
        f.close()
        print('Cropped data saved to {}'.format(FileName))

    def plot_single_spectrum_from_file(self):
        with open(self.single_spectrum_path,'rb') as f:
            print('loading data for analyzer from ',self.single_spectrum_path)
            Data=(pickle.load(f))
        plt.figure()
        plt.plot(Data[:,0],Data[:,1])
        plt.xlabel('Wavelength, nm')
        plt.ylabel('Spectral power density')
        
    
    
    def CalculateLinewidth_1(self,Xarray,Yarray,IndexOfMinimum,AreaToSearch):
        Ymin=Yarray[IndexOfMinimum]
        NewYarray=Yarray[IndexOfMinimum-AreaToSearch:IndexOfMinimum+AreaToSearch]
        Edges=np.argsort(abs(NewYarray-(Ymin+3)))
        if len(Edges)>6:
            LineWidths=np.diff(Xarray[Edges[0:5]])
            return np.max(LineWidths)
        
        else:
            return 0
        
    def CalculateLinewidth_2(self,Xarray,Yarray,IndexOfMinimum,AreaToSearch):
        Ymin=Yarray[IndexOfMinimum]
        NewYarray=Yarray[IndexOfMinimum-AreaToSearch:IndexOfMinimum+AreaToSearch]
        NewYarray=10**(NewYarray/10)
        Ymax=max(NewYarray)
        Edges=np.argsort(abs(NewYarray-(Ymin+Ymax)/2))
        if len(Edges)>6:
            LineWidths=np.diff(Xarray[Edges[0:5]])
            return np.max(LineWidths)
        
        else:
            return 0
        
    def forward(self,x):
        return (x-self.lambda_0)/self.lambda_0*self.Radius*refractive_index
    
    def backward(self,y):
        return y/self.Radius/refractive_index*self.lambda_0+self.lambda_0
        
    def plot_sample_shape(self):
        from mpl_toolkits.mplot3d import Axes3D
        if self.Data is None: self.load_data()
        plt.figure()
        ax = plt.axes(projection='3d')
        ax.plot(self.Positions[:,2],self.Positions[:,0],self.Positions[:,1])
        ax.set_xlabel('Z,steps')
        ax.set_ylabel('X,steps')
        ax.set_zlabel('Y,steps')
        plt.gca().invert_zaxis()
        plt.gca().invert_xaxis()
    
    def plot2D(self):
        if self.Data is None:
            self.load_data()
        self.lambda_0=min(self.WavelengthArray)
        index=self.number_of_axis[self.axis]
        Positions=self.Positions[:,index]
        plt.figure()
        plot=plt.contourf(Positions,self.WavelengthArray,self.Data,200,cmap=self.Cmap)
#        plot=plt.gca().pcolorfast(Positions,WavelengthArray)
        ax1=plt.gca()
        if self.axis=='W':
            plt.xlabel('Wavelength,nm')
            plt.colorbar(plot,ax=ax1)
        else:
            plt.xlabel('Position, steps (2.5 um each)')
            ax2=ax1.twiny()
            ax2.set_xlabel('Distance, um')
            ax2.set_xlim([np.min(Positions)*2.5,np.max(Positions)*2.5])
            ax3=ax1.secondary_yaxis('right',functions=(self.forward, self.backward))
            ax3.set_ylabel('Effective radius variation, nm')
            plt.colorbar(plot,ax=ax3)
        
        plt.ylabel('Wavelength, nm')
        
        plt.tight_layout()
        self.axis_of_2D_plot=ax1
        

        
    
    def plotSlice(self,position, MinimumPeakDepth,axis_to_process='Z'):
        if self.Data is None:
            self.load_data()
        Positions=self.Positions[:,self.number_of_axis[self.axis]]
        i=np.argmin(abs(Positions-position))
        SignalData=self.Data[:,i]
        plt.figure()
        plt.plot(self.WavelengthArray,SignalData)
        plt.title('Position=' + str(Positions[i])+ ' steps along axis '+axis_to_process) 
        peakind2,_=find_peaks(abs(SignalData-np.nanmean(SignalData)),height=MinimumPeakDepth , distance=(self.MinimumPeakDistance))
        plt.plot(self.WavelengthArray[peakind2], SignalData[peakind2], '.')
        plt.tight_layout()
        
        
    def extractERV(self,MinimumPeakDepth,MinWavelength,MaxWavelength,axis_to_process='Z'):
        time1=time.time()
        if self.Data is None:
            self.load_data()
        NumberOfWavelength,Number_of_positions = self.Data.shape
        LineWidthArray=np.zeros(Number_of_positions)
        PeakWavelengthArray=np.zeros(Number_of_positions)
        PeakWavelengthMatrix=np.zeros(np.shape(self.Data))
        PeakWavelengthMatrix[:]=np.nan
        WavelengthArray=self.WavelengthArray
        Positions=self.Positions[:,self.number_of_axis[self.axis]]
        
        PeakWavelengthArray=[]
        LineWidthArray=[]
        Pos=[]
        for Zind, Z in enumerate(range(0,Number_of_positions)):
            print(Z,Zind)
            peakind,_=find_peaks(abs(self.Data[:,Zind]-np.nanmean(self.Data[:,Zind])),height=MinimumPeakDepth , distance=(self.MinimumPeakDistance))
            NewPeakind=np.extract((WavelengthArray[peakind]>MinWavelength) & (WavelengthArray[peakind]<MaxWavelength),peakind)
            NewPeakind=NewPeakind[np.argsort(-WavelengthArray[NewPeakind])] ##sort in wavelength decreasing
        #    peakind2=np.argsort(-Data[peakind1,Zind])
            if len(NewPeakind)>self.IndexOfPeakOfInterest:
                try:
                    LineWidthArray.append(self.CalculateLinewidth_2(WavelengthArray,self.Data[:,Zind],NewPeakind[self.IndexOfPeakOfInterest],self.AreaToSearch))
                except:
                    print('Error while deriving Linewidth')
                    LineWidthArray.append(0)
                PeakWavelengthArray.append(WavelengthArray[NewPeakind[self.IndexOfPeakOfInterest]])
                PeakWavelengthMatrix[NewPeakind[self.IndexOfPeakOfInterest],Zind]=-self.Data[NewPeakind[self.IndexOfPeakOfInterest],Zind]
                Pos.append(Positions[Zind])
        
        
        path,FileName = os.path.split(self.FilePath)
        NewFileName=path+'\\'+FileName.split('.pkl')[0]+'_ERV.txt'
        np.savetxt(NewFileName,np.transpose(np.stack((np.array(Pos),np.array(PeakWavelengthArray),np.array(LineWidthArray)))))
        
        time2=time.time()
        print('Time used =', time2-time1 ,' s')
        plt.figure()
        plt.clf()
        plt.plot(Pos,LineWidthArray)
        plt.xlabel('Step Number')
        plt.ylabel('Linewidth, nm')
        plt.tight_layout()
        plt.figure()
        plt.clf()
        plt.plot(Pos,PeakWavelengthArray,'.')
        plt.xlabel('Step Number')
        plt.ylabel('Wavelength, nm')
        plt.tight_layout()
        plt.figure()
        plt.clf()
        plt.contourf(Positions,self.WavelengthArray,self.Data,200,cmap='jet')
        plt.pcolormesh(Positions,self.WavelengthArray,PeakWavelengthMatrix)
        plt.tight_layout()
        
if __name__ == "__main__":
    os.chdir('..')
    analyzer=AnalyzerForSpectrogram(os.getcwd()+'\\ProcessedData\\Processed_spectrogram_cropped.pkl')

#    AnalyzerForSpectrogram.plotSlice(100)
    analyzer.plot2D()
    analyzer.extractERV(18,15,2000)
#    Analyzer.save_cropped_data()
    
