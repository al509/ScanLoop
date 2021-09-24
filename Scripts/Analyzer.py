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
import Scripts.SNAP_experiment
import json

class Analyzer(QObject,Scripts.SNAP_experiment.SNAP):
        def __init__(self, path:str):
            '''
            path: 
            '''
            super().__init__(None)
            self.single_spectrum_path=None
            self.file_path=path
            self.plotting_parameters_file=os.path.dirname(sys.argv[0])+'\\plotting_parameters.txt'
            self.fig_slice=None
            
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
            self.fig_slice=plt.figure()
            plt.plot(Data[:,0],Data[:,1])
            plt.xlabel('Wavelength, nm')
            plt.ylabel('Spectral power density, dBm')
            plt.tight_layout()
            
        def plot2D(self):
            with open(self.plotting_parameters_file,'r') as f:
                parameters_dict=json.load(f)
            self.plot_spectrogram(**parameters_dict)
            
        def plot_slice(self,position,axis_to_process='Z'):
            '''
            plot slice using SNAP object parameters
            '''
            with open(self.plotting_parameters_file,'r') as f:
                parameters_dict=json.load(f)
            self.fig_slice=self.plot_spectrum(position,language=parameters_dict['language'])
            plt.tight_layout()
            
        def analyze_slice(self,MinimumPeakDepth):
            '''
            find all minima in represented part of slice and derive parameters of Lorenzian fitting for the minimal minimum
            '''
            line = self.fig_slice.gca().get_lines()[0]
            waves = line.get_xdata()
            signal = line.get_ydata()
            
            
            peakind2,_=find_peaks(abs(signal-np.nanmean(signal)),height=MinimumPeakDepth , distance=10)
            plt.plot(waves[peakind2], signal[peakind2], '.')
            wave_min,wave_max=self.fig_slice.gca().get_xlim()
            index_min=np.argmin(abs(waves-wave_min))
            index_max=np.argmin(abs(waves-wave_max))
            waves=waves[index_min:index_max]
            signal=signal[index_min:index_max]
            popt, waves_fitted,signal_fitted=Scripts.SNAP_experiment.get_lorenzian_fit(waves,signal)
            plt.plot(waves_fitted, signal_fitted, color='red')
            resutls_text='$|S_0|$={:.2f} \n arg(S)={:.2f} $\pi$  \n $\lambda_0$={:.4f}  nm \n $\Delta \lambda={:.4f}$ nm \n Depth={:.3e} \n Q factor={:.1e}'.format(*popt,popt[2]/popt[3])
            plt.text(0.8, 0.5,resutls_text,
                     horizontalalignment='center',
                     verticalalignment='center',
                     transform = plt.gca().transAxes)
            plt.tight_layout()
            plt.show()
            plt.draw()
            
        def save_slice_data(self):
            '''
            save data that is plotted on figure with slice
            '''
            line = self.fig_slice.gca().get_lines()[0]
            waves = line.get_xdata()
            signal = line.get_ydata()
            wave_min,wave_max=self.fig_slice.gca().get_xlim()
            index_min=np.argmin(abs(waves-wave_min))
            index_max=np.argmin(abs(waves-wave_max))
            Data=np.column_stack((waves[index_min:index_max],signal[index_min:index_max]))
            if self.file_path is not None:
                path,FileName = os.path.split(self.file_path)
            elif self.single_spectrum_path() is not None:
                path,FileName = os.path.split(self.single_spectrum_path)
            NewFileName=path+'\\'+FileName.split('.pkl')[0]+'_new_slice'
            f = open(NewFileName+'.pkl',"wb")
            pickle.dump(Data,f)
            f.close()
        
  
            
        
        def extractERV(self,MinimumPeakDepth,MinWavelength,MaxWavelength,axis_to_process='Z'):
            positions,peak_wavelengths, ERV, linewidths=Scripts.SNAP_experiment.SNAP.extract_ERV(self,MinimumPeakDepth,MinWavelength,
                                                        MaxWavelength, indicate_ERV_on_spectrogram=True)
            path,FileName = os.path.split(self.file_path)
            NewFileName=path+'\\'+FileName.split('.pkl')[0]+'_ERV.txt'
            np.savetxt(NewFileName,np.transpose(np.vstack((positions,peak_wavelengths,ERV,linewidths))))
        
  

if __name__ == "__main__":
    analyzer=Analyzer('')
    os.chdir('..')
    analyzer.single_spectrum_path=os.getcwd()+'\\Test_spectrum.pkl'
    analyzer.plot_single_spectrum_from_file()
    analyzer.analyze_slice(1)
    # analyzer.extractERV(1,0,15000)
