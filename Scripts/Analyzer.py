# -*- coding: utf-8 -*-
"""
This is the wrapper of SNAP_experiment.SNAP class to incorporate it to the SCANLOOP

@author: Ilya
"""
import os
import sys
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from PyQt5.QtCore import QObject
import pickle
from scipy.signal import find_peaks
from Scripts.SNAP_experiment import SNAP
import json

class Analyzer(QObject,SNAP):
        def __init__(self, path:str):
            '''
            path: 
            '''
            super().__init__(None)
            self.single_spectrum_path=None
            self.file_path=path
            self.plotting_parameters_file=os.path.dirname(sys.argv[0])+'\\plotting_parameters.txt'
            
        def save_cropped_data(self):
            x_lim=self.fig_spectrogram.axes[0].get_xlim() #positions
            wave_lim=self.fig_spectrogram.axes[0].get_ylim()
            i_x_min=np.argmin(abs(self.x-x_lim[0]))
            i_x_max=np.argmin(abs(self.x-x_lim[1]))
            
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
            with open(self.plotting_parameters_file,'r') as f:
                parameters_dict=json.load(f)
            self.plot_spectrogram(**parameters_dict)
            
        def plot_and_analyze_slice(self,position, MinimumPeakDepth,axis_to_process='Z'):
            with open(self.plotting_parameters_file,'r') as f:
                parameters_dict=json.load(f)
            fig=self.plot_spectrum(position,language=parameters_dict['language'])
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
    analyzer.file_path=os.getcwd()+'\\Test_spectrogram_cropped.pkl'
    analyzer.load_data(analyzer.file_path)
    analyzer.plot_spectrogram()
    # analyzer.extractERV(1,0,15000)
