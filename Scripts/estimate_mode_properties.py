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
"""

__version__=2
__date__='21.10.2022'

import numpy as np
from scipy import special
import matplotlib.pyplot as plt 
from numba import jit

delta_c=100e6 # 2*pi*Hz
delta_0=300e6 # 2*pi*Hz
lambda_0=1550 # nm

n=1.445

length=200 # micron
R_0=62.5 #micron
delta_theta=1/3 # s^-1, thermal dissipation time, (11.35) from Gorodetsky, calculated numerically


P_in=0.05 # W
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


def get_cross_section():
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


cross_section=get_cross_section() # in m
volume=cross_section*length*1e-6 # m**3
zeta=epsilon_0*n*c*absorption*cross_section/(2*specific_heat*density*np.pi*R_0**2*1e-12)

F=np.sqrt(4*P_in*delta_c/(epsilon_0*n**2*volume))  #(11.21) 
field_intensity=F**2/(delta_c**2+delta_0**2) # (11.20)

heat_effect=field_intensity*zeta/delta_theta/P_in
temperature_shift=field_intensity*zeta/delta_theta*int_psi_4_by_int_psi_2
omega=c/(lambda_0*1e-9)*2*np.pi
delta=(delta_0+delta_c)*2

threshold=n**2*volume*delta**3/c/omega/n2/delta_c # Gorodecky (11.25)
print('Threshold for Kerr nonlinearity={} W'.format(threshold))
print('Q_factor={:.2e}, V={} m^3={} micron^3'.format(omega/delta,volume,volume*1e18))
print('Mode amplitude squared={:.3e} (V/m)**2'.format(field_intensity))
print('Thermal shift {} K '.format(temperature_shift))
print('Averaged temperature response is {} degrees per Watt of pump'.format(heat_effect))

