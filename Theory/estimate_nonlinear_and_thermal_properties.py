# -*- coding: utf-8 -*-
"""
Created on Mon Mar 21 23:56:09 2022


@author: t-vatniki

Estimate different mode parameters:
    - Threshold for nonlinear Kerr effects
    - Mode amplitude under given pump rate AND
    - Change of the temperature of the cavity under pumping
    

Mode distributions are derived following Demchenko, Y. A. and Gorodetsky, M. L., “Analytical estimates of eigenfrequencies, dispersion, and field distribution in whispering gallery resonators,” J. Opt. Soc. Am. B 30(11), 3056 (2013).
eq(23)

Estimations given following М. Л. Городецкий, Оптические Микрорезонаторы с Гигантской Добротностью (2012).
"""

__version__=2.1
__date__='2022.12.18'

import numpy as np
from scipy import special
import matplotlib.pyplot as plt 
from numba import jit

delta_c=400e6 # 2*pi*Hz
delta_0=750e6 # 2*pi*Hz
lambda_0=1550 # nm

n=1.445

length=65 # micron
R_0=62.5 #micron
delta_theta=1/3 # s^-1, thermal dissipation time, (11.35) from Gorodetsky, calculated numerically


P_in=0.05 # W
'''
'''
C=6e4 # micron/microsec
Im_D=2e5 # micron/microsec
Gamma=40 # 1/microsec
w=26 # micron, gussian distribution
a=433 # micron, maximum position
'''


'''

m=355
p=1



n=1.445
c=3e8 #m/sec
n2=3.2e-20 #m**2/W


# absorption=6.65e12/4.343 * np.exp(-52.62/(lambda_0*1e-3))/1e6 # 1/m, after (10.7) Gorodetsky
# absorption=1e-3*1e2
absorption=5e-4*1e2 # 1/m

epsilon_0=8.85e-12 # F/m
int_psi_4_by_int_psi_2=0.7 # for gaussian distribution
specific_heat=680 # J/kg/K
density=2.2*1e3 # kg/m**3

delta_omega=0

hi_3=4*n2/3*epsilon_0*c*n**2
omega=c/(lambda_0*1e-9)*2*np.pi # 1/sec

def get_cross_section(R):
    T_mp=special.jn_zeros(m,p)[p-1]
    
    def E(x,R,pol='TE'): #phase not considered
        if pol=='TE':
            P=1
        elif pol=='TM':
            P=1/n**2
        k_0=m/R/n
        gamma=np.sqrt(n**2-1)*k_0
        R_eff=R+P/gamma
        
       
        if x<R:
            return special.jn(m,x/R_eff*T_mp)
        else:
            return 1/P *special.jn(m,R/R_eff*T_mp)*np.exp(-gamma*(x-R))
       
    
    step=R_0*0.0001 # Number of points
    r_min=R_0*0.8
    r_max=R_0*1.1
    
    F = np.vectorize(E)
    Rarray=np.arange(r_min,r_max,step)
    F_TM_Array=abs(F(Rarray,pol='TM', R=R_0))**2
    F_TE_Array=abs(F(Rarray,pol='TE',R=R_0))**2
    
    return sum(F_TM_Array*Rarray*2*np.pi)*step/max(F_TM_Array)*1e-12 # in m**2 , here we consider distributions normilized as max(I(r))=1

def volume(length,R): #length, R - in microns
    cross_section=get_cross_section(R) # in m
    volume=cross_section*length*1e-6 # m**3
    return volume
    
def F(delta_c,length,R):
    return np.sqrt(4*P_in*delta_c/(epsilon_0*n**2*volume(length,R)))  #(11.21) 

def get_field_intensity(delta_c,length,R):
    field_intensity=F(delta_c,length,R)**2/(delta_c+delta_0)**2 # (from first diff equation in 11.20)
    return field_intensity


def Kerr_threshold(wave,delta_c,delta_0,length,R):
    omega=c/(lambda_0*1e-9)*2*np.pi # 1/sec
    delta=(delta_0+delta_c)*2
    thres=n**2*volume(length,R)*delta**3/c/omega/n2/delta_c # Gorodecky (11.25)
    return thres

def get_heat_effect(delta_c,delta_0,length,R):
    zeta=epsilon_0*n*c*absorption*get_cross_section(R)/(2*specific_heat*density*np.pi*R_0**2*1e-12)
    heat_effect=get_field_intensity(delta_c,length,R)*zeta/delta_theta/P_in    
    temperature_shift=get_field_intensity(delta_c,length,R)*zeta/delta_theta*int_psi_4_by_int_psi_2
    return heat_effect,temperature_shift

def get_min_threshold(R,wave,a,w,C,D,Gamma):
    omega=c/(lambda_0*1e-9)*2*np.pi # 1/sec
    Leff=np.sqrt(2*np.pi)*w
    volume=get_cross_section(R)*Leff*1e-6
    min_threshold=9*epsilon_0*n**4*volume/4/omega/hi_3*(Gamma*1e6)**2*(D)/C
    position=a-np.sqrt(-(np.log(Gamma*Leff/2/D)*2*w**2))
    return min_threshold, position

if __name__=='__main__':
    delta=(delta_0+delta_c)*2
    
    threshold=Kerr_threshold(lambda_0,delta_c,delta_0,length,R_0)
    heat_effect,temperature_shift=get_heat_effect(delta_c,delta_0,length,R_0)
    min_threshold, position=get_min_threshold(R_0,omega,a,w,C,Im_D,Gamma)
    print(get_cross_section(62.5)*1e12)
    print('Threshold for Kerr nonlinearity={} W'.format(threshold))
    print('Minimal Threshold at optimized point={} W'.format(min_threshold))
    print('Q_factor={:.2e}, V={} m^3={} micron^3'.format(omega/delta,volume(length,R_0),volume(length,R_0)*1e18))
    print('Mode amplitude squared={:.3e} (V/m)**2'.format(get_field_intensity(delta_c,length,R_0)))
    print('Thermal shift {} K '.format(temperature_shift))
    print('Averaged temperature response is {} degrees per Watt of pump'.format(heat_effect))
    
