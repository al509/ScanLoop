# -*- coding: utf-8 -*-
"""
Created on Tue Aug 23 21:11:28 2022

@author: Илья
"""

import pickle
import os    
def find_between( s, first, last ): ## local function to find the substring between two given strings
    try:
        start = s.index( first ) + len( first )
        end = s.index( last, start )
        return s[start:end]
    except ValueError:
        return ""
def get_position_from_file_name(string,axis): # extract postitions of the contact from the file name

    if axis=='X':
        return float(find_between(string,'X=','_Y'))
    if axis=='Y':
        return float(find_between(string,'Y=','_Z'))
    if axis=='Z':
        return float(find_between(string,'Z=','_.'))
    if axis=='W':
        try:
            a=float(find_between(string,'W=','_'))
        except:
            a=0
        return a
    if axis=='p':
        try:
            a=int(find_between(string,'p=','_'))
        except:
            a=0
        return a
def Create2DListOfFiles(InputFileList,axis='X'):  
    '''
    Find all files which acqured at the same point
    
    return  structures file list and list of positions in microns!
    '''
    
    NewFileList=[]
    Positions=[]
    FileList=InputFileList.copy()

    while FileList:
        Name=FileList[0]
        s=axis+'='+str(get_position_from_file_name(Name,axis=axis))+'_'
         #s=s[2] # take signature of the position,  etc
        Temp=[T for T in FileList if s in T]  # take all 'signature' + 'i' instances
        NewFileList.append(Temp)
        Positions.append([get_position_from_file_name(Name,axis='X'),
                          get_position_from_file_name(Name,axis='Y'),
                          get_position_from_file_name(Name,axis='Z'),
                          get_position_from_file_name(Name,axis='W'),
                          get_position_from_file_name(Name,axis='p')])
        FileList=[T for T in FileList if not (T in Temp)]
    return NewFileList,Positions

AllFilesList=os.listdir('SpectralBinData\\')
OutOfContactFileList=[]
ContactFileList=[]
type_of_input_data='bin'
is_remove_background_out_of_contact=False
axis_to_plot_along='X'
if '.gitignore' in AllFilesList:AllFilesList.remove('.gitignore')
for file in AllFilesList:
   if type_of_input_data in file:
        if 'out_of_contact' in file and is_remove_background_out_of_contact:
            OutOfContactFileList.append(file)
        elif 'out_of_contact' not in file:
            ContactFileList.append(file)
ContactFileList=sorted(ContactFileList,key=lambda s:get_position_from_file_name(s,axis=axis_to_plot_along))
StructuredFileList,Positions=Create2DListOfFiles(ContactFileList,axis=axis_to_plot_along)
