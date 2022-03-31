# -*- coding: utf-8 -*-
"""
Created on Fri Sep 25 16:30:03 2020

@author: Ilya Vatnik
matplotlib 3.4.2 is needed! 

"""
__version__='5'
__date__='2022.04.01'

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

lambda_to_nu=125e3 #MHz/nm

class SNAP():
    def __init__(self,
                 positions=None,
                 wavelengths=None,
                 transmission=None,
                 R_0=62.5):
        
        self.R_0=R_0 # in microns!
        self.refractive_index=1.45
        self.wavelengths=wavelengths
        self.transmission=transmission
        self.positions=None # whole three dimensions, in microns!
        self.axes_dict={'X':0,'Y':1,'Z':2,'W':3,'p':4}
        self.transmission_scale='log'
        self.axis_key='Z'
        
        self.mode_wavelengths=None
        
        if transmission is not None:
            self.lambda_0=np.min(wavelengths)
        else:
            self.lambda_0=None
            
        self.fig_spectrogram=None
        self.date='_'

        

    
    def remove_nans(self):
        indexes_of_nan=list()
    
    def convert_to_lin_transmission(self):
        self.transmission_scale='lin'
        self.transmission=10**((self.transmission-np.max(self.transmission))/10)
    
    def load_ERV_estimation(self,file_name):
        A=np.loadtxt(file_name)
        x_ERV=A[:,0]
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
        x=self.positions[:,self.axes_dict[self.axis_key]]
        if self.mode_wavelengths is None:
            self.find_modes()
        ind=np.where(self.wavelengths==np.max(self.mode_wavelengths))[0][0]
        t_f=np.sum(self.transmission[ind-2:ind+2,:],axis=0)
        return (np.sum(t_f*x)/np.sum(t_f))
    
    
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
    

      

    
    


    # @numba.njit
    def extract_ERV(self,number_of_peaks_to_search=1,min_peak_level=1,min_peak_distance=10000,min_wave=0,max_wave=1e4,find_widths=True,
                    N_points_for_fitting=100,iterate_different_N_points=False,max_N_points_for_fitting=100):
        '''
        analyze 2D spectrogram
        return position of several first (higher-wavelegth) main resonances. Number of resonances is defined by number_of_peaks_to_search
        return corresponding ERV in nm, and resonance parameters:
            nonresonance transmission, Fano phase shift, depth/width, linewidth
        for each slice along position axis
        
        uses scipy.find_peak
        
        N_points_for_fitting - part of spectrum to be used for fitting. if 0, whole spectrum is used
        iterate_different_N_points - whether to check different N_points_for_fitting in each fitting process
        '''
        
               
        
        NumberOfWavelength,Number_of_positions = self.transmission.shape
        WavelengthArray=self.wavelengths
        x=self.positions[:,self.axes_dict[self.axis_key]]
        number_of_spectral_points=len(WavelengthArray)
        
        PeakWavelengthArray=np.empty((Number_of_positions,number_of_peaks_to_search))
        resonance_parameters_array=np.empty((Number_of_positions,number_of_peaks_to_search,7))
        PeakWavelengthArray.fill(np.nan)
        resonance_parameters_array.fill(np.nan)

            
        for Zind, Z in enumerate(range(0,Number_of_positions)):
            peakind,_=scipy.signal.find_peaks(abs(self.transmission[:,Zind]-np.nanmean(self.transmission[:,Zind])),height=min_peak_level,distance=min_peak_distance)
            NewPeakind=np.extract((WavelengthArray[peakind]>min_wave) & (WavelengthArray[peakind]<max_wave),peakind)
            NewPeakind=NewPeakind[np.argsort(-WavelengthArray[NewPeakind])] ##sort in wavelength decreasing
            if len(NewPeakind)>0:
                if len(NewPeakind)>=number_of_peaks_to_search:
                    shortWavArray=WavelengthArray[NewPeakind[:number_of_peaks_to_search]]
                elif len(NewPeakind)<number_of_peaks_to_search:
                    print(number_of_peaks_to_search-len(NewPeakind))
                    shortWavArray=np.concatenate(WavelengthArray[NewPeakind],np.nan*np.zeros(number_of_peaks_to_search-len(NewPeakind)))
                PeakWavelengthArray[Zind]=shortWavArray
                if find_widths:
                    for ii,peak_wavelength in enumerate(shortWavArray):
                        if peak_wavelength is not np.nan:
                            index=NewPeakind[ii]
                            # try:
                            if not iterate_different_N_points:
                                if N_points_for_fitting==0:
                                    fitting_parameters,_,_=get_Fano_fit(WavelengthArray, self.transmission[:,Zind],peak_wavelength)
                                else:
                                     i_min=0 if index-N_points_for_fitting<0 else index-N_points_for_fitting
                                     i_max=number_of_spectral_points-1 if index+N_points_for_fitting>number_of_spectral_points-1 else index+N_points_for_fitting
                                     fitting_parameters,_,_=get_Fano_fit(WavelengthArray[i_min:i_max], self.transmission[i_min:i_max,Zind],peak_wavelength)
                            else:
                                N_points_for_fitting=10
                                minimal_linewidth=max(WavelengthArray)-min(WavelengthArray)
                                for N_points in np.arange(10,max_N_points_for_fitting,2):
                                     i_min=0 if index-N_points<0 else index-N_points
                                     i_max=number_of_spectral_points-1 if index+N_points>number_of_spectral_points-1 else index+N_points
                                     fitting_parameters,_,_=get_Fano_fit(WavelengthArray[i_min:i_max], self.transmission[i_min:i_max,Zind],peak_wavelength)
                                     if (N_points%10==0): print('Z={},i_peak={},N_points={},linewidth={}'.format(Z,ii,N_points,fitting_parameters[3]))
                                     if minimal_linewidth>fitting_parameters[3]:
                                         minimal_linewidth=fitting_parameters[3]
                                         N_points_for_fitting=N_points
                                         
                                i_min=0 if index-N_points_for_fitting<0 else index-N_points_for_fitting
                                i_max=number_of_spectral_points-1 if index+N_points_for_fitting>number_of_spectral_points-1 else index+N_points_for_fitting
                                fitting_parameters,_,_=get_Fano_fit(WavelengthArray[i_min:i_max], self.transmission[i_min:i_max,Zind],peak_wavelength)
                            [non_res_transmission, Fano_phase, resonance_position,linewidth,depth]=fitting_parameters
                            delta_coupling=depth/2*lambda_to_nu #MHz/nm
                            delta_0=(linewidth/2-depth/2)*lambda_to_nu #MHz/nm
                            resonance_parameters_array[Zind,ii]=([non_res_transmission,Fano_phase,
                                                                  depth,linewidth,delta_coupling,delta_0,N_points_for_fitting])
                            # except:
                            #     print('error while fitting')
        lambdas_0=np.amin(PeakWavelengthArray,axis=0)
        ERV=(PeakWavelengthArray-lambdas_0)/np.nanmean(PeakWavelengthArray,axis=0)*self.R_0*self.refractive_index*1e3 # in nm
        print('Analyzing finished')

                # self.fig_spectrogram_ERV_lines.append[line]

        
        resonance_parameters_array=np.array(resonance_parameters_array)

   
        
        return x,np.array(PeakWavelengthArray),np.array(ERV),resonance_parameters_array
    
           

        
def get_Fano_fit(waves,signal,peak_wavelength=None):
    '''
    fit shape, given in log scale, with Lorenzian 10*np.log10(abs(transmission*np.exp(1j*phase) - 1j*depth/(w-w0+1j*width/2))**2)  # Gorodetsky, (9.19), p.253
    
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

