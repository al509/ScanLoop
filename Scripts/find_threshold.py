# -*- coding: utf-8 -*-
"""
Created on Mon Mar 21 23:56:09 2022

@author: t-vatniki
"""
import numpy as np

delta_c=10e6 # 2*pi*Hz
delta_0=30e6 # 2*pi*Hz
length=700e-6 # m
R=62.5e-6 #m

c=3e8 #m/sec
n2=3.2e-20 #m**2/W


dR=1.5e-6 #m 
const=2*np.pi*R*dR
lambda_0=1550e-9 #m
n=1.5
V=const*length
omega=c/lambda_0*2*np.pi
delta=(delta_0+delta_c)*2

threshold=n**2*V*delta**3/c/omega/n2/delta_c # Gorodecky (11.25)
print('Threshold={} W'.format(threshold))
print('Q_factor={:.2e},V={}'.format(omega/delta,V))