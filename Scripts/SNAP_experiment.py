# -*- coding: utf-8 -*-
"""
Created on Fri Sep 25 16:30:03 2020

@author: Ilya Vatnik
matplotlib 3.4.2 is needed! 

"""
__version__='2.2'
__data__='2022.01.20'

import numpy as np
import matplotlib.pyplot as plt
import matplotlib

import pickle
import bottleneck as bn
from scipy import interpolate
import scipy.signal
from  scipy.ndimage import center_of_mass
from scipy.fftpack import rfft, irfft, fftfreq
import scipy.optimize
# from mpl_toolkits.mplot3d import Axes3D


class SNAP():
    def __init__(self,
                 x=None,
                 wavelengths=None,
                 transmission=None,
                 R_0=62.5):
        
        self.R_0=R_0 # in microns!
        self.refractive_index=1.45
        self.x=x  # in microns! 
        self.wavelengths=wavelengths
        self.transmission=transmission
        self.positions=None # whole three dimensions, in steps!
        self.axes_number={'X':0,'Y':1,'Z':2,'W':3,'p':4}
        self.transmission_scale='log'
        self.axis=0
        
        self.mode_wavelengths=None
        
        if transmission is not None:
            self.lambda_0=np.min(wavelengths)
        else:
            self.lambda_0=None
            
        self.fig_spectrogram=None

        

    
    def remove_nans(self):
        indexes_of_nan=list()
    
    def convert_to_lin_transmission(self):
        self.transmission_scale='lin'
        self.transmission=10**((self.transmission-np.max(self.transmission))/10)
    
    def load_ERV_estimation(self,file_name):
        A=np.loadtxt(file_name)
        x_ERV=A[:,0]*2.5
        Waves=A[:,1]
        lambda_0=np.nanmin(Waves)
        ERV=(Waves-lambda_0)/np.nanmean(Waves)*self.R_0*1e3
    
        if (max(np.diff(x_ERV))-min(np.diff(x_ERV)))>0:
            f = interpolate.interp1d(x_ERV, ERV)
            x_ERV=np.linspace(min(x_ERV),max(x_ERV),len(x_ERV))
            ERV=f(x_ERV)
        return x_ERV,ERV,lambda_0

    def find_modes(self,prominence_factor=2):
        T_shrinked=np.nanmean(abs(self.transmission-np.nanmean(self.transmission,axis=0)),axis=1)
        mode_indexes,_=scipy.signal.find_peaks(T_shrinked,prominence=prominence_factor*bn.nanstd(T_shrinked))
        mode_wavelengths=np.sort(self.wavelengths[mode_indexes])
        mode_wavelengths=np.array([x for x in mode_wavelengths if x>self.lambda_0])
        self.mode_wavelengths=mode_wavelengths
        return mode_wavelengths
    
    
    
    def find_center(self):
        if self.mode_wavelengths is None:
            self.find_modes()
        ind=np.where(self.wavelengths==np.max(self.mode_wavelengths))[0][0]
        t_f=np.sum(self.transmission[ind-2:ind+2,:],axis=0)
        return (np.sum(t_f*self.x)/np.sum(t_f))
    
    
    def apply_FFT_filter(self,LowFreqEdge=0.00001,HighFreqEdge=0.001):
        def FFTFilter(y_array):
            W=fftfreq(y_array.size)
            f_array = rfft(y_array)
            Indexes=[i for  i,w  in enumerate(W) if all([abs(w)>LowFreqEdge,abs(w)<HighFreqEdge])]
            f_array[Indexes] = 0
#            f_array[] = 0
            return irfft(f_array)
        for ii,spectrum in enumerate(np.transpose(self.transmission)):
            self.transmission[:,ii]=FFTFilter(spectrum)
    

    def plot_spectrogram(self,new_figure=True,figsize=(8,4),font_size=11,title=False,vmin=None,vmax=None,
                         cmap='jet',language='eng',enable_offset=True, 
                         position_in_steps_axis=True,ERV_axis=True,
                         colorbar_location='right',colorbar_pad=0.12,
                         colorbar_title_position='right',colorbar_title_rotation=0):
        '''
        Parameters:
        font_size=11,title=True,vmin=None,vmax=None,cmap='jet',language='eng'
        '''
        w_0=np.mean(self.wavelengths)
        def _convert_ax_Wavelength_to_Radius(ax_Wavelengths):
            """
            Update second axis according with first axis.
            """
            y1, y2 = ax_Wavelengths.get_ylim()
            print(y1,y2)
            nY1=(y1-self.lambda_0)/w_0*self.R_0*self.refractive_index*1e3
            nY2=(y2-self.lambda_0)/w_0*self.R_0*self.refractive_index*1e3
            ax_Radius.set_ylim(nY1, nY2)
            
        def _forward(x):
            return (x-self.lambda_0)/w_0*self.R_0*self.refractive_index*1e3

        def _backward(x):
            return self.lambda_0 + w_0*x/self.R_0/self.refractive_index/1e3
    
    
        
        if (new_figure) or (figsize!=None):
            fig=plt.figure(figsize=figsize)
        else:
            fig=plt.gcf()
        
        plt.clf()
        matplotlib.rcParams.update({'font.size': font_size})
        
        if not enable_offset: plt.rcParams['axes.formatter.useoffset'] = False
        
        ax_Wavelengths = fig.subplots()
        try:
            im = ax_Wavelengths.pcolorfast(self.x,self.wavelengths,self.transmission,50,cmap=cmap,vmin=vmin,vmax=vmax)
        except:
            im = ax_Wavelengths.contourf(self.x,self.wavelengths,self.transmission,50,cmap=cmap,vmin=vmin,vmax=vmax)
        if ERV_axis:
            ax_Radius = ax_Wavelengths.secondary_yaxis('right', functions=(_forward,_backward))
            # ax_Wavelengths.callbacks.connect("ylim_changed", _convert_ax_Wavelength_to_Radius)
        
        if position_in_steps_axis:
            ax_steps=ax_Wavelengths.twiny()
            ax_steps.set_xlim([np.min(self.x)/2.5,np.max(self.x)/2.5])
            try:
                clb=fig.colorbar(im,ax=ax_steps,pad=colorbar_pad,location=colorbar_location)
            except TypeError:
                print('WARNING: update matplotlib up to 3.4.2 to plot colorbars properly')
                clb=fig.colorbar(im,ax=ax_steps,pad=colorbar_pad)
        else:
            try:
                clb=fig.colorbar(im,ax=ax_Wavelengths,pad=colorbar_pad,location=colorbar_location)
            except TypeError:
                print('WARNING: update matplotlib up to 3.4.2 to plot colorbars properly')
                clb=fig.colorbar(im,ax=ax_Wavelengths,pad=colorbar_pad)

        if language=='eng':
            ax_Wavelengths.set_xlabel(r'Position, $\mu$m')
            ax_Wavelengths.set_ylabel('Wavelength, nm')
            try:
                ax_Radius.set_ylabel('$\Delta r_{eff}$, nm')
            except: pass
            if self.transmission_scale=='log':
                if colorbar_title_position=='right':
                    clb.ax.set_ylabel('dB',rotation= colorbar_title_rotation,labelpad=5)
                else:
                    clb.ax.set_title('dB',labelpad=5)
            if title:
                plt.title('experiment')
            try:
                ax_steps.set_xlabel('Position, steps')
            except: pass 
        
        elif language=='ru':
            ax_Wavelengths.set_xlabel('Расстояние, мкм')
            ax_Wavelengths.set_ylabel('Длина волны, нм')
            try:
                ax_Radius.set_ylabel('$\Delta r_{eff}$, нм')
            except: pass
            if self.transmission_scale=='log':
                if colorbar_title_position=='right':
                    clb.ax.set_ylabel('дБ',rotation= colorbar_title_rotation)
                else:
                    clb.ax.set_title('дБ')
            if title:
                plt.title('эксперимент')
            try:
                ax_steps.set_xlabel('Расстояние, шаги')
            except: pass 
        plt.tight_layout()
        self.fig_spectrogram=fig
        return fig,im,ax_Wavelengths,ax_Radius
    
    

    
    

    
    def plot_spectrum(self,x,language='eng'):
        fig=plt.figure()
        plt.clf()

        ax = plt.axes()
        ax.minorticks_on()
        ax.grid(which='major', linestyle=':', linewidth='0.1', color='black')
        ax.grid(which='minor', linestyle=':', linewidth='0.1', color='black')

        index=np.argmin(abs(x-self.x))
        plt.plot(self.wavelengths,self.transmission[:,index])
        
        if language=='eng':
            plt.xlabel('Wavelength, nm')
            plt.ylabel('Spectral power density, dBm')
        elif language=='ru':
            plt.xlabel('Длина волны, нм')
            plt.ylabel('Спектральная плотность мощности, дБм')
        return fig
    

    # @numba.njit
    def extract_ERV(self,number_of_peaks_to_search=1,min_peak_level=1,min_peak_distance=10000,min_wave=0,max_wave=1e4,find_widths=True, indicate_ERV_on_spectrogram=True, plot_results_separately=False):
        '''
        analyze 2D spectrogram
        return position of seeral first (higher-wavelegth) main resonances. Number of resonances is defined by number_of_peaks_to_search
        return corresponding ERV in nm, and resonance parameters:
            nonresonance transmission, Fano phase shift, depth/width, linewidth
        for each slice along position axis
        
        uses scipy.find_peak
        '''
        NumberOfWavelength,Number_of_positions = self.transmission.shape
        WavelengthArray=self.wavelengths
        Positions=self.x
        
        PeakWavelengthArray=np.empty((Number_of_positions,number_of_peaks_to_search))
        resonance_parameters_array=np.empty((Number_of_positions,number_of_peaks_to_search,4))
        PeakWavelengthArray.fill(np.nan)
        resonance_parameters_array.fill(np.nan)

        for Zind, Z in enumerate(range(0,Number_of_positions)):
            peakind,_=scipy.signal.find_peaks(abs(self.transmission[:,Zind]-np.nanmean(self.transmission[:,Zind])),height=min_peak_level,distance=min_peak_distance)
            NewPeakind=np.extract((WavelengthArray[peakind]>min_wave) & (WavelengthArray[peakind]<max_wave),peakind)
            NewPeakind=NewPeakind[np.argsort(-WavelengthArray[NewPeakind])] ##sort in wavelength decreasing
            N_points_for_fitting=50
            if len(NewPeakind)>0:
                if len(NewPeakind)>=number_of_peaks_to_search:
                    shortWavArray=WavelengthArray[NewPeakind[:number_of_peaks_to_search]]
                elif len(NewPeakind)<number_of_peaks_to_search:
                    shortWavArray=np.concatenate(WavelengthArray[NewPeakind],np.nan*np.zeros(number_of_peaks_to_search-len(NewPeakind)))
                PeakWavelengthArray[Zind]=shortWavArray
                if find_widths:
                    for ii,peak_wavelength in enumerate(shortWavArray):
                        if peak_wavelength is not np.nan:
                            index=NewPeakind[ii]
                            try:
                                fitting_parameters,_,_=get_Fano_fit(WavelengthArray[index-N_points_for_fitting:index+N_points_for_fitting], self.transmission[index-N_points_for_fitting:index+N_points_for_fitting,Zind],peak_wavelength)
                                resonance_parameters_array[Zind,ii]=([fitting_parameters[0],fitting_parameters[1],
                                                                      fitting_parameters[4]/fitting_parameters[3],fitting_parameters[3]])
                            except:
                                print('error while fitting')
        lambdas_0=np.amin(PeakWavelengthArray,axis=0)
        ERV=(PeakWavelengthArray-lambdas_0)/np.nanmean(PeakWavelengthArray,axis=0)*self.R_0*self.refractive_index*1e3 # in nm
        print('Analyze finished')
        if self.fig_spectrogram is not None and indicate_ERV_on_spectrogram:
            if len(self.fig_spectrogram.axes[0].lines)>1:
                for line in self.fig_spectrogram.axes[0].lines[1:]: line.remove()
            for i in range(0,number_of_peaks_to_search):
                self.fig_spectrogram.axes[0].plot(self.x,PeakWavelengthArray[:,i])
            self.fig_spectrogram.canvas.draw()
        elif self.fig_spectrogram is None and indicate_ERV_on_spectrogram:
            self.plot_spectrogram()
            for i in range(0,number_of_peaks_to_search):
                self.fig_spectrogram.axes[0].plot(self.x,PeakWavelengthArray[:,i])
                line=self.fig_spectrogram.axes[0].plot(self.x,PeakWavelengthArray[:,i])
                self.fig_spectrogram_ERV_lines.append[line]

        
        resonance_parameters_array=np.array(resonance_parameters_array)

        
        if plot_results_separately:
            plt.figure()
            for i in range(0,number_of_peaks_to_search):
                plt.plot(self.x,PeakWavelengthArray[:,i])
            plt.xlabel('Distance, $\mu$m')
            plt.ylabel('Cut-off wavelength, nm')
            plt.title('Cut-off wavelength')
            plt.tight_layout()

        if plot_results_separately and find_widths:    
            plt.figure()
            for i in range(0,number_of_peaks_to_search):
                plt.plot(self.x,resonance_parameters_array[:,i,2])
            plt.xlabel('Distance, $\mu$m')
            plt.ylabel('Depth',color='blue')
            plt.gca().tick_params(axis='y', colors='blue')
            plt.title('Depth of the resonance')
            
            plt.figure()
            for i in range(0,number_of_peaks_to_search):
                plt.plot(self.x,resonance_parameters_array[:,i,3], color='red')
            plt.xlabel('Distance, $\mu$m')
            plt.ylabel('Linewidth $\Delta \lambda$, nm',color='red')
            plt.title('Linewidth $\Delta \lambda$')
            plt.tight_layout()
            
            plt.figure()
            plt.title('Nonresonanse transmission $|S_0|$')
            for i in range(0,number_of_peaks_to_search):
                plt.plot(self.x,resonance_parameters_array[:,i,0])
            plt.xlabel('Distance, $\mu$m')
            plt.ylabel('Nonresonance transmission $|S_0|$')
            plt.tight_layout()
        
        
        return self.x,np.array(PeakWavelengthArray),np.array(ERV),resonance_parameters_array
    
def load_data(file_name):
              
        print('loading data for analyzer from ',file_name)
        f=open(file_name,'rb')
        D=(pickle.load(f))
        f.close()
        SNAP_object=SNAP()
        SNAP_object.axis=D['axis']
        Positions=np.array(D['Positions'])
        wavelengths,exp_data=D['Wavelengths'],D['Signal']
        x=Positions[:,SNAP_object.axes_number[SNAP_object.axis]]*2.5
        
        SNAP_object.x=x
        SNAP_object.wavelengths=wavelengths
        SNAP_object.transmission=exp_data
        
        SNAP_object.lambda_0=np.min(wavelengths)
        SNAP_object.positions=Positions
        return SNAP_object
        
def get_Fano_fit(waves,signal,peak_wavelength=None):
    '''
    fit shape, given in log scale, with Lorenzian 10*np.log10(abs(transmission*np.exp(1j*phase) - 1j*depth/(w-w0+1j*width/2))**2) 
    
    meay use peak_wavelength
    return [transmission, Fano_phase, resonance_position,linewidth,depth], [x_fitted,y_fitted]
    

    '''
    signal_lin=10**(signal/10)
    transmission=np.mean(signal_lin)
    if peak_wavelength is None:
        peak_wavelength=waves[scipy.signal.find_peaks(signal_lin-transmission)[0][0]]
        peak_wavelength_lower_bound=0
        peak_wavelength_higher_bound=np.inf
    else:
        peak_wavelength_lower_bound=peak_wavelength-1e-3
        peak_wavelength_higher_bound=peak_wavelength+1e-3
    
    width=(waves[-1]-waves[0])/5
    phase=0
    depth=0.001
    initial_guess=[transmission,phase,peak_wavelength,width,depth]
    bounds=((0,0,peak_wavelength_lower_bound,0,0),(1,2,peak_wavelength_higher_bound,np.inf,np.inf))
    
    try:
        popt, pcov=scipy.optimize.curve_fit(Fano_lorenzian,waves,signal,p0=initial_guess,bounds=bounds)
        return popt, waves, Fano_lorenzian(waves,*popt)
    except RuntimeError as E:
        print(E)
        return initial_guess,waves,Fano_lorenzian(waves,*initial_guess)
    
       
def Fano_lorenzian(w,transmission,phase,w0,width,depth):
    '''
    return log of Fano shape
    '''
    return 10*np.log10(abs(transmission*np.exp(1j*phase*np.pi) - 1j*depth/(w-w0+1j*width/2))**2) 

if __name__ == "__main__":
    '''
    testing and debug
    '''
    # plt.figure(2)
    # waves=np.linspace(1550.64-0.05,1550.64+0.05,400)
    # for phase in np.linspace(-np.pi,np.pi,5):
    #     plt.plot(waves,Fano_lorenzian(waves, 0.5, 1550.64, 0.01, 0.001, phase),label=str(phase))
    # plt.legend()
    #%%
    import os
    import time
    
    os.chdir('..')
    
    SNAP=SNAP('Processed_spectrogram.pkl')
    #%%
    SNAP.plot_spectrogram(position_in_steps_axis=False,language='ru')
    
    #%%
    time1=time.time()
    # SNAP.extract_ERV(min_peak_level=0.7,min_peak_distance=100,number_of_peaks_to_search=3,plot_results_separately=True,find_widths=False)
    time2=time.time()
    SNAP.apply_FFT_filter()
    SNAP.plot_spectrogram(position_in_steps_axis=False,language='ru')
    print(time2-time1)

