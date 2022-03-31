# -*- coding: utf-8 -*-
"""
This is the wrapper of SNAP_experiment.SNAP class to incorporate it to the SCANLOOP

@author: Ilya


"""
__date__='2022.04.01'

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

lambda_to_nu=125e3 #MHz/nm

class Analyzer(QObject):
        def __init__(self, path:str,parameters=None):
            '''
            path: 
            '''
            super().__init__(None)
            self.single_spectrum_path=None
            self.file_path=path
            self.plotting_parameters_file_path=os.path.dirname(sys.argv[0])+'\\plotting_parameters.txt'
            self.single_spectrum_figure=None
            self.figure_spectrogram=None
            self.number_of_peaks_to_search=1
            self.min_peak_level=1
            self.min_peak_distance=10
            self.min_wave=1500
            self.max_wave=1600
            self.slice_position=0
            self.find_widths=False
            self.indicate_ERV_on_spectrogram=True
            self.plot_results_separately=False
            self.N_points_for_fitting=0
            self.iterate_different_N_points=False
            self.max_N_points_for_fitting=100
            self.FFTFilter_low_freq_edge=0.00001
            self.FFTFilter_high_freq_edge=0.01
            
            self.SNAP=None
            
            self.type_of_SNAP_file='SNAP'
            
            
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
            Seriazible attributes of the Analyzer object
            '''
            d=dict(vars(self)).copy() #make a copy of the vars dictionary
            del d['SNAP']
            del d['single_spectrum_figure']
            del d['figure_spectrogram']
            return d
        
        def load_data(self,path):
            f=open(path,'rb')
            D=(pickle.load(f))
            f.close()
            if isinstance(D,SNAP_experiment.SNAP):
                print('loading SNAP data for analyzer from ',path)
                self.SNAP=D
            else:
                print('loading old style SNAP data for analyzer from ',path)
                SNAP_object=SNAP_experiment.SNAP()
                SNAP_object.axis_key=D['axis']
                Positions=np.array(D['Positions'])
                wavelengths,exp_data=D['Wavelengths'],D['Signal']
                try:
                    scale=D['spatial_scale']
                    if scale=='microns':
                        pass
                except KeyError:
                        print('Spatial scale is defined as steps 2.5 um each')
                        Positions=Positions*2.5
                try:
                    SNAP_object.date=D['date']
                except KeyError:
                    print('No date indicated')
                    SNAP_object.date='_'
                

                SNAP_object.wavelengths=wavelengths
                SNAP_object.transmission=exp_data
                
                SNAP_object.lambda_0=np.min(wavelengths)
                SNAP_object.positions=Positions
                self.SNAP=SNAP_object
                

        def save_as_pkl3d(self):
            path,FileName = os.path.split(self.file_path)    
            NewFileName=path+'\\'+FileName.split('.')[-2]+'.pkl3d'

            D={}
            D['axis']=self.SNAP.axis_key
            D['spatial_scale']='microns'
            D['Positions']=self.SNAP.positions
            D['Wavelengths']=self.SNAP.wavelengths
            D['Signal']=self.SNAP.transmission
            from datetime import datetime
            D['date']=self.SNAP.date
            print('spectrogram saved as ' +NewFileName)
            with open(NewFileName,'wb') as f:
                pickle.dump(D,f)
                        
        def save_cropped_data(self):
            x_lim=self.figure_spectrogram.axes[0].get_xlim() #positions
            wave_lim=self.figure_spectrogram.axes[0].get_ylim()
            i_x_min=np.argmin(abs(self.SNAP.positions[:,self.SNAP.axes_dict[self.SNAP.axis_key]]-x_lim[0]))
            i_x_max=np.argmin(abs(self.SNAP.positions[:,self.SNAP.axes_dict[self.SNAP.axis_key]]-x_lim[1]))
            
            i_w_min=np.argmin(abs(self.SNAP.wavelengths-wave_lim[0]))
            i_w_max=np.argmin(abs(self.SNAP.wavelengths-wave_lim[1]))
            path,FileName = os.path.split(self.file_path)
            NewFileName=path+'\\'+FileName.split('.')[-2]+'_cropped.SNAP'
            import copy
            new_SNAP=copy.deepcopy(self.SNAP)
            new_SNAP.positions=self.SNAP.positions[i_x_min:i_x_max,:]
            new_SNAP.wavelengths=self.SNAP.wavelengths[i_w_min:i_w_max]
            new_SNAP.transmission=self.SNAP.transmission[i_w_min:i_w_max,i_x_min:i_x_max]
            f=open(NewFileName,'wb')
            pickle.dump(new_SNAP,f)
            f.close()
            print('Cropped data saved to {}'.format(NewFileName))
            
        def save_slice_data(self):
            '''
            save data that is plotted on figure with slice
            '''
            line = self.single_spectrum_figure.gca().get_lines()[0]
            waves = line.get_xdata()
            signal = line.get_ydata()
            wave_min,wave_max=self.single_spectrum_figure.gca().get_xlim()
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
            elif self.single_spectrum_path is not None:
                path,FileName = os.path.split(self.single_spectrum_path)
            NewFileName=path+'\\'+FileName.split('.')[-2]+'_at_{}'.format(self.slice_position)
            f = open(NewFileName+'.pkl',"wb")
            pickle.dump(Data,f)
            f.close()
            print('spectrum has been saved to ', NewFileName+'.pkl')
        

        def plot_single_spectrum_from_file(self):
            with open(self.single_spectrum_path,'rb') as f:
                print('loading data for analyzer from ',self.single_spectrum_path)
                Data=(pickle.load(f))
            self.single_spectrum_figure=plt.figure()
            plt.plot(Data[:,0],Data[:,1])
            plt.xlabel('Wavelength, nm')
            plt.ylabel('Spectral power density, dBm')
            plt.tight_layout()

            
        def plot_spectrogram(self):
            if self.SNAP is None:
                self.load_data(self.file_path)
            
            with open(self.plotting_parameters_file_path,'r') as f:
                p=json.load(f)

            w_0=np.mean(self.SNAP.wavelengths)
            x=self.SNAP.positions[:,self.SNAP.axes_dict[self.SNAP.axis_key]]
            def _convert_ax_Wavelength_to_Radius(ax_Wavelengths):
                """
                Update second axis according with first axis.
                """
                y1, y2 = ax_Wavelengths.get_ylim()
                print(y1,y2)
                nY1=(y1-self.SNAP.lambda_0)/w_0*self.SNAP.R_0*self.SNAP.refractive_index*1e3
                nY2=(y2-self.SNAP.lambda_0)/w_0*self.SNAP.R_0*self.SNAP.refractive_index*1e3
                ax_Radius.set_ylim(nY1, nY2)
                
            def _forward(x):
                return (x-self.SNAP.lambda_0)/w_0*self.SNAP.R_0*self.SNAP.refractive_index*1e3
    
            def _backward(x):
                return self.SNAP.lambda_0 + w_0*x/self.SNAP.R_0/self.SNAP.refractive_index/1e3
        
        
            
            if (p['new_figure']) or (p['figsize']!=None):
                fig=plt.figure(figsize=p['figsize'])
            else:
                fig=plt.gcf()
            
            plt.clf()
            matplotlib.rcParams.update({'font.size': p['font_size']})
            
            if not p['enable_offset']: plt.rcParams['axes.formatter.useoffset'] = False
            
            ax_Wavelengths = fig.subplots()
            try:
                im = ax_Wavelengths.pcolorfast(x,self.SNAP.wavelengths,self.SNAP.transmission,50,cmap=p['cmap'],vmin=p['vmin'],vmax=p['vmax'])
            except:
                im = ax_Wavelengths.contourf(x,self.SNAP.wavelengths,self.SNAP.transmission,50,cmap=p['cmap'],vmin=p['vmin'],vmax=p['vmax'])
            if p['ERV_axis']:
                ax_Radius = ax_Wavelengths.secondary_yaxis('right', functions=(_forward,_backward))
                # ax_Wavelengths.callbacks.connect("ylim_changed", _convert_ax_Wavelength_to_Radius)
            
            if p['position_in_steps_axis']:
                ax_steps=ax_Wavelengths.twiny()
                ax_steps.set_xlim([np.min(x)/2.5,np.max(x)/2.5])
                try:
                    clb=fig.colorbar(im,ax=ax_steps,pad=p['colorbar_pad'],location=p['colorbar_location'])
                except TypeError:
                    print('WARNING: update matplotlib up to 3.4.2 to plot colorbars properly')
                    clb=fig.colorbar(im,ax=ax_steps,pad=p['colorbar_pad'])
            else:
                try:
                    clb=fig.colorbar(im,ax=ax_Wavelengths,pad=p['colorbar_pad'],location=p['colorbar_location'])
                except TypeError:
                    print('WARNING: update matplotlib up to 3.4.2 to plot colorbars properly')
                    clb=fig.colorbar(im,ax=ax_Wavelengths,pad=p['colorbar_pad'])
    
            if p['language']=='eng':
                ax_Wavelengths.set_xlabel(r'Position, $\mu$m')
                ax_Wavelengths.set_ylabel('Wavelength, nm')
                try:
                    ax_Radius.set_ylabel('$\Delta r_{eff}$, nm')
                except: pass
                if self.SNAP.transmission_scale=='log':
                    if p['colorbar_title_position']=='right':
                        clb.ax.set_ylabel('dB',rotation= p['colorbar_title_rotation'],labelpad=5)
                    else:
                        clb.ax.set_title('dB',labelpad=5)
                if p['title']:
                    plt.title('experiment')
                try:
                    ax_steps.set_xlabel('Position, steps')
                except: pass 
            
            elif p['language']=='ru':
                ax_Wavelengths.set_xlabel('Расстояние, мкм')
                ax_Wavelengths.set_ylabel('Длина волны, нм')
                try:
                    ax_Radius.set_ylabel('$\Delta r_{eff}$, нм')
                except: pass
                if self.SNAP.transmission_scale=='log':
                    if p['colorbar_title_position']=='right':
                        clb.ax.set_ylabel('дБ',rotation= p['colorbar_title_rotation'])
                    else:
                        clb.ax.set_title('дБ')
                if p['title']:
                    plt.title('эксперимент')
                try:
                    ax_steps.set_xlabel('Расстояние, шаги')
                except: pass 
            fig.tight_layout()
            self.figure_spectrogram=fig
            
            
        def plot_sample_shape(self):
            fig=plt.figure()
            ax = plt.axes(projection='3d')
            ax.plot(self.SNAP.positions[:,2],self.SNAP.positions[:,0],self.SNAP.positions[:,1])
            ax.set_xlabel('Z, microns')
            ax.set_ylabel('X, microns')
            ax.set_zlabel('Y, microns')
            plt.gca().invert_zaxis()
            plt.gca().invert_xaxis()
            return fig
            
        def plot_slice(self,position):
            '''
            plot slice using SNAP object parameters
            '''
            self.slice_position=position
            if self.SNAP.transmission is None:
                self.load_data(self.file_path)
            with open(self.plotting_parameters_file_path,'r') as f:
                p=json.load(f)
                
            fig=plt.figure()
            plt.clf()
    
            ax = plt.axes()
            ax.minorticks_on()
            ax.grid(which='major', linestyle=':', linewidth='0.1', color='black')
            ax.grid(which='minor', linestyle=':', linewidth='0.1', color='black')
            x=self.SNAP.positions[:,self.SNAP.axes_dict[self.SNAP.axis_key]]
            index=np.argmin(abs(position-x))
            plt.plot(self.SNAP.wavelengths,self.SNAP.transmission[:,index])
            
            if p['language']=='eng':
                plt.xlabel('Wavelength, nm')
                plt.ylabel('Spectral power density, dBm')
            elif p['language']=='ru':
                plt.xlabel('Длина волны, нм')
                plt.ylabel('Спектральная плотность мощности, дБм')
            self.single_spectrum_figure=fig
            
        def analyze_spectrum(self,fig):
            '''
            find all minima in represented part of slice and derive parameters of Lorenzian fitting for the minimal minimum
            '''
            axes=fig.gca()
            line =axes.get_lines()[0]
            waves = line.get_xdata()
            signal = line.get_ydata()
            wave_min,wave_max=axes.get_xlim()
            index_min=np.argmin(abs(waves-wave_min))
            index_max=np.argmin(abs(waves-wave_max))
            waves=waves[index_min:index_max]
            signal=signal[index_min:index_max]
            if all(np.isnan(signal)):
                print('Error. Signal is NAN only')
                return
            
            peakind2,_=find_peaks(abs(signal-np.nanmean(signal)),height=self.min_peak_level , distance=self.min_peak_distance)
            if len(peakind2)>0:
                axes.plot(waves[peakind2], signal[peakind2], '.')
                
                main_peak_index=np.argmax(abs(signal[peakind2]-np.nanmean(signal)))
                # wavelength_main_peak=waves[peakind2][main_peak_index]
                peakind2=peakind2[np.argsort(-waves[peakind2])] ##sort in wavelength decreasing
                wavelength_main_peak=waves[peakind2[0]]
                
                
                try:
                    parameters, waves_fitted,signal_fitted=SNAP_experiment.get_Fano_fit(waves,signal,wavelength_main_peak)
                except Exception as e:
                        print('Error: {}'.format(e))
                axes.plot(waves_fitted, signal_fitted, color='green')             
                [non_res_transmission, Fano_phase, resonance_position,linewidth,depth]=parameters
                results_text1='$|S_0|$={:.2f} \n arg(S)={:.2f} $\pi$  \n $\lambda_0$={:.4f}  nm \n $\Delta \lambda={:.5f}$ nm \n Depth={:.3e} \n'.format(non_res_transmission,Fano_phase, resonance_position,linewidth,depth)
                delta_coupling=depth/2*lambda_to_nu # in MHz
                delta_0=(linewidth/2-depth/2)*lambda_to_nu  # in MHz
                Q_factor=resonance_position/linewidth
                results_text2='\n $\delta_c$={:.2f} MHz \n $\delta_0$={:.2f} MHz \n Q-factor={:.2e}'.format(delta_coupling,delta_0,Q_factor)
                results_text=results_text1+results_text2
                for t in axes.texts:
                    t.set_visible(False)
                axes.text(0.8, 0.5,results_text,
                         horizontalalignment='center',
                         verticalalignment='center',
                         transform = axes.transAxes)
            else:
                print('Error: No peaks found')
            # plt.tight_layout()
            fig.canvas.draw_idle()
            


        
            
        
        # def extract_ERV(self,N_peaks,min_peak_depth,distance, MinWavelength,MaxWavelength,axis_to_process='Z',plot_results_separately=False):
        def extract_ERV(self):
                        # positions,peak_wavelengths, ERV, resonance_parameters=SNAP_experiment.SNAP.extract_ERV(self,
            positions,peak_wavelengths, ERV, resonance_parameters=self.SNAP.extract_ERV(self.number_of_peaks_to_search,self.min_peak_level,
                                                                                        self.min_peak_distance,self.min_wave,self.max_wave,
                                                                                        self.find_widths, self.N_points_for_fitting,
                                                                                        self.iterate_different_N_points,self.max_N_points_for_fitting)
            path,FileName = os.path.split(self.file_path)
            NewFileName=path+'\\'+FileName.split('.')[-2]+'_ERV.pkl'
            with open(NewFileName,'wb') as f:
                ERV_params={'positions':positions,'peak_wavelengths':peak_wavelengths,'ERVs':ERV,'resonance_parameters':resonance_parameters,'fitting_parameters':self.get_parameters()}
                pickle.dump(ERV_params, f)
            
            
            x=self.SNAP.positions[:,self.SNAP.axes_dict[self.SNAP.axis_key]]
            if self.figure_spectrogram is not None and self.indicate_ERV_on_spectrogram:
                if len(self.figure_spectrogram.axes[0].lines)>1:
                    for line in self.figure_spectrogram.axes[0].lines[1:]: line.remove()
                for i in range(0,self.number_of_peaks_to_search):
                    self.figure_spectrogram.axes[0].plot(x,peak_wavelengths[:,i])
                self.figure_spectrogram.canvas.draw()
            elif self.figure_spectrogram is None and self.indicate_ERV_on_spectrogram:
                self.plot_spectrogram()
                for i in range(0,self.number_of_peaks_to_search):
                    self.figure_spectrogram.axes[0].plot(x,peak_wavelengths[:,i])
                    line=self.figure_spectrogram.axes[0].plot(x,peak_wavelengths[:,i])
            
            
            if self.plot_results_separately:
                self.plot_ERV_params(ERV_params,self.find_widths)
            
        
        def plot_ERV_params(self,params_dict:dict,find_widths=True):
            positions=params_dict['positions']
            peak_wavelengths=params_dict['peak_wavelengths']
            number_of_peaks_to_search=np.shape(peak_wavelengths)[1]
            resonance_parameters_array=params_dict['resonance_parameters']
            
            plt.figure()
            for i in range(0,number_of_peaks_to_search):
                plt.plot(positions,peak_wavelengths[:,i])
            plt.xlabel('Distance, $\mu$m')
            plt.ylabel('Cut-off wavelength, nm')
            plt.title('Cut-off wavelength')
            plt.tight_layout()
  
            plt.figure()
            plt.title('Depth and Linewidth $\Delta \lambda$')
            for i in range(0,number_of_peaks_to_search):
                plt.plot(positions,resonance_parameters_array[:,i,2],color='blue')
            plt.xlabel('Distance, $\mu$m')
            plt.ylabel('Depth ',color='blue')
            plt.gca().tick_params(axis='y', colors='blue')
            plt.gca().twinx()
            # plt.figure()
            for i in range(0,number_of_peaks_to_search):
                plt.plot(positions,resonance_parameters_array[:,i,3], color='red')
            plt.ylabel('Linewidth $\Delta \lambda$, nm',color='red')
            plt.gca().tick_params(axis='y', colors='red')
            plt.tight_layout()
            
            plt.figure()
            plt.title('Nonresonanse transmission $|S_0|$ and its phase')
            for i in range(0,number_of_peaks_to_search):
                plt.plot(positions,resonance_parameters_array[:,i,0],color='blue')
            plt.xlabel('Distance, $\mu$m')
            plt.ylabel('Nonresonance transmission $|S_0|$',color='blue')
            plt.gca().tick_params(axis='y', colors='blue')
            plt.gca().twinx()
            # plt.figure()
            for i in range(0,number_of_peaks_to_search):
                plt.plot(positions,resonance_parameters_array[:,i,1], color='red')
            plt.ylabel('Phase',color='red')
            plt.gca().tick_params(axis='y', colors='red')
            plt.tight_layout()
            
            plt.figure()
            plt.title('$\delta_0$ and $\delta_c$')
            for i in range(0,number_of_peaks_to_search):
                plt.plot(positions,resonance_parameters_array[:,i,4],color='blue')
            plt.xlabel('Distance, $\mu$m')
            plt.ylabel('$\delta_c$, nm',color='blue')
            plt.gca().tick_params(axis='y', colors='blue')
            plt.gca().twinx()
            # plt.figure()
            for i in range(0,number_of_peaks_to_search):
                plt.plot(positions,resonance_parameters_array[:,i,5], color='red')
            plt.ylabel('$\delta_0$, nm',color='red')
            plt.gca().tick_params(axis='y', colors='red')
            plt.tight_layout()
        
        
        def plot_ERV_from_file(self,file_name):
            with open(file_name,'rb') as f:
                d=pickle.load(f)
            self.plot_ERV_params(d)
            
            
        def apply_FFT_to_spectrogram(self):
            self.SNAP.apply_FFT_filter(self.FFTFilter_low_freq_edge,self.FFTFilter_high_freq_edge)
            self.plot_spectrogram()
                
        
  

if __name__ == "__main__":
    
    os.chdir('..')
    
    
    
    #%%
    analyzer=Analyzer(os.getcwd()+'\\ProcessedData\\flattened_spectrogram_cropped_cropped_1.pkl')
    analyzer.plotting_parameters_file_path=os.getcwd()+'\\plotting_parameters.txt'
    
    analyzer.plot_spectrogram()
    # analyzer.plot_slice(800)
    
    import json
    f=open('Parameters.txt')
    Dicts=json.load(f)
    f.close()
    analyzer.set_parameters(Dicts['Analyzer'])
    analyzer.extract_ERV()
    

    # 

