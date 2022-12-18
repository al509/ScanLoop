# -*- coding: utf-8 -*-
"""
Created on Sun Dec 18 01:39:35 2022


@author: t-vatniki

following paper of Kolesnikova 
"""

__version__='1'
__date__='2022.12.18'

import numpy as np
import pickle
import matplotlib.pyplot as plt
from  scipy.optimize import curve_fit


max_allowed_error=0.2 #  omit data with higher relative error
file=r"C:\!WorkFolder\!Experiments\!SNAP system\2022.12 playing with parameters\potential 4\parabola3_resaved_mode_parameters.pkl"

epsilon_0=8.85e-12 # F/m

def Gauss_delta_c(x,a,w,C):
    L_eff=(2*np.pi*w)
    return  C/L_eff*np.exp(-(x-a)**2/2/w**2)
def Gauss_delta_0(x,a,w,C,D,Gamma):
    L_eff=(2*np.pi*w)
    return  (D-C)/L_eff*np.exp(-(x-a)**2/2/w**2)+Gamma
    
def get_taper_resonator_qualities(x_array,delta_c,delta_0):
    '''
    Derive C,D,Gamma from the masurements of delta_0 and delta_c along cavity axis for the first axial WGM
    WGM distribution is assumed to be Gaussian
    return 
    [a,w,C,D,Gamma], errors[a,w,C,D,Gamma]
    '''
    

    def Gaussian_2D(x,a,w,C,D,Gamma):
        
        output=np.array([Gauss_delta_c(x,a,w,C), # for delta_c output
                         Gauss_delta_0(x,a,w,C,D,Gamma)])# for delta_0 output
        return output.ravel()
    
    ydata = np.column_stack((delta_c,delta_0))
    init_guess=[np.mean(x_array),(np.max(x_array)-np.min(x_array))/4,
                10000,10000,10]
    bounds=[(0,np.inf),(0,np.inf),(0,np.inf),(0,np.inf),(0,100)]
    try:
        popt,pcov = curve_fit(Gaussian_2D, x_array, ydata.T.ravel(),p0=init_guess)
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
    ind_nan=np.argwhere(np.isnan(delta_c))
    ind_high_delta_c_errors=np.argwhere(delta_c_errors/delta_c>max_allowed_error)
    ind_high_delta_0_errors=np.argwhere(delta_0_errors/delta_0>max_allowed_error)
    
    ind_to_delete = np.unique(np.concatenate((ind_nan,ind_high_delta_c_errors,ind_high_delta_0_errors)))
    
    # ind_to_delete=sorted(np.unique(ind_nan+ind_high_delta_c_errors+ind_high_delta_0_errors))
    x=np.delete(x,ind_to_delete)
    delta_c=np.delete(delta_c,ind_to_delete)
    delta_0=np.delete(delta_0,ind_to_delete)
    delta_c_errors=np.delete(delta_c_errors,ind_to_delete)
    delta_0_errors=np.delete(delta_0_errors,ind_to_delete)
    
    popt,perr=get_taper_resonator_qualities(x,delta_c,delta_0)
    a,w,C,D,Gamma,a_err,w_err,C_err,D_err,Gamma_err=*popt,*perr
    fig1,ax=plt.subplots(2,1,sharex=True)
    
    ax[0].errorbar(x,delta_c,delta_c_errors)
    ax[0].plot(x,Gauss_delta_c(x,a,w,C))
    ax[1].errorbar(x,delta_0,delta_0_errors)
    ax[1].plot(x,Gauss_delta_0(x,a,w,C,D,Gamma))
    ax[1].set_xlabel(r'Position, $\mu$m')
                    
    ax[0].set_ylabel('$\delta_c$, 1/$\mu$s')
    ax[1].set_ylabel('$\delta_0$, 1/$\mu$s')
    
    results_text1='\n C=({:.1e} $\pm$ {:.1e}) '.format(C,C_err)+'$\mu m / \mu s$'
    results_text2='\n D=({:.1e} $\pm$ {:.1e}) '.format(D,D_err)+'$\mu m / \mu s$'
    results_text3='\n $\Gamma$=({:.0f} $\pm$ {:.0f}) '.format(Gamma,Gamma_err)+'$\mu s^{-1}$'
    results_text4='\n $a$=({:.0f} $\pm$ {:.0f}) '.format(a,a_err)+'$\mu m$'
    results_text5='\n $w$=({:.0f} $\pm$ {:.0f}) '.format(w,w_err)+'$\mu m$'
    results_text=results_text1+results_text2+results_text3+results_text4+results_text5
    ax[0].text(0.5, 0.3,results_text,
              horizontalalignment='center',
              verticalalignment='center',
              transform = ax[0].transAxes)
    plt.tight_layout()
    return  a,w,C,D,Gamma
    
    

if __name__=='__main__':
    estimate_params(file)
