# -*- coding: utf-8 -*-
"""
Created on Sun Dec 18 01:39:35 2022


@author: t-vatniki

following paper of Kolesnikova 
"""

__version__='2.1'
__date__='2023.03.14'

import numpy as np
import pickle
import matplotlib.pyplot as plt
from  scipy.optimize import curve_fit

delete_unreliable_data=True
use_ReD_joint_approximation=False

max_allowed_error=0.3 #  omit data with higher relative error
file=r"F:\!Projects\!SNAP system\Q -factors, Dependence on taper waist, etc\2022.12 from crown - good potential for losses evaluation\Processed_spectrogram good potential_resaved_q=0_mode_parameters.pkl"

c=3e8 #m/s

epsilon_0=8.85e-12 # F/m

def Gauss_delta_c(x,a,w,C):
    L_eff=np.sqrt(2*np.pi)*w
    return  C/L_eff*np.exp(-(x-a)**2/2/w**2)
def Gauss_delta_0(x,a,w,C,ImD,Gamma):
    L_eff=np.sqrt(2*np.pi)*w
    return  (ImD-C)/L_eff*np.exp(-(x-a)**2/2/w**2)+Gamma

def Gauss_shift(x,a,w,ReD): # in mks^(-1)
    L_eff=np.sqrt(2*np.pi)*w
    return  ReD/L_eff*np.exp(-(x-a)**2/2/w**2)
    
def get_taper_resonator_qualities(x_array,delta_c,delta_0,shift):
    '''
    Derive C,D,Gamma,ReD from the masurements of delta_0 and delta_c along cavity axis for the first axial WGM
    WGM distribution is assumed to be Gaussian
    
    return 
    [a,w,C,D,Gamma], errors[a,w,C,D,Gamma]
    '''
    
    def Gaussian_2D(x,a,w,C,ImD,Gamma):
        
        output=np.array([Gauss_delta_c(x,a,w,C), # for delta_c output
                         Gauss_delta_0(x,a,w,C,ImD,Gamma)]) # for delta_0 output
        return output.ravel()
    

    def Gaussian_3D(x,a,w,C,ReD,ImD,Gamma):
        
        output=np.array([Gauss_delta_c(x,a,w,C), # for delta_c output
                         Gauss_delta_0(x,a,w,C,ImD,Gamma), # for delta_0 output
                         Gauss_shift(x, a, w, ReD)])# shift
        return output.ravel()
    
    if use_ReD_joint_approximation:
        ydata = np.column_stack((delta_c,delta_0,shift))
        init_guess=[np.mean(x_array),(np.max(x_array)-np.min(x_array))/4,
                    10000,0,10000,10]
        bounds=[(-np.inf,0,0,-np.inf,0,0),(np.inf,1000,1e6,np.inf,1e6,1e6)]
        try:
            popt,pcov = curve_fit(Gaussian_3D, x_array, ydata.T.ravel(),p0=init_guess,bounds=bounds)
            perr = np.sqrt(np.diag(pcov))
            return popt,perr
        except Exception as e:
            print(e)
            return init_guess,np.array(init_guess)*0.1
        
    else:
        ydata = np.column_stack((delta_c,delta_0))
        init_guess=[np.mean(x_array),(np.max(x_array)-np.min(x_array))/4,
                    10000,10000,10]
        bounds=[(-np.inf,0,0,0,0),(np.inf,1000,1e6,1e6,1e6)]
        try:
            popt,pcov = curve_fit(Gaussian_2D, x_array, ydata.T.ravel(),p0=init_guess,bounds=bounds)
            perr = np.sqrt(np.diag(pcov))
            return popt,perr
        except Exception as e:
            print(e)
            return init_guess,np.array(init_guess)*0.1



def estimate_params(file):
    with open(file,'rb') as f:
        data=pickle.load(f)
        
    x=data['coordinates']
    delta_c=data['modes_parameters'][0]['delta_c']
    delta_0=data['modes_parameters'][0]['delta_0']
    delta_c_errors=data['modes_parameters'][0]['delta_c_error']
    delta_0_errors=data['modes_parameters'][0]['delta_0_error']
    
    
    shifts=data['modes_parameters'][0]['res_wavelength']
    lambda_0=np.nanmean(shifts)
    shifts-=np.nanmin(shifts)
    shifts_error=data['modes_parameters'][0]['res_wavelength_error']
    shifts=-shifts*2*np.pi*c/lambda_0**2 *1e3 # 1/mks
    
    ind_nan=np.argwhere(np.isnan(delta_c))
    ind_high_delta_c_errors=np.argwhere(delta_c_errors/delta_c>max_allowed_error)
    ind_high_delta_0_errors=np.argwhere(delta_0_errors/delta_0>max_allowed_error)
    if delete_unreliable_data:
        ind_to_delete = np.unique(np.concatenate((ind_nan,ind_high_delta_c_errors,ind_high_delta_0_errors)))
    else:
        ind_to_delete=ind_nan
    # ind_to_delete=sorted(np.unique(ind_nan+ind_high_delta_c_errors+ind_high_delta_0_errors))

        x=np.delete(x,ind_to_delete)
        delta_c=np.delete(delta_c,ind_to_delete)
        delta_0=np.delete(delta_0,ind_to_delete)
        delta_c_errors=np.delete(delta_c_errors,ind_to_delete)
        delta_0_errors=np.delete(delta_0_errors,ind_to_delete)
        shifts=np.delete(shifts,ind_to_delete)
        shifts_error=np.delete(shifts_error,ind_to_delete)
        
    popt,perr=get_taper_resonator_qualities(x,delta_c,delta_0,shifts)
    if use_ReD_joint_approximation:
        a,w,C,ReD,ImD,Gamma,a_err,w_err,C_err,ReD_err,ImD_err,Gamma_err=*popt,*perr
    else:
        a,w,C,ImD,Gamma,a_err,w_err,C_err,ImD_err,Gamma_err=*popt,*perr
        ind_center=np.argmin(abs(x-a))
        ReD=np.sqrt(2*np.pi)*w * shifts[ind_center] # L_eff [mkm] *\Omega [1/mks]
        ReD_err=0
    
    fig1,ax=plt.subplots(3,1,sharex=True)
    
    ax[0].errorbar(x,delta_c,delta_c_errors)
    ax[0].plot(x,Gauss_delta_c(x,a,w,C))
    ax[1].errorbar(x,delta_0,delta_0_errors)
    ax[1].plot(x,Gauss_delta_0(x,a,w,C,ImD,Gamma))
    ax[2].errorbar(x,shifts,shifts_error)
    ax[2].plot(x,Gauss_shift(x, a, w, ReD))
    ax[2].set_xlabel(r'Position, $\mu$m')
                    
    ax[0].set_ylabel('$\delta_c$, 1/$\mu$s')
    ax[1].set_ylabel('$\delta_0$, 1/$\mu$s')
    ax[2].set_ylabel('$\Omega$, 1/$\mu$s')
    
    results_text1='$C^2$=({:.1e} $\pm$ {:.1e}) '.format(C,C_err)+'$\mu m / \mu s$'
    ax[0].text(0.7, 0.9,results_text1,
              horizontalalignment='center',
              verticalalignment='center',
              transform = ax[0].transAxes)
    results_text2='ImD=({:.1e} $\pm$ {:.1e}) '.format(ImD,ImD_err)+'$\mu m / \mu s$'
    results_text3='\n $\Gamma$=({:.0f} $\pm$ {:.0f}) '.format(Gamma,Gamma_err)+'$\mu s^{-1}$'
    results_text4='\n $a$=({:.0f} $\pm$ {:.0f}) '.format(a,a_err)+'$\mu m$'
    results_text5='\n $w$=({:.0f} $\pm$ {:.0f}) '.format(w,w_err)+'$\mu m$'
  
    ax[1].text(0.7, 0.5,results_text2+results_text3+results_text4+results_text5,
              horizontalalignment='center',
              verticalalignment='center',
              transform = ax[1].transAxes)
    
    results_text6='ReD=({:.1e} $\pm$ {:.1e}) '.format(ReD,ReD_err)+'$\mu m / \mu s$'
    if use_ReD_joint_approximation:
        results_text6+='\n calculated jointly'
    else:
        results_text6+='\n calculated separately'
        
    ax[2].text(0.5, 0.3,results_text6,
              horizontalalignment='center',
              verticalalignment='center',
              transform = ax[2].transAxes)
    
    ax[0].set_ylim((0,np.nanmax(delta_c)*1.1))
    ax[1].set_ylim((0,np.nanmax(delta_0)*1.1))
    plt.tight_layout()
    
    plt.figure()
    Gamma_estimation=delta_0+(1-ImD/C)*delta_c
    plt.plot(x,Gamma_estimation)
    plt.xlabel(r'Position, $\mu$m')
    plt.ylabel('$\Gamma$,  1/$\mu$s')
    
    
    
    return  a,w,C,ReD,ImD,Gamma
    
    

if __name__=='__main__':
    estimate_params(file)

