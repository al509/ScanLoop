# -*- coding: utf-8 -*-
"""
Created on Wed Jun  9 17:48:51 2021

resave from txt to pkl

@author: Ilya
"""

import numpy as np
import pickle

folder_path='C:\\!WorkFolder\\!Experiments\\!SNAP system\\!CO2 modification\\19.12.04\\Processed'



pos_filename='\\Sp_Positions.txt'
spectra_filename='\\SpectraArray.txt'
waves_filename='\\WavelengthArray.txt'

f_name='\\Processed_spectrogram.pkl'

positions=np.loadtxt(folder_path+pos_filename)
spectra=np.loadtxt(folder_path+spectra_filename)
waves=np.loadtxt(folder_path+waves_filename)


f=open(folder_path+f_name,'wb')
D={}
D['axis']='Z'
D['Positions']=positions
D['Wavelengths']=waves
D['Signal']=spectra
pickle.dump(D,f)
f.close()