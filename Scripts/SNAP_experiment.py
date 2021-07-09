# -*- coding: utf-8 -*-
"""
Created on Fri Sep 25 16:30:03 2020

@author: Ilya Vatnik

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
from mpl_toolkits.mplot3d import Axes3D


class SNAP():
    def __init__(self,file=None,
                 x=None,
                 wavelengths=None,
                 transmission=None,
                 R_0=62.5):
        
        self.R_0=62.5
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
        global R_0
        A=np.loadtxt(file_name)
        x_ERV=A[:,0]*2.5
        Waves=A[:,1]
        lambda_0=np.nanmin(Waves)
        ERV=(Waves-lambda_0)/np.nanmean(Waves)*R_0*1e3
    
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

    def plot_spectrogram(self,new_figure=True,figsize=None,font_size=11,title=False,vmin=None,vmax=None,
                         cmap='jet',language='eng',enable_offset=True,
                         colorbar_location='right',colorbar_pad=0.12,colorbar_title_position='right',colorbar_title_rotation=0):
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
        ax_Radius = ax_Wavelengths.twinx()
        ax_Wavelengths.callbacks.connect("ylim_changed", _convert_ax_Wavelength_to_Radius)
        try:
            im = ax_Wavelengths.pcolorfast(self.x,self.wavelengths,self.transmission,50,cmap=cmap,vmin=vmin,vmax=vmax)
        except:
            im = ax_Wavelengths.contourf(self.x,self.wavelengths,self.transmission,50,cmap=cmap,vmin=vmin,vmax=vmax)
        
        clb=plt.colorbar(im,ax=ax_Radius,pad=colorbar_pad,location=colorbar_location)
        
        if self.transmission_scale=='log':
            if colorbar_title_position=='right':
                clb.ax.set_ylabel('dB',rotation= colorbar_title_rotation)
            else:
                clb.ax.set_title('dB')
        if language=='eng':
            ax_Wavelengths.set_xlabel(r'Position, $\mu$m')
            ax_Wavelengths.set_ylabel('Wavelength, nm')
            ax_Radius.set_ylabel('Variation, nm')
            if title:
                plt.title('experiment')
        elif language=='ru':
            ax_Wavelengths.set_xlabel('Расстояние, мкм')
            ax_Wavelengths.set_ylabel('Длина волны, нм')
            ax_Radius.set_ylabel('Вариация радиуса, нм')
            if title:
                plt.title('эксперимент')
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
    
    
    def plot_spectrum(self,x):
        fig=plt.figure()
        plt.clf()
        # matplotlib.rcParams.update({'font.size': font_size})
        index=np.argmin(abs(x-self.x))
        plt.plot(self.wavelengths,self.transmission[:,index])
        plt.xlabel('Wavelength,nm')
        plt.ylabel('Spectral power density, dBm')
        return fig
        
        
    
    def extract_ERV(self,MinimumPeakDepth,MinWavelength=0,MaxWavelength=1e4, indicate_ERV_on_spectrogram=False):
        global R_0
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
        ERV=(PeakWavelengthArray-lambda_0)/np.nanmean(PeakWavelengthArray)*self.R_0*1e3
        
        if self.fig_spectrogram is not None and indicate_ERV_on_spectrogram:
            self.fig_spectrogram.axes[0].pcolormesh(Positions,WavelengthArray,PeakWavelengthMatrix)
        elif self.fig_spectrogram is None and indicate_ERV_on_spectrogram:
            self.plot_spectrogram()
            self.fig_spectrogram.axes[0].pcolormesh(Positions,WavelengthArray,PeakWavelengthMatrix)
        elif not indicate_ERV_on_spectrogram:
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
        return np.array(Pos),np.array(PeakWavelengthArray),np.array(ERV),np.array(LineWidthArray)
        



def _difference_between_exp_and_num(x_exp,exp_data,x_num,num_data,lambdas):
    f = interpolate.interp2d(x_num, lambdas, num_data, kind='quintic')
#    print(np.shape(exp_data),np.shape(f(x_exp,lambdas)))
#    return signal.correlate(exp_data,np.reshape(f(x_exp,lambdas),-1))
    t=np.sum((exp_data-(f(x_exp,lambdas)))**2)    
    return t



def _difference_for_ERV_position(x_0_ERV,*details):
    ERV_f,ERV_params,x,wavelengths,lambda_0,taper_params,x_exp,signal_exp=details
    ERV_array=np.squeeze(ERV_f(x,x_0_ERV,ERV_params))
    SNAP=SNAP_model.SNAP(x,ERV_array,wavelengths,lambda_0)
    # print(ERV_array)
    SNAP.set_taper_params(*taper_params)
    x_num,lambdas,num_data=SNAP.derive_transmission()
    x_center_num=x_num[int(center_of_mass(num_data)[1])]
    x_center_exp=x_exp[int(center_of_mass(signal_exp)[1])]
    t=abs(x_center_exp-x_center_num)
    print('num={},exp={},difference in mass centers is {}'.format(x_center_num,x_center_exp,t))
    return t
        
        
    # return difference_between_exp_and_num(x_exp,signal_exp,x,num_data,lambdas)





def optimize_taper_params(x,ERV,wavelengths,lambda_0,init_taper_params,SNAP_exp,bounds=None,max_iter=5):
    def _difference_on_taper(taper_params,*details):
        (absS,phaseS,ReD,ImD_exc,C)=taper_params
        x,ERV,wavelengths,lambda_0,x_exp,signal_exp=details
        SNAP=SNAP_model.SNAP(x,ERV,wavelengths,lambda_0)
        SNAP.set_taper_params(absS,phaseS,ReD,ImD_exc,C)
        x,wavelengths,num_data=SNAP.derive_transmission()
        t=_difference_between_exp_and_num(x_exp,signal_exp,x,num_data,wavelengths)
        print('taper opt. delta_t is {}'.format(t))
        return t
    
    if SNAP_exp.transmission_scale=='log':
        SNAP_exp.convert_to_lin_transmission()
    x_exp,signal_exp=SNAP_exp.x,SNAP_exp.transmission
    options={}
    options['maxiter']=max_iter 
    [absS,phaseS,ReD,ImD_exc,C]=init_taper_params # use current taper parameters as initial guess
    res=sp_minimize(_difference_on_taper,[absS,phaseS,ReD,ImD_exc,C],args=(x,ERV,wavelengths,lambda_0,x_exp,signal_exp),bounds=bounds,options=options)
    taper_params=res.x
    return res, taper_params
   

def optimize_ERV_shape_by_modes(ERV_f,initial_ERV_params,x_0_ERV,x,lambda_0,
                       taper_params,SNAP_exp,bounds=None,max_iter=20):
    
    def _difference_for_ERV_shape(ERV_params,*details):
        ERV_f,x_0_ERV,x,wavelengths,lambda_0,taper_params,SNAP_exp=details
        exp_modes=SNAP_exp.find_modes()
        ERV_array=ERV_f(x,x_0_ERV,ERV_params)
        SNAP=SNAP_model.SNAP(x,ERV_array,wavelengths,lambda_0)
        SNAP.set_taper_params(*taper_params)
        x_num,wavelengths,num_data=SNAP.derive_transmission()
        num_modes=SNAP.find_modes()
        N_num=len(num_modes)
        N_exp=len(exp_modes)
        if N_num>N_exp:
            exp_modes=np.sort(np.append(exp_modes,lambda_0*np.ones((N_num-N_exp,1))))
        elif N_exp>N_num:
            num_modes=np.sort(np.append(num_modes,lambda_0*np.ones((N_exp-N_num,1))))
        t=np.sum(abs(num_modes-exp_modes))
        print('mode positions difference is {}'.format(t))
        return t

    if SNAP_exp.transmission_scale=='log':
        SNAP_exp.convert_to_lin_transmission()
    wavelengths=SNAP_exp.wavelengths
    options={}
    options['maxiter']=max_iter  
    [absS,phaseS,ReD,ImD_exc,C]=taper_params # use current taper parameters as initial guess
    res=sp_minimize(_difference_for_ERV_shape,initial_ERV_params,args=(ERV_f,x_0_ERV,x,wavelengths,lambda_0,taper_params,SNAP_exp),
                    bounds=bounds,options=options,method='Nelder-Mead')
    ERV_params=res.x
    return res, ERV_params


def optimize_ERV_shape_by_whole_transmission(ERV_f,initial_ERV_params,x_0_ERV,x,lambda_0,
                       taper_params,SNAP_exp,bounds=None,max_iter=20):
    
    def _difference_for_ERV_shape(ERV_params,*details):
        ERV_f,x_0_ERV,x,wavelengths,lambda_0,taper_params,SNAP_exp=details
        ERV_array=ERV_f(x,x_0_ERV,ERV_params)
        SNAP=SNAP_model.SNAP(x,ERV_array,wavelengths,lambda_0)
        SNAP.set_taper_params(*taper_params)
        x_num,wavelengths,num_data=SNAP.derive_transmission()
        t=_difference_between_exp_and_num(SNAP_exp.x,SNAP_exp.transmission,x_num,num_data,wavelengths)
        print('ERV opt, delta_t is {}'.format(t))
        return t
    

    if SNAP_exp.transmission_scale=='log':
        SNAP_exp.convert_to_lin_transmission()
    wavelengths=SNAP_exp.wavelengths
    options={}
    options['maxiter']=max_iter  
    [absS,phaseS,ReD,ImD_exc,C]=taper_params # use current taper parameters as initial guess
    res=sp_minimize(_difference_for_ERV_shape,initial_ERV_params,args=(ERV_f,x_0_ERV,x,wavelengths,lambda_0,taper_params,SNAP_exp),
                    bounds=bounds,options=options,method='Nelder-Mead')
    ERV_params=res.x
    return res, ERV_params

# def optimize_ERV_position(ERV_f,initial_x_0_ERV,x,ERV_params,
#                           wavelengths,lambda_0,taper_params,exp_data,
#                           bounds=None,max_iter=20):
#     x_exp,signal_exp=exp_data[0],exp_data[1]
#     options={}
#     options['maxiter']=max_iter  
#     [absS,phaseS,ReD,ImD_exc,C]=taper_params # use current taper parameters as initial guess
#     res=sp_minimize(_difference_for_ERV_position,initial_x_0_ERV,
#                     args=(ERV_f,ERV_params,x,wavelengths,lambda_0,taper_params,x_exp,signal_exp),
#                     bounds=bounds,options=options,method='Nelder-Mead')
#     x_0_ERV_res=res.x
#     return res, x_0_ERV_res



def ERV_gauss(x,x_0_ERV,ERV_params):
    sigma=ERV_params[0]
    A=ERV_params[1]
    K=ERV_params[2]
    x_0=x_0_ERV
    return np.array(list(map(lambda x:K+np.exp(-(x-x_0)**2/2/sigma**2)*A,x)))


