# -*- coding: utf-8 -*-
"""
Created on Thu Sep 30 17:56:24 2021

@author: Ilya
"""
import pickle
import matplotlib.pyplot as plt
import numpy as np
import os

os.chdir('..')
# single_spectrum_path='test.pkl'
single_spectrum_path='taper_self_scan__new_slice.pkl'
with open(single_spectrum_path,'rb') as f:
    print('loading data for analyzer from ',single_spectrum_path)
    Data=(pickle.load(f))
print(Data[:,1])
a=np.array(Data[:,1])
plt.plot(Data[:,1])