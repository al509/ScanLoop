# -*- coding: utf-8 -*-
"""
@author: Ilya


"""
__version__='2.6.6'
__date__='2023.03.07'

import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
import matplotlib
from PyQt5.QtCore import QObject, pyqtSignal
import pickle
from scipy.signal import find_peaks
try:
    import Scripts.SNAP_experiment as SNAP_experiment
    import Scripts.QuantumNumbersStructure as QuantumNumbersStructure
except ModuleNotFoundError as E:
    print(E)
    
    import SNAP_experiment
    import QuantumNumbersStructure
import json


c=299792458 # m/s

class Analyzer(QObject):
    
        S_print=pyqtSignal(str) # signal used to print into main text browser
        S_print_error=pyqtSignal(str) # signal used to print errors into main text browser
     
        def __init__(self, spectrogram_file_path=None,parameters=None):
            '''
            path: 
            '''
            super().__init__(None)
            self.single_spectrum_path=None
            self.spectrogram_file_path=spectrogram_file_path
            self.plotting_parameters_file_path=os.path.dirname(sys.argv[0])+'\\plotting_parameters.txt'
            self.single_spectrum_figure=None
            
            self.type_of_spectrogram='insertion losses'
            self.figure_spectrogram=None
            
            self.number_of_peaks_to_search=1
            self.min_peak_level=0.8
            self.min_peak_distance=0.05
            self.min_wave=1500
            self.max_wave=1600

            self.lambda_0_for_ERV = 1500

            

            self.slice_position=0
            
            self.find_widths=False
            self.indicate_ERV_on_spectrogram=True
            self.plot_results_separately=False
            
            self.bandwidth_for_fitting=0
            self.iterate_different_bandwidths=False
            self.iterating_cost_function_type='linewidth'
            self.max_bandwidth_for_fitting=0.05
            self.derive_taper_cavity_params=False
            
            self.FFTFilter_low_freq_edge=0.00001
            self.FFTFilter_high_freq_edge=0.01
            
            self.quantum_numbers_fitter_dispersion=False
            self.quantum_numbers_fitter_p_max=3
            self.quantum_numbers_fitter_polarizations='both'
            

            self.temperature = 20            
            self.quantum_numbers_fitter_vary_temperature=False
            
            self.SNAP = None          
            
            self.cost_function_figure = None
            self.cost_function_ax = None
            
            '''
            Временно. Для постройки графика функции ошибки от радиуса и температуры
            
            self.cost_function_figure=plt.figure()
            self.cost_function_ax = self.cost_function_figure.add_subplot(1, 1, 1)
            self.cost_function_ax.grid()
            self.cost_function_ax.set_title('Radius dependent cost function', fontsize=14)
            self.cost_function_ax.set_xlabel('Radius, $\mu m$', fontsize=14)
            self.cost_function_ax.set_ylabel('Cost function', fontsize=14)
            '''
            
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
        
        def load_data(self,file_path=None):
            if file_path is not None:
                self.spectrogram_file_path=file_path
            if self.spectrogram_file_path is not None:    
                with open(self.spectrogram_file_path,'rb') as f:
                    loaded_object=(pickle.load(f))

                if isinstance(loaded_object,SNAP_experiment.SNAP):

                    self.S_print.emit('loading SNAP data for analyzer from ' + self.spectrogram_file_path)
                    self.SNAP=loaded_object
                    if not hasattr(self.SNAP, 'type_of_signal'):
                        self.SNAP.type_of_signal='insertion losses'
                        self.SNAP.jones_matrix_used=False
                        self.SNAP.signal=self.SNAP.transmission
                    self.S_print.emit('File has been loaded to SNAP object')
                else:
                    self.S_print.emit('loading old style SNAP data for analyzer from ' + self.spectrogram_file_path)
                    SNAP_object=SNAP_experiment.SNAP()
                    SNAP_object.axis_key=loaded_object['axis']
                    Positions=np.array(loaded_object['Positions'])
                    wavelengths,exp_data=loaded_object['Wavelengths'],loaded_object['Signal']
                    
                
                    try:
                        scale=loaded_object['spatial_scale']
                        if scale=='microns':
                            pass
                    except KeyError:
                            self.S_print_error.emit('Spatial scale is defined as steps 2.5 um each')
                            Positions[:,0:3]=Positions[:,0:3]*2.5
                    try:
                        SNAP_object.date=loaded_object['date']
                    except KeyError:
                        self.S_print_error.emit('No date indicated')
                        SNAP_object.date='_'
                    
    
                    SNAP_object.wavelengths=wavelengths
                    SNAP_object.signal=exp_data
                    
                    SNAP_object.lambda_0=np.min(wavelengths)
                    SNAP_object.positions=Positions
                    try:
                        SNAP_object.type_of_signal=loaded_object['type_of_signal']
                    except KeyError:
                        self.S_print_error.emit('No type of signal indicated')
                        SNAP_object.type_of_signal='insertion losses'
                    try:
                        SNAP_object.R_0=loaded_object['R_0']
                    except KeyError:
                        self.S_print_error.emit('No radius indicated')
                        SNAP_object.R_0=62.5
                    try:
                        SNAP_object.refractive_index=loaded_object['refractive_index']
                    except KeyError:
                        self.S_print_error.emit('No refractive index indicated')
                        SNAP_object.refractive_index=1.45
                    self.SNAP=SNAP_object
                    self.S_print.emit('File has been loaded to SNAP object')
            else:
                self.S_print.emit('SNAP file not chosen')
                

        def resave_SNAP(self,output_file_type='SNAP'):
            try:
                x_lim=self.figure_spectrogram.axes[0].get_xlim() #positions
                wave_lim=self.figure_spectrogram.axes[0].get_ylim()
                i_x_min=np.argmin(abs(self.SNAP.positions[:,self.SNAP.axes_dict[self.SNAP.axis_key]]-x_lim[0]))
                i_x_max=np.argmin(abs(self.SNAP.positions[:,self.SNAP.axes_dict[self.SNAP.axis_key]]-x_lim[1]))
                i_w_min=np.argmin(abs(self.SNAP.wavelengths-wave_lim[0]))
                i_w_max=np.argmin(abs(self.SNAP.wavelengths-wave_lim[1]))
            except:
                i_x_min=0
                i_x_max=-1
                i_w_min=0
                i_w_max=-1
            import copy
            path,FileName = os.path.split(self.spectrogram_file_path)
            
            if output_file_type in ['SNAP','cSNAP']:
                new_SNAP=copy.deepcopy(self.SNAP)
                new_SNAP.positions=self.SNAP.positions[i_x_min:i_x_max,:]
                new_SNAP.wavelengths=self.SNAP.wavelengths[i_w_min:i_w_max]
                new_SNAP.signal=self.SNAP.signal[i_w_min:i_w_max,i_x_min:i_x_max]
                new_SNAP.lambda_0=new_SNAP.wavelengths[0]
                if output_file_type=='SNAP':
                    NewFileName=path+'\\'+FileName.split('.')[-2]+'_resaved.SNAP'
                    new_SNAP.jones_matrixes_used=False
                    new_SNAP.jones_matrixes_array=None
                else:
                    NewFileName=path+'\\'+FileName.split('.')[-2]+'_resaved.cSNAP'
                    new_SNAP.jones_matrixes_used=True
                    new_SNAP.jones_matrixes_array=self.SNAP.jones_matrixes_array[i_w_min:i_w_max,i_x_min:i_x_max,:,:]
                f=open(NewFileName,'wb')
                pickle.dump(new_SNAP,f)
                f.close()
                self.S_print.emit('Data resaved to {}'.format(NewFileName))
                
            elif output_file_type=='pkl3d':
                NewFileName=path+'\\'+FileName.split('.')[-2]+'_resaved.pkl3d'
                D={}
                D['axis']=self.SNAP.axis_key
                D['spatial_scale']='microns'
                D['Positions']=self.SNAP.positions
                D['Wavelengths']=self.SNAP.wavelengths
                D['Signal']=self.SNAP.signal
                D['type_of_signal']=self.SNAP.type_of_signal
                from datetime import datetime
                D['date']=self.SNAP.date
                D['R_0']=self.SNAP.R_0
                D['refractive_index']=self.SNAP.refractive_index
                with open(NewFileName,'wb') as f:
                    pickle.dump(D,f)
                self.S_print.emit('spectrogram saved as ' +NewFileName)

        def delete_slice(self,position):
            self.slice_position=position
            if self.SNAP.signal is None:
                self.load_data()


            x=self.SNAP.positions[:,self.SNAP.axes_dict[self.SNAP.axis_key]]
            index=np.argmin(abs(position-x))
            self.SNAP.signal=np.delete(self.SNAP.signal,index,1)
            self.SNAP.positions=np.delete(self.SNAP.positions,index,0)
            path,FileName = os.path.split(self.spectrogram_file_path)
            NewFileName=path+'\\'+FileName.split('.')[-2]+'_resaved.SNAP'
            f=open(NewFileName,'wb')
            pickle.dump(self.SNAP,f)
            f.close()
            self.S_print.emit('Index {} deleted. Data resaved to {}'.format(index,NewFileName))
    
                            
        # def save_cropped_data(self):
        #     x_lim=self.figure_spectrogram.axes[0].get_xlim() #positions
        #     wave_lim=self.figure_spectrogram.axes[0].get_ylim()
        #     i_x_min=np.argmin(abs(self.SNAP.positions[:,self.SNAP.axes_dict[self.SNAP.axis_key]]-x_lim[0]))
        #     i_x_max=np.argmin(abs(self.SNAP.positions[:,self.SNAP.axes_dict[self.SNAP.axis_key]]-x_lim[1]))
            
        #     i_w_min=np.argmin(abs(self.SNAP.wavelengths-wave_lim[0]))
        #     i_w_max=np.argmin(abs(self.SNAP.wavelengths-wave_lim[1]))
        #     path,FileName = os.path.split(self.spectrogram_file_path)
        #     NewFileName=path+'\\'+FileName.split('.')[-2]+'_cropped.SNAP'
        #     import copy
        #     new_SNAP=copy.deepcopy(self.SNAP)
        #     new_SNAP.positions=self.SNAP.positions[i_x_min:i_x_max,:]
        #     new_SNAP.wavelengths=self.SNAP.wavelengths[i_w_min:i_w_max]
        #     new_SNAP.signal=self.SNAP.signal[i_w_min:i_w_max,i_x_min:i_x_max]
        #     f=open(NewFileName,'wb')
        #     pickle.dump(new_SNAP,f)
        #     f.close()
        #     print('Cropped data saved to {}'.format(NewFileName))
            

        def save_single_spectrum(self):
            '''
            save data that is plotted on current self.single_spectrum_figure
            '''
            line = plt.gca().get_lines()[0]
            waves = line.get_xdata()
            signal = line.get_ydata()
            wave_min,wave_max=plt.gca().get_xlim()
            index_min=np.argmin(abs(waves-wave_min))
            index_max=np.argmin(abs(waves-wave_max))
            signal=signal[index_min:index_max]
            waves=waves[index_min:index_max]
            # indexes=np.argwhere(~np.isnan(signal))
            # signal=signal[indexes]
            # waves=waves[indexes]
            Data=np.column_stack((waves,signal))
            if self.slice_position is None:
                path,FileName = os.path.split(self.single_spectrum_path)
                if FileName.endswith('.pkl'): FileName=FileName[:-4]
                NewFileName=path+'\\'+FileName+'_resaved'
            else:
                path,FileName = os.path.split(self.spectrogram_file_path)
                if FileName.endswith('.pkl'): FileName=FileName[:-4]
                if FileName.endswith('.SNAP'): FileName=FileName[:-5]
                if FileName.endswith('.pkl3d'): FileName=FileName[:-6]
                NewFileName=path+'\\'+FileName+'_at_{}'.format(self.slice_position)
            f = open(NewFileName+'.pkl',"wb")
            pickle.dump(Data,f)
            f.close()
            self.S_print.emit('spectrum has been saved to ' + NewFileName+'.pkl')
        

        def plot_single_spectrum(self):
            self.slice_position=None
            if self.single_spectrum_path.split('.')[-1]=='laserdata':

                self.S_print.emit('loading data for analyzer from ' +self.single_spectrum_path)
                data=np.genfromtxt(self.single_spectrum_path)
                attempts=[]
                
                indexes_of_attempt_start=np.where(np.diff(data[:,0])<0)[0]
                ind_start=0
                if len(indexes_of_attempt_start)>0:
                    
                    for ind_stop in indexes_of_attempt_start:
                        d={}
                        d['times']=data[ind_start:ind_stop,0]
                        d['wavelengths']=data[ind_start:ind_stop,1]
                        d['powers']=data[ind_start:ind_stop,2]*1e3
                        
                        attempts.append(d)
                        ind_start=ind_stop+1
                d={}
                d['times']=data[ind_start:,0]
                d['wavelengths']=data[ind_start:,1]
                d['powers']=data[ind_start:,2]*1e3
                attempts.append(d)
                
                fig1, (ax1, ax2) = plt.subplots(2, 1)
                self.single_spectrum_figure=plt.figure()
                ax3=plt.gca()
                for i,attempt in enumerate(attempts):
                    ax1.plot(attempt['times'],attempt['powers'])
                    ax2.plot(attempt['times'],attempt['wavelengths'])
                    if attempt['wavelengths'][1]-attempt['wavelengths'][0]>0:
                        label='increasing $\lambda$'
                    else:
                        label='decreasing $\lambda$'
                    ax3.plot(attempt['wavelengths'],attempt['powers'],label=label)
                    
                    
                ax2.set_xlabel('Time, s')
                ax1.set_ylabel('Power, mW')
                ax2.set_ylabel('Wavelength, nm')
                ax3.legend()
                ax3.set_xlabel('Wavelength, nm')
                ax3.set_ylabel('Power, mW')
                fig1.tight_layout()
                self.single_spectrum_figure.tight_layout()
                
                    
                
  
                # plt.plot(wavelengths,powers,color='green')
                # plt.xlabel('Wavelength, nm')
                # plt.ylabel('Power, mW',color='green')
                
                
            elif self.single_spectrum_path.split('.')[-1]=='pkl':
                with open(self.single_spectrum_path,'rb') as f:
                    self.S_print.emit('loading data for analyzer from ' + self.single_spectrum_path)
                    Data=(pickle.load(f))
                self.single_spectrum_figure=plt.figure()
                plt.plot(Data[:,0],Data[:,1])
                plt.xlabel('Wavelength, nm')
                plt.ylabel('Spectral power density, dBm')
                plt.tight_layout()

            
        def plot_spectrogram(self):
            if self.SNAP is None:
                self.load_data()
            
            with open(self.plotting_parameters_file_path,'r') as f:
                p=json.load(f)
            try:
                if self.SNAP.type_of_signal!=self.type_of_spectrogram:
                    if self.SNAP.jones_matrixes_used:
                        self.SNAP.switch_signal_type(self.type_of_spectrogram)
                    else:
                        self.S_print_error.emit('Error. No complex data in SNAP object to derive {}. Only {} is available'.format(self.type_of_spectrogram, self.SNAP.type_of_signal))
                        return 
            except AttributeError as E:
                print(E)
            
            w_0=np.mean(self.SNAP.wavelengths)
            x=self.SNAP.positions[:,self.SNAP.axes_dict[self.SNAP.axis_key]]-p['shift_x_axis']
            if p['shift_x_axis']!=0:
                self.S_print_error.emit('!!! Note that X axis in spectrogram are shifted on {} um according to plotting_parameters.txt'.format(p['shift_x_axis']))
            
            def _convert_ax_Wavelength_to_Radius(ax_Wavelengths):
                """
                Update second axis according with first axis.
                """
                y1, y2 = ax_Wavelengths.get_ylim()
                print(y1,y2)
                nY1=(y1-self.SNAP.lambda_0)/self.SNAP.lambda_0*self.SNAP.R_0*self.SNAP.refractive_index*1e3
                nY2=(y2-self.SNAP.lambda_0)/self.SNAP.lambda_0*self.SNAP.R_0*self.SNAP.refractive_index*1e3
                ax_Radius.set_ylim(nY1, nY2)
                
            def _forward(x):
                return (x-self.SNAP.lambda_0)/self.SNAP.lambda_0*self.SNAP.R_0*self.SNAP.refractive_index*1e3
    
            def _backward(x):
                return self.SNAP.lambda_0 + self.SNAP.lambda_0*x/self.SNAP.R_0/self.SNAP.refractive_index/1e3
        
        
            
            if (p['new_figure']) or (p['figsize']!=None):
                fig=plt.figure(figsize=p['figsize'])
            else:
                fig=plt.gcf()
            
            plt.clf()
            matplotlib.rcParams.update({'font.size': p['font_size']})
            
            if not p['enable_offset']: plt.rcParams['axes.formatter.useoffset'] = False
            
            ax_Wavelengths = fig.subplots()
            if p['use_contourf']==True:
                levels=p['contourf_levels']
                im = ax_Wavelengths.contourf(x,self.SNAP.wavelengths,self.SNAP.signal,cmap=p['cmap'],levels=levels,vmin=p['vmin'],vmax=p['vmax'])
            else:
                im = ax_Wavelengths.pcolormesh(x,self.SNAP.wavelengths,self.SNAP.signal,cmap=p['cmap'],vmin=p['vmin'],vmax=p['vmax'])
                # im = ax_Wavelengths.imshow(x,self.SNAP.wavelengths,self.SNAP.signal,cmap=p['cmap'],vmin=p['vmin'],vmax=p['vmax'])
            if p['ERV_axis']:
                ax_Radius = ax_Wavelengths.secondary_yaxis('right', functions=(_forward,_backward))
                # ax_Wavelengths.callbacks.connect("ylim_changed", _convert_ax_Wavelength_to_Radius)
            '''
            legacy code
            '''
            if p['position_in_steps_axis']:
                ax_steps=ax_Wavelengths.twiny()
                ax_steps.set_xlim([np.min(x)/2.5,np.max(x)/2.5])
                try:
                    clb=fig.colorbar(im,ax=ax_steps,pad=p['colorbar_pad'],location=p['colorbar_location'])
                except TypeError:
                    self.S_print.emit('WARNING: update matplotlib up to 3.4.2 to plot colorbars properly')
                    clb=fig.colorbar(im,ax=ax_steps,pad=p['colorbar_pad'])
            else:
                try:
                    clb=fig.colorbar(im,ax=ax_Wavelengths,pad=p['colorbar_pad'],location=p['colorbar_location'])
                except TypeError as e:
                    self.S_print.emit('WARNING: update matplotlib up to 3.4.2 to plot colorbars properly. Error is ' + str(e))
                    clb=fig.colorbar(im,ax=ax_Wavelengths,pad=p['colorbar_pad'])
    
            if p['language'] in ['eng','en']:
                try:
                    if self.SNAP.axis_key=='W':
                        ax_Wavelengths.set_xlabel(r'Wavelength $\lambda$, nm')    
                    elif self.SNAP.axis_key=='p':
                        ax_Wavelengths.set_xlabel('Position, number')   
                    else:
                        ax_Wavelengths.set_xlabel(r'Position $z_0$, $\mu$m')
                    ax_Wavelengths.set_ylabel(r'Wavelength $\lambda$, nm')   
                    try:
                        ax_Radius.set_ylabel('$\Delta r_{eff}$, nm')
                    except: pass
                    if self.SNAP.signal_scale=='log':
                        if p['colorbar_title_position']=='right':
                            clb.ax.set_ylabel('dB',rotation= p['colorbar_title_rotation'],labelpad=5)
                        else:
                            clb.ax.set_title('dB')
                    if p['title']:
                        plt.title('experiment')
                    try:
                        ax_steps.set_xlabel('Position, steps')
                    except: pass 
                except Exception as E:
                    print(E)
                    
            
            elif p['language']=='ru':
                if self.SNAP.axis_key=='W':
                    ax_Wavelengths.set_xlabel('Длина волны, нм')    
                elif self.SNAP.axis_key=='p':
                    ax_Wavelengths.set_xlabel('Позиция, #')    
                else:
                    ax_Wavelengths.set_xlabel('Расстояние, мкм')
                ax_Wavelengths.set_ylabel('Длина волны, нм')
                try:
                    ax_Radius.set_ylabel('$\Delta r_{eff}$, нм')
                except: pass
                try:
                    if self.SNAP.signal_scale=='log':
                        if p['colorbar_title_position']=='right':
                            clb.ax.set_ylabel('дБ',rotation= p['colorbar_title_rotation'])
                        else:
                            clb.ax.set_title('дБ')
                    if p['title']:
                        plt.title('эксперимент')
                    try:
                        ax_steps.set_xlabel('Расстояние, шаги')
                    except: pass 
                except Exception as E:
                    print(E)
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
            if self.SNAP.signal is None:
                self.load_data()
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
            plt.plot(self.SNAP.wavelengths,self.SNAP.signal[:,index])
            
            if p['language'] in ['eng','en']:
                plt.xlabel('Wavelength, nm')
                plt.ylabel('Spectral power density, dBm')
            elif p['language']=='ru':
                plt.xlabel('Длина волны, нм')
                plt.ylabel('Спектральная плотность мощности, дБм')
            self.single_spectrum_figure=fig
            plt.tight_layout()
            return fig
        
        
            
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
                self.S_print_error.emit('Error. Signal is NAN only')
                return
            dw=(waves[-1]-waves[0])/len(waves)
            peakind2,_=find_peaks(abs(signal-np.nanmean(signal)),prominence=self.min_peak_level , distance=int(self.min_peak_distance/dw))
            if len(peakind2)>0:
                axes.plot(waves[peakind2], signal[peakind2], '.')
                
                main_peak_index=np.argmax(abs(signal[peakind2]-np.nanmean(signal)))
                # wavelength_main_peak=waves[peakind2][main_peak_index]
                peakind2=peakind2[np.argsort(-waves[peakind2])] ##sort in wavelength decreasing
                wavelength_main_peak=waves[peakind2[0]]
                
                
                try:
                    [non_res_transmission,Fano_phase,resonance_position,delta_c,delta_0,bandwidth_for_fitting,perrors]=SNAP_experiment.find_width(waves, signal, wavelength_main_peak,
                                                                                                                                      self.bandwidth_for_fitting,self.iterate_different_bandwidths,
                                                                                                                                      self.max_bandwidth_for_fitting,self.iterating_cost_function_type)
                    # parameters, waves_fitted,signal_fitted=SNAP_experiment.get_Fano_fit(waves,signal,wavelength_main_peak)
                    signal_fitted=SNAP_experiment.Fano_lorenzian(waves,non_res_transmission,Fano_phase,resonance_position,delta_0,delta_c)
                except Exception as e:
                        self.S_print_error.emit('Error: {}'.format(e))
                axes.plot(waves, signal_fitted, color='green')   
                lambda_to_nu=c/resonance_position**2*1e3 # MHz per nm
                lambda_to_omega=lambda_to_nu*2*np.pi
                depth=4*delta_0*delta_c/(delta_0+delta_c)**2
                linewidth=(delta_0+delta_c)*2/lambda_to_omega
                results_text1='$|S_0|$={:.2f} \n arg(S)={:.2f} $\pi$  \n $\lambda_0$={:.5f}  nm \n $\Delta \lambda={:.3f}$ pm \n Depth={:.3e} \n'.format(non_res_transmission,Fano_phase, resonance_position,linewidth*1e3,depth)
                delta_c_err=perrors[4]
                delta_0_err=perrors[3]
                
                Q_factor=resonance_position/linewidth
                results_text2='\n $\delta_c$=({:.2f} $\pm$ {:.2f}) '.format(delta_c,delta_c_err)+'$\mu s^{-1}$'
                results_text3='\n $\delta_0$=({:.2f} $\pm$ {:.2f}) '.format(delta_0,delta_0_err)+'$\mu s^{-1}$'
                results_text4='\n Q-factor={:.2e}'.format(Q_factor)
                results_text=results_text1+results_text2+results_text3+results_text4
                for t in axes.texts:
                    t.set_visible(False)
                axes.text(0.8, 0.5,results_text,
                         horizontalalignment='center',
                         verticalalignment='center',
                         transform = axes.transAxes)
            else:
                self.S_print_error.emit('Error: No peaks found')
            # plt.tight_layout()
            fig.canvas.draw_idle()


        def extract_ERV(self):
            positions, peak_wavelengths, ERV, resonance_parameters = self.SNAP.extract_ERV(self.number_of_peaks_to_search,
                                                                                           self.min_peak_level,
                                                                                        self.min_peak_distance,
                                                                                        self.min_wave,
                                                                                        self.max_wave,
                                                                                        self.lambda_0_for_ERV,
                                                                                        self.find_widths,
                                                                                        self.bandwidth_for_fitting,
                                                                                        self.iterate_different_bandwidths,
                                                                                        self.max_bandwidth_for_fitting,
                                                                                        self.iterating_cost_function_type)

            path, FileName = os.path.split(self.spectrogram_file_path)
            NewFileName=path+'\\'+FileName.split('.')[-2]+'_ERV.pkl'
            with open(NewFileName,'wb') as f:
                ERV_params={'R_0':self.SNAP.R_0, 'refractive_index':self.SNAP.refractive_index,
                            'positions':positions, 'peak_wavelengths':peak_wavelengths,
                            'ERVs':ERV, 'resonance_parameters':resonance_parameters,
                            'fitting_parameters':self.get_parameters()}
                pickle.dump(ERV_params, f)
            
            
            x = self.SNAP.positions[:, self.SNAP.axes_dict[self.SNAP.axis_key]]
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
            
        def get_modes_parameters(self):
            x = self.SNAP.positions[:, self.SNAP.axes_dict[self.SNAP.axis_key]]
               
            modes_parameters=self.SNAP.get_modes_parameters(self.min_peak_level,
                                           self.min_peak_distance,
                                           self.bandwidth_for_fitting,
                                           self.iterate_different_bandwidths,
                                           self.max_bandwidth_for_fitting,
                                           self.iterating_cost_function_type)

            
            fig1,axes1=plt.subplots(2,1,sharex=True)
            fig2,axes2=plt.subplots(2,1,sharex=True)
            if len(modes_parameters)>0:
                for D in modes_parameters:
                    if self.figure_spectrogram is not None:
                        self.figure_spectrogram.axes[0].plot(x,D['mode wavelength']*np.ones(len(x)),'--',color='black')
                        self.figure_spectrogram.axes[0].plot(x,D['res_wavelength'],color='gray',linewidth=3.0)
                    delta_c=D['delta_c']
                    delta_c_err=D['delta_c_error']
                    delta_0=D['delta_0']
                    delta_0_err=D['delta_0_error']
                    axes1[0].errorbar(x,delta_c,yerr=delta_c_err,label='{:.2f}'.format(D['mode wavelength']))
                    axes1[1].errorbar(x,delta_0,yerr=delta_0_err,label='{:.2f}'.format(D['mode wavelength']))
                    
                    mode_intensity=(delta_c)/(delta_0+delta_c)**2
                    threshold=(delta_0+delta_c)**3/delta_c
                    
                    axes2[0].plot(x,mode_intensity,label='{:.2f}'.format(D['mode wavelength']))
                    axes2[1].plot(x,threshold,label='{:.2f}'.format(D['mode wavelength']))
                    
                if self.figure_spectrogram is not None:
                    self.figure_spectrogram.canvas.draw()
                    
                axes1[0].set_ylim(bottom=0,top=np.nanmax(delta_c)*1.1)
                axes1[1].set_ylim(bottom=0,top=np.nanmax(delta_0)*1.1)

                
                axes2[0].set_yscale('log')
                axes2[1].set_yscale('log')
                
                axes1[1].set_xlabel(r'Position, $\mu$m')
                axes2[1].set_xlabel(r'Position, $\mu$m')
                
                axes1[0].set_ylabel('$\delta_c$, 1e6 1/s')
                axes1[1].set_ylabel('$\delta_0$, 1e6 1/s')
                axes2[0].set_ylabel(r'$\frac {\delta_c} {(\delta_c+\delta_0)^{2}}$')
                axes2[1].set_ylabel(r'$\frac{(\delta_0+\delta_c)^{3}}{\delta_c}$, 1e12 $1/s^2$')
                axes1[0].legend()
                
                fig1.tight_layout()
                fig2.tight_layout()
                
                path, FileName = os.path.split(self.spectrogram_file_path)
                NewFileName=path+'\\'+FileName.split('.')[-2]+'_mode_parameters.pkl'
                Data_to_save={}
                Data_to_save['modes_parameters']=modes_parameters
                Data_to_save['coordinates']=x
                with open(NewFileName,'wb') as f:
                    pickle.dump(Data_to_save, f)
                print('mode parameters saved to ', NewFileName)
            
            if self.derive_taper_cavity_params:
                max_allowed_error=0.2
                from Theory.estimate_cavity_and_taper_params import estimate_params
                from Theory.estimate_nonlinear_and_thermal_properties import get_min_threshold,Kerr_threshold
                a,w,C2,ReD,ImD,Gamma=estimate_params(NewFileName)
                print(C2,ReD,ImD,Gamma)
                min_threshold,position_for_min_threshold=get_min_threshold(self.SNAP.R_0,self.SNAP.wavelengths[0],a,w,C2,ImD,Gamma)
                self.S_print.emit('Min_threshold={} W'.format(min_threshold))
                self.figure_spectrogram.axes[0].axvline(position_for_min_threshold,color='blue')
                self.figure_spectrogram.axes[0].text(0.4,0.4,'{:.3f} W'.format(min_threshold), 
                                                     horizontalalignment='center',
                                                     verticalalignment='center',
                                                     transform = self.figure_spectrogram.axes[0].transAxes)
                self.figure_spectrogram.canvas.draw()
                plt.figure()
                for D in modes_parameters:
                    delta_c=D['delta_c']
                    delta_c_err=D['delta_c_error']
                    
                    delta_0=D['delta_0']
                    delta_0_err=D['delta_0_error']
                    
                    # ind_nan=np.argwhere(np.isnan(delta_c))
                    # ind_high_delta_c_errors=np.argwhere(delta_c_err/delta_c>max_allowed_error)
                    # ind_high_delta_0_errors=np.argwhere(delta_0_err/delta_0>max_allowed_error)
                    # ind_to_delete = np.unique(np.concatenate((ind_nan,ind_high_delta_c_errors,ind_high_delta_0_errors)))
    
                    #     # ind_to_delete=sorted(np.unique(ind_nan+ind_high_delta_c_errors+ind_high_delta_0_errors))
                    # x_cutted=np.delete(x,ind_to_delete)
                    # delta_c=np.delete(delta_c,ind_to_delete)
                    # delta_0=np.delete(delta_0,ind_to_delete)
                    
                    x_cutted=x

    
                    length=np.nansum(delta_c[1:]*np.diff(x_cutted))/np.nanmax(delta_c)
                    plt.plot(x_cutted,Kerr_threshold(D['res_wavelength'],delta_c*1e6,delta_0*1e6,length,self.SNAP.R_0),label='{:.2f}'.format(D['mode wavelength']))
                plt.xlabel('Distance, micron')
                plt.ylabel('Kerr threshold, W')
                plt.legend()
                plt.tight_layout()
                    
                    
                

                
        
        def plot_ERV_params(self,params_dict:dict,find_widths=True):
            positions=params_dict['positions']
            ERVs=params_dict['ERVs']
            peak_wavelengths=params_dict['peak_wavelengths']
            number_of_peaks_to_search=np.shape(peak_wavelengths)[1]
            resonance_parameters_array=params_dict['resonance_parameters']
            
            non_res_transmission=resonance_parameters_array[:,:,0]
            Fano_phase=resonance_parameters_array[:,:,1]
            delta_c=resonance_parameters_array[:,:,2]
            delta_0=resonance_parameters_array[:,:,3]
            
            non_res_transmission=non_res_transmission.reshape(len(positions),number_of_peaks_to_search)
            Fano_phase=Fano_phase.reshape(len(positions),number_of_peaks_to_search)
            delta_c=delta_c.reshape(len(positions),number_of_peaks_to_search)
            delta_0=delta_0.reshape(len(positions),number_of_peaks_to_search)
            
            lambda_to_nu=c/np.nanmean(peak_wavelengths)**2*1e3 # MHz per nm
            lambda_to_omega=lambda_to_nu*2*np.pi
            depth=4*delta_0*delta_c/(delta_0+delta_c)**2
            linewidth=(delta_0+delta_c)*2/lambda_to_omega
            
            plt.figure()
            for i in range(0,number_of_peaks_to_search):
                plt.plot(positions,peak_wavelengths[:,i])
            plt.xlabel('Distance, $\mu$m')
            plt.ylabel('Cut-off wavelength, nm')
            plt.title('Cut-off wavelength')
            plt.tight_layout()
            
            plt.figure()
            for i in range(0,number_of_peaks_to_search):
                plt.plot(positions,ERVs[:,i])
            plt.xlabel('Distance, $\mu$m')
            plt.ylabel('Effective radius variation, nm')
            plt.title('Effective radius variation')
            plt.tight_layout()
  

            if  find_widths:
                plt.figure()
                plt.title('Depth and Linewidth $\Delta \lambda$')
                for i in range(0,number_of_peaks_to_search):
                    plt.plot(positions,depth[:,i],color='blue')
                plt.xlabel('Distance, $\mu$m')
                plt.ylabel('Depth ',color='blue')
                plt.gca().tick_params(axis='y', colors='blue')
                plt.gca().twinx()
                # plt.figure()
                for i in range(0,number_of_peaks_to_search):
                    plt.plot(positions,linewidth[:,i], color='red')
                plt.ylabel('Linewidth $\Delta \lambda$, nm',color='red')
                plt.gca().tick_params(axis='y', colors='red')
                plt.tight_layout()
                
                plt.figure()
                plt.title('Nonresonanse transmission $|S_0|$ and its phase')
                for i in range(0,number_of_peaks_to_search):
                    plt.plot(positions,non_res_transmission[:,i],color='blue')
                plt.xlabel('Distance, $\mu$m')
                plt.ylabel('Nonresonance transmission $|S_0|$',color='blue')
                plt.gca().tick_params(axis='y', colors='blue')
                plt.gca().twinx()
                # plt.figure()
                for i in range(0,number_of_peaks_to_search):
                    plt.plot(positions,Fano_phase[:,i], color='red')
                plt.ylabel('Phase',color='red')
                plt.gca().tick_params(axis='y', colors='red')
                plt.tight_layout()
                
                plt.figure()
                plt.title('$\delta_0$ and $\delta_c$')
                for i in range(0,number_of_peaks_to_search):
                    plt.plot(positions,delta_c[:,i],color='blue')
                plt.xlabel('Distance, $\mu$m')
                plt.ylabel('$\delta_c$,  $10^6$ 1/s',color='blue')
                plt.gca().tick_params(axis='y', colors='blue')
                plt.gca().twinx()
                # plt.figure()
                for i in range(0,number_of_peaks_to_search):
                    plt.plot(positions,delta_0[:,i], color='red')
                plt.ylabel('$\delta_0$,  $10^6$ 1/s',color='red')
                plt.gca().tick_params(axis='y', colors='red')
                plt.tight_layout()
            
            self.S_print.emit(f'R_0 = {params_dict["R_0"]}, n = {params_dict["refractive_index"]}')
        
        
        def plot_ERV_from_file(self,file_name):
            with open(file_name,'rb') as f:
                d=pickle.load(f)
            self.plot_ERV_params(d)
            
            
        def apply_FFT_to_spectrogram(self):
            self.S_print.emit('Applying FFT filter...')
            self.SNAP.apply_FFT_filter(float(self.FFTFilter_low_freq_edge),float(self.FFTFilter_high_freq_edge))
            self.plot_spectrogram()
            self.S_print.emit('Filter applied. New spectrogram plotted')
            

            
        def run_quantum_numbers_fitter(self):
            self.S_print.emit('start finding quantum numbers...')
            axes=self.single_spectrum_figure.gca()
            line = axes.get_lines()[0]
            waves = line.get_xdata()
            signal = line.get_ydata()
            wave_min,wave_max=axes.get_xlim()
            index_min=np.argmin(abs(waves-wave_min))
            index_max=np.argmin(abs(waves-wave_max))
            waves=waves[index_min:index_max]
            signal=signal[index_min:index_max]
            if all(np.isnan(signal)):
                self.S_print_error.emit('Error. Signal is NAN only')
                return
            fitter=QuantumNumbersStructure.Fitter(waves, signal, self.min_peak_level, self.min_peak_distance,
                                                  wave_min=None, wave_max=None, p_guess_array=[self.quantum_numbers_fitter_p_max],
                                                  dispersion=self.quantum_numbers_fitter_dispersion,
                                                  polarization=self.quantum_numbers_fitter_polarizations,
                                                  type_of_optimizer=self.quantum_numbers_fitter_type_of_optimizer,
                                                  temperature= self.temperature,vary_temperature=self.quantum_numbers_fitter_vary_temperature)
            axes.plot(fitter.exp_resonances,fitter.signal[fitter.resonances_indexes],'.')
            self.single_spectrum_figure.canvas.draw()
            
            
            fitter.run(self.cost_function_figure, self.cost_function_ax)
            self.S_print.emit('quantum numbers found')
                    
            resonances, labels = fitter.th_resonances.create_unstructured_list(self.quantum_numbers_fitter_polarizations)
            
            
            print('N_exp=%d , N_th=%d,R=%f,p_max=%d, cost_function=%f' % (len(fitter.exp_resonances),fitter.th_resonances.N_of_resonances['Total'],fitter.R_best,fitter.p_best, fitter.cost_best))
            plt.figure()
            if fitter.vary_temperature:
                plt.pcolor(fitter.T_array,fitter.R_array,fitter.cost_function_array, norm=LogNorm())
                plt.title('cost function VS R and T')
                plt.colorbar()
            else:
                plt.plot(fitter.R_array,fitter.cost_function_array[:,0])
                plt.gca().set_yscale('log')
                plt.title('cost function VS R')
            
            '''
            Запись в файл для дальнейшего пользования
            '''
            path,FileName = os.path.split(self.single_spectrum_path)
            with open(path+'\\polarizations.pkl', 'wb') as f:
                pickle.dump(labels, f)
            with open(path+'\\found resonances.pkl', 'wb') as f:
                pickle.dump(resonances, f)

            
            '''
            Plotting to the single spectrum
            '''
            y_min,y_max=axes.get_ylim()
            for i,wave in enumerate(resonances):
                if labels[i].split(',')[0]=='TM':
                    color='blue'
                else:
                    color='red'
                axes.axvline(wave,0,0.9,color=color)
                y=y_min+(y_max-y_min)/fitter.th_resonances.pmax*float(labels[i].split(',')[2])
                axes.annotate(labels[i],(wave,y))
            axes.set_title('R_fitted={} nm, T_best={} cost_function={}'.format(fitter.R_best,fitter.T_best,fitter.cost_best))
            self.single_spectrum_figure.canvas.draw()
            

            
            
            
                
        
  

if __name__ == "__main__":
    
    # os.chdir('..')
    
    
    
    #%%
    
    
    os.chdir('..')

    a=Analyzer()

    a.plotting_parameters_file_path=os.getcwd()+'\\plotting_parameters.txt'
    # f=r"C:\!WorkFolder\!Experiments\!SNAP system\2022.12 playing with parameters\potential 6\central.SNAP"
    f=r"C:\Users\Илья\Desktop\линейная модификация_resaved_resaved_resaved_resaved.pkl3d"
    a.load_data(f)
    a.plot_slice(680)
    a.analyze_spectrum(a.single_spectrum_figure)
    a.plot_results_separately=True
    a.lambda_0_for_ERV=1553.34
    b=a.extract_ERV()
    
    # import json
    # f=open('Parameters.txt')
    # Dicts=json.load(f)
    # f.close()
    # analyzer.set_parameters(Dicts['Analyzer'])
    # a.find_widths=True
    # a.plot_results_separately=True
    # a.plot_spectrogram()
    # # a.extract_ERV()
    # a.iterate_different_bandwidths=False
    # a.bandwidth_for_fitting=200
    # a.get_modes_parameters()
    # analyzer.single_spectrum_path=os.getcwd()+'\\ProcessedData\\test.laserdata'
    # analyzer.plot_single_spectrum_from_file()
# 
    # 

