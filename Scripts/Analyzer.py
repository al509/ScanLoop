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
try:
    import Scripts.SNAP_experiment as SNAP_experiment
except ModuleNotFoundError:
    import SNAP_experiment
import json

class Analyzer(QObject):
        def __init__(self, path:str,parameters=None):
            '''
            path: 
            '''
            super().__init__(None)
            self.single_spectrum_path=None
            self.file_path=path
            self.plotting_parameters_file=os.path.dirname(sys.argv[0])+'\\plotting_parameters.txt'
            self.fig_slice=None
            self.number_of_peaks_to_search=1
            self.min_peak_level=1
            self.min_peak_distance=10
            self.min_wave=1500
            self.max_wave=1600
            self.find_widths=False
            self.indicate_ERV_on_spectrogram=True
            self.plot_results_separately=False
            
            self.SNAP=None
            
            
        def set_parameters(self,dictionary):
            for key in dictionary:
                try:
                    self.__setattr__(key, dictionary[key])
                except:
                    pass
                
        def get_parameters(self)->dict:
            '''
            Returns
            -------
            Seriazible attributes of the object
            '''
            d=dict(vars(self)) #make a copy of the vars dictionary
            del d['SNAP']
            return d
        
        def load_data(self,path):
            self.SNAP=SNAP_experiment.load_data(path)
            
            
        def save_cropped_data(self):
            x_lim=self.SNAP.fig_spectrogram.axes[0].get_xlim() #positions
            wave_lim=self.SNAP.fig_spectrogram.axes[0].get_ylim()
            i_x_min=np.argmin(abs(self.SNAP.x-x_lim[0]))
            i_x_max=np.argmin(abs(self.SNAP.x-x_lim[1]))
            
            i_w_min=np.argmin(abs(self.SNAP.wavelengths-wave_lim[0]))
            i_w_max=np.argmin(abs(self.SNAP.wavelengths-wave_lim[1]))
            path,FileName = os.path.split(self.file_path)
            NewFileName=path+'\\'+FileName.split('.pkl')[0]+'_cropped.pkl'
            f=open(NewFileName,'wb')
            D={}
            D['axis']=self.SNAP.axis
            D['Positions']=self.SNAP.positions[i_x_min:i_x_max,:]
            D['Wavelengths']=self.SNAP.wavelengths[i_w_min:i_w_max]
            D['Signal']=self.SNAP.transmission[i_w_min:i_w_max,i_x_min:i_x_max]
            pickle.dump(D,f)
            f.close()
            print('Cropped data saved to {}_cropped.pkl'.format(FileName.split('.pkl')[0]))
            
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
            signal=signal[index_min:index_max]
            waves=waves[index_min:index_max]
            # indexes=np.argwhere(~np.isnan(signal))
            # signal=signal[indexes]
            # waves=waves[indexes]
            Data=np.column_stack((waves,signal))
            if self.file_path is not None:
                path,FileName = os.path.split(self.file_path)
            elif self.single_spectrum_path() is not None:
                path,FileName = os.path.split(self.single_spectrum_path)
            NewFileName=path+'\\'+FileName.split('.pkl')[0]+'_new_slice'
            f = open(NewFileName+'.pkl',"wb")
            pickle.dump(Data,f)
            f.close()
            print('spectrum has been saved to ', NewFileName+'.pkl')
        

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
            if self.SNAP is None:
                self.SNAP=SNAP_experiment.load_data(self.file_path)
            
            with open(self.plotting_parameters_file,'r') as f:
                parameters_dict=json.load(f)
            self.SNAP.plot_spectrogram(**parameters_dict)
            
        def plot_sample_shape(self):
            fig=plt.figure()
            ax = plt.axes(projection='3d')
            ax.plot(self.SNAP.positions[:,2],self.SNAP.positions[:,0],self.SNAP.positions[:,1])
            ax.set_xlabel('Z,steps')
            ax.set_ylabel('X,steps')
            ax.set_zlabel('Y,steps')
            plt.gca().invert_zaxis()
            plt.gca().invert_xaxis()
            return fig
            
        def plot_slice(self,position,axis_to_process='Z'):
            '''
            plot slice using SNAP object parameters
            '''
            if self.SNAP.transmission is None:
                self.SNAP=SNAP_experiment.load_data(self.file_path)
            with open(self.plotting_parameters_file,'r') as f:
                parameters_dict=json.load(f)
            self.fig_slice=self.SNAP.plot_spectrum(position,language=parameters_dict['language']) ## plot_spectrum is SNAP_experiment method
            plt.tight_layout()
            
        def analyze_spectrum(self,fig,min_peak_level):
            '''
            find all minima in represented part of slice and derive parameters of Lorenzian fitting for the minimal minimum
            '''
            line = fig.gca().get_lines()[0]
            waves = line.get_xdata()
            signal = line.get_ydata()
            wave_min,wave_max=self.fig_slice.gca().get_xlim()
            index_min=np.argmin(abs(waves-wave_min))
            index_max=np.argmin(abs(waves-wave_max))
            waves=waves[index_min:index_max]
            signal=signal[index_min:index_max]
            if all(np.isnan(signal)):
                print('Error. Signal is NAN only')
                return
            
            peakind2,_=find_peaks(abs(signal-np.nanmean(signal)),height=min_peak_level , distance=10)
            if len(peakind2)>0:
                plt.plot(waves[peakind2], signal[peakind2], '.')
                
                main_peak_index=np.argmax(abs(signal[peakind2]-np.nanmean(signal)))
                # wavelength_main_peak=waves[peakind2][main_peak_index]
                peakind2=peakind2[np.argsort(-waves[peakind2])] ##sort in wavelength decreasing
                wavelength_main_peak=waves[peakind2[0]]
                
                
                try:
                    popt, waves_fitted,signal_fitted=SNAP_experiment.get_Fano_fit(waves,signal,wavelength_main_peak)
                except Exception as e:
                        print('Error: {}'.format(e))
                plt.plot(waves_fitted, signal_fitted, color='red')
                results_text='$|S_0|$={:.2f} \n arg(S)={:.2f} $\pi$  \n $\lambda_0$={:.4f}  nm \n $\Delta \lambda={:.4f}$ nm \n Depth={:.3e} \n Depth/$\Delta \lambda$={:.4f} \n Q factor={:.1e}'.format(*popt,popt[4]/popt[3],popt[2]/popt[3])
                for t in plt.gca().texts:
                    t.set_visible(False)
                plt.text(0.8, 0.5,results_text,
                         horizontalalignment='center',
                         verticalalignment='center',
                         transform = plt.gca().transAxes)
            else:
                print('Error: No peaks found')
            plt.tight_layout()
            plt.show()
            plt.draw()
            


        
            
        
        # def extract_ERV(self,N_peaks,min_peak_depth,distance, MinWavelength,MaxWavelength,axis_to_process='Z',plot_results_separately=False):
        def extract_ERV(self):
                        # positions,peak_wavelengths, ERV, resonance_parameters=SNAP_experiment.SNAP.extract_ERV(self,
            positions,peak_wavelengths, ERV, resonance_parameters=self.SNAP.extract_ERV(self.number_of_peaks_to_search,self.min_peak_level,
                                                                                                   self.min_peak_distance,self.min_wave,self.max_wave,
                                                                                                   self.find_widths, self.indicate_ERV_on_spectrogram, self.plot_results_separately)
            path,FileName = os.path.split(self.file_path)
            NewFileName=path+'\\'+FileName.split('.pkl')[0]+'_ERV.pkl'
            with open(NewFileName,'wb') as f:
                temp={'positions':positions,'peak_wavelengths':peak_wavelengths,'ERVs':ERV,'resonance_parameters':resonance_parameters,'fitting_parameters':(kwargs)}
                pickle.dump(temp, f)
            # np.savetxt(NewFileName,np.transpose(np.vstack((positions,peak_wavelengths,ERV,np.transpose(resonance_parameters)))))
            
        
        
  

if __name__ == "__main__":
    
    os.chdir('..')
    
    
    
    #%%
    analyzer=Analyzer(os.getcwd()+'\\Processed_spectrogram.pkl')
    analyzer.plotting_parameters_file=os.getcwd()+'\\plotting_parameters.txt'
    
    analyzer.plot2D()
    # analyzer.plot_slice(800)
    
    import json
    f=open('Parameters.txt')
    Dicts=json.load(f)
    f.close()
    analyzer.set_parameters(Dicts[1])
    analyzer.extract_ERV()
    

    # 

