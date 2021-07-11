# -*- coding: utf-8 -*-
"""
Created on Fri Sep 25 16:30:03 2020

@author: Ilya Vatnik
matplotlib 3.4.2 is needed! 
v.2
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib

import pickle
import bottleneck as bn
from scipy import interpolate
from scipy.optimize import minimize as sp_minimize
import scipy.signal
from  scipy.ndimage import center_of_mass
# from mpl_toolkits.mplot3d import Axes3D


class SNAP():
    def __init__(self,file=None,
                 x=None,
                 wavelengths=None,
                 transmission=None,
                 R_0=62.5):
        
        self.R_0=R_0
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
        
        if file is not None:
            self.load_data(file)
            self.transmission_scale='log'
        
    def load_data(self,file_name):
              
        print('loading data for analyzer from ',file_name)
        f=open(file_name,'rb')
        D=(pickle.load(f))
        f.close()
        self.axis=D['axis']
        Positions=np.array(D['Positions'])
        wavelengths,exp_data=D['Wavelengths'],D['Signal']
        x=Positions[:,self.axes_number[self.axis]]*2.5
        
        self.x=x
        self.wavelengths=wavelengths
        self.transmission=exp_data
        
        self.lambda_0=np.min(wavelengths)
        self.positions=Positions
        return x,wavelengths,exp_data
    
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
            nY1=(y1-self.lambda_0)/w_0*self.R_0*self.refractive_index*1e3
            nY2=(y2-self.lambda_0)/w_0*self.R_0*self.refractive_index*1e3
            ax_Radius.set_ylim(nY1, nY2)
    
        
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
            ax_Radius = ax_Wavelengths.twinx()
            ax_Wavelengths.callbacks.connect("ylim_changed", _convert_ax_Wavelength_to_Radius)
        
        if position_in_steps_axis:
            ax_steps=ax_Wavelengths.twiny()
            ax_steps.set_xlim([np.min(self.x)/2.5,np.max(self.x)/2.5])

            
            clb=fig.colorbar(im,ax=ax_steps,pad=colorbar_pad,location=colorbar_location)
        else:
            clb=fig.colorbar(im,ax=ax_Radius,pad=colorbar_pad,location=colorbar_location)
            
        

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
    
    
    def plot_sample_shape(self):
        fig=plt.figure()
        ax = plt.axes(projection='3d')
        ax.plot(self.positions[:,2],self.positions[:,0],self.positions[:,1])
        ax.set_xlabel('Z,steps')
        ax.set_ylabel('X,steps')
        ax.set_zlabel('Y,steps')
        plt.gca().invert_zaxis()
        plt.gca().invert_xaxis()
        return fig
    
    
    def plot_spectrum(self,x,language='eng'):
        fig=plt.figure()
        plt.clf()
        # matplotlib.rcParams.update({'font.size': font_size})
        index=np.argmin(abs(x-self.x))
        plt.plot(self.wavelengths,self.transmission[:,index])
        if language=='eng':
            plt.xlabel('Wavelength, nm')
            plt.ylabel('Spectral power density, dBm')
        elif language=='ru':
            plt.xlabel('Длина волны, нм')
            plt.ylabel('Спектральная плотность мощности, дБм')
        return fig
        
        
    
    def extract_ERV(self,MinimumPeakDepth,MinWavelength=0,MaxWavelength=1e4, indicate_ERV_on_spectrogram=False):
        NumberOfWavelength,Number_of_positions = self.transmission.shape
        LineWidthArray=np.zeros(Number_of_positions)
        PeakWavelengthArray=np.zeros(Number_of_positions)
        PeakWavelengthMatrix=np.zeros(np.shape(self.transmission))
        PeakWavelengthMatrix[:]=np.nan
        WavelengthArray=self.wavelengths
        Positions=self.x
        
        PeakWavelengthArray=[]
        LineWidthArray=[]
        Pos=[]
        for Zind, Z in enumerate(range(0,Number_of_positions)):
            peakind,_=scipy.signal.find_peaks(abs(self.transmission[:,Zind]-np.nanmean(self.transmission[:,Zind])),height=MinimumPeakDepth)
            NewPeakind=np.extract((WavelengthArray[peakind]>MinWavelength) & (WavelengthArray[peakind]<MaxWavelength),peakind)
            NewPeakind=NewPeakind[np.argsort(-WavelengthArray[NewPeakind])] ##sort in wavelength decreasing
            
            if len(NewPeakind)>0:
                PeakWavelengthArray.append(WavelengthArray[NewPeakind[0]])
                PeakWavelengthMatrix[NewPeakind[0],Zind]=-self.transmission[NewPeakind[0],Zind]
                Pos.append(Positions[Zind])
                LineWidthArray.append(0)
                
        lambda_0=np.nanmin(WavelengthArray)
        ERV=(PeakWavelengthArray-lambda_0)/np.nanmean(PeakWavelengthArray)*self.R_0*self.refractive_index
        
        if self.fig_spectrogram is not None and indicate_ERV_on_spectrogram:
            self.fig_spectrogram.axes[0].pcolormesh(Positions,WavelengthArray,PeakWavelengthMatrix,shading='auto')
            self.fig_spectrogram.canvas.draw()
        elif self.fig_spectrogram is None and indicate_ERV_on_spectrogram:
            self.plot_spectrogram()
            self.fig_spectrogram.axes[0].pcolormesh(Positions,WavelengthArray,PeakWavelengthMatrix,shading='auto')
        
        plt.figure()
        plt.plot(Pos,PeakWavelengthArray)
        plt.xlabel('Distance, $\mu$m')
        plt.ylabel('Cutt-off wavelength, nm')
        plt.tight_layout()
        return np.array(Pos),np.array(PeakWavelengthArray),np.array(ERV),np.array(LineWidthArray)
        



