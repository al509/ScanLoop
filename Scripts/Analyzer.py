# -*- coding: utf-8 -*-
"""
This is the wrapper of SNAP_experiment.SNAP class to incorporate it to the SCANLOOP

@author: Ilya
"""
import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import time
from PyQt5.QtCore import QObject
import pickle
from scipy.signal import find_peaks
from Scripts.SNAP_experiment import SNAP

class Analyzer(QObject,SNAP):
        def __init__(self, path:str):
            '''
            path: 
            '''
            super().__init__(None)
            self.single_spectrum_path=None
            self.file_path=path
            
        def save_cropped_data(self):
            x_lim=self.fig_spectrogram.axes[0].get_xlim()
            wave_lim=self.fig_spectrogram.axes[0].get_xlim()
            index=self.axes_number[self.axis]
            x=self.positions[:,index]
            i_x_min=np.argmin(abs(x-x_lim[0]))
            i_x_max=np.argmin(abs(x-x_lim[1]))
            
            i_w_min=np.argmin(abs(self.wavelengths-wave_lim[0]))
            i_w_max=np.argmin(abs(self.wavelengths-wave_lim[1]))
            
            path,FileName = os.path.split(self.file_path)
            NewFileName=path+'\\'+FileName.split('.pkl')[0]+'_cropped.pkl'
            f=open(NewFileName,'wb')
            D={}
            D['axis']=self.axis
            D['Positions']=self.positions[i_x_min:i_x_max,:]
            D['Wavelengths']=self.wavelengths[i_w_min:i_w_max]
            D['Signal']=self.transmission[i_w_min:i_w_max,i_x_min:i_x_max]
            pickle.dump(D,f)
            f.close()
            print('Cropped data saved to {}_cropped.pkl'.format(FileName.split('.pkl')[0]))

        def plot_single_spectrum_from_file(self):
            with open(self.single_spectrum_path,'rb') as f:
                print('loading data for analyzer from ',self.single_spectrum_path)
                Data=(pickle.load(f))
            plt.figure()
            plt.plot(Data[:,0],Data[:,1])
            plt.xlabel('Wavelength, nm')
            plt.ylabel('Spectral power density, dBm')
            
        def plot2D(self):
            self.plot_spectrogram()
            
        def plot_and_analyze_slice(self,position, MinimumPeakDepth,axis_to_process='Z'):
            fig=self.plot_spectrum(position)
            i=np.argmin(abs(self.x-position))
            SignalData=self.transmission[:,i]
            peakind2,_=find_peaks(abs(SignalData-np.nanmean(SignalData)),height=MinimumPeakDepth , distance=10)
            plt.plot(self.wavelengths[peakind2], SignalData[peakind2], '.')
            plt.tight_layout()
        
        def extractERV(self,MinimumPeakDepth,MinWavelength,MaxWavelength,axis_to_process='Z'):
            positions,peak_wavelengths, ERV, linewidths=SNAP.extract_ERV(self,MinimumPeakDepth,MinWavelength,
                                                        MaxWavelength, indicate_ERV_on_spectrogram=True)
            path,FileName = os.path.split(self.file_path)
            NewFileName=path+'\\'+FileName.split('.pkl')[0]+'_ERV.txt'
            np.savetxt(NewFileName,np.transpose(np.vstack((positions,peak_wavelengths,ERV,linewidths))))
        
  

if __name__ == "__main__":
    analyzer=Analyzer('')
    os.chdir('..')
    analyzer.file_path=os.getcwd()+'\\Test_spectrogram.pkl'
    analyzer.extractERV(1,0,15000)
