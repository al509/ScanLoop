# -*- coding: utf-8 -*-
"""
Created on Wed Jun  9 17:48:51 2021

resave from txt to pkl

@author: Ilya
"""

import numpy as np
import pickle
pos_filename='Sp_Positions.txt'
spectra_filename='SpectraArray.txt'
waves_filename='WavelengthArray.txt'

f_name='Processed_spectrogram.pkl'

positions=np.loadtxt(pos_filename)
spectra=np.loadtxt(spectra_filename)
waves=np.loadtxt(waves_filename)


f=open(f_name,'wb')
D={}
D['axis']='Z'
D['Positions']=positions
D['Wavelengths']=waves
D['Signal']=spectra
pickle.dump(D,f)
f.close()