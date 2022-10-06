# -*- coding: utf-8 -*-
"""
Created on Mon Mar 21 23:56:09 2022


@author: t-vatniki

Estimate different mode parameters:
    - Threshold for nonlinear Kerr effects
    - Mode amplitude under given pump rate AND
    - Change of the temperature of the cavity
    

Mode distributions are derived following Demchenko, Y. A. and Gorodetsky, M. L., “Analytical estimates of eigenfrequencies, dispersion, and field distribution in whispering gallery resonators,” J. Opt. Soc. Am. B 30(11), 3056 (2013).
"""

__version__=2
import numpy as np
from scipy import special

delta_c=10e6 # 2*pi*Hz
delta_0=30e6 # 2*pi*Hz
length=700e-6 # m

R=62.5e-6 #m

c=3e8 #m/sec
n2=3.2e-20 #m**2/W



def E(x,m,p,R,pol='TE'): #phase not considered
    if pol=='TE':
        P=1
    elif pol=='TM':
        P=1/n**2
    k_0=m/R/n
    gamma=np.sqrt(n**2-1)*k_0
    R_eff=R+P/gamma
    T_mp=special.jn_zeros(m,p)[p-1]
    argument=-(2/m)**(-1/3)*(T_mp*x/R_eff-m)
    # if argument<-10:
        # print('temp<')
    if x<R:
        return special.airy(argument)[0]
    else:
        return 1/P * special.airy(-(2/m)**(-1/3)*(T_mp*R/R_eff-m))[0]*np.exp(-gamma*(x-R))
    



step=R*0.0001 # Number of points
r_min=R*0.9
r_max=R*1.1
radial_number=2


F = np.vectorize(E)
Rarray=np.arange(r_min,r_max,step)
F_TM_Array=abs(F(Rarray,m=m,p=radial_number,pol='TM', R=R))**2
F_TE_Array=abs(F(Rarray,m=m,p=radial_number,pol='TE',R=R))**2


plt.figure(1)    
plt.clf()
plt.plot(Rarray,F_TM_Array)
plt.plot(Rarray,F_TE_Array)
X_TM_Max=Rarray[(np.argmax(F_TM_Array))]
X_TE_Max=Rarray[(np.argmax(F_TE_Array))]
print('Positions of maximum of TM and TE WGMS are ', X_TM_Max,' and ',X_TE_Max)
print('X_TM_Max/X_TE_Max= ',X_TM_Max/X_TE_Max)


dR=1.5e-6 #m 
const=2*np.pi*R*dR
lambda_0=1550e-9 #m
n=1.5
V=const*length
omega=c/lambda_0*2*np.pi
delta=(delta_0+delta_c)*2

threshold=n**2*V*delta**3/c/omega/n2/delta_c # Gorodecky (11.25)
print('Threshold={} W'.format(threshold))
print('Q_factor={:.2e},V={} m^3'.format(omega/delta,V))