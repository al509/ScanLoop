"""
Version Nov 13 2019
"""

import os
import numpy as np
import matplotlib.pyplot as plt
import time
from scipy import interpolate
from PyQt5.QtCore import QObject


class ProcessAndPlotTD(QObject):
    ProcessedDataFolder='ProcessedData\\'
    skip_Header=0
    axis_to_plot_along='X'
    number_of_axis={'X':0,'Y':1,'Z':2}
    
#    
    def get_sampling_rate(self,FileName):
        return float(self.find_between(FileName,'SR=','_p'))
        
    def find_between(self, s, first, last ): ## local function to find the substring between two given strings
        try:
            start = s.index( first ) + len( first )
            end = s.index( last, start )
            return s[start:end]
        except ValueError:
            return ""

    def get_position_from_file_name(self,string,axis):
        if axis=='X':
            return int(self.find_between(string,'X=','_Y'))
        if axis=='Y':
            return int(self.find_between(string,'Y=','_Z'))
        if axis=='Z':
            return int(self.find_between(string,'Z=','_.'))



    def Create2DListOfFiles(self,FileList,axis='X'):  #Find all files which acqured at the same point
        NewFileList=[]
        Positions=[]
        ## if Files are named with X position then Using new 
        while FileList:
            Name=FileList[0]
            s=axis+'='+str(self.get_position_from_file_name(Name,axis=axis))
             #s=s[2] # take signature of the position,  etc
            Temp=[T for T in FileList if s in T]  # take all 'signature' + 'i' instances
            NewFileList.append(Temp)
            Positions.append([self.get_position_from_file_name(Name,axis='X'),
                              self.get_position_from_file_name(Name,axis='Y'),
                              self.get_position_from_file_name(Name,axis='Z')])
            FileList=[T for T in FileList if not (T in Temp)]
        return NewFileList,Positions
        



    def InterpolateInDesiredPoint(self, YArray,XOldArray,XNewarray):
        f=interpolate.interp1d(XOldArray,YArray,fill_value='extrapolate')
        Output=f(XNewarray)
        if np.isinf(Output[0]):
            Output[0]=np.mean(Output[1:-1])
        if np.isinf(Output[-1]):
            Output[-1]=np.mean(Output[1:-1])
        return Output



    def run(self,Averaging:bool,DirName,axis_to_plot_along='X',channel_number=0):
        self.axis_to_plot_along=axis_to_plot_along
        time1=time.time()
        FileList=os.listdir(DirName)
        if '.gitignore' in FileList:FileList.remove('.gitignore')
        sampling_rate=self.get_sampling_rate(FileList[0])
        
        """
        group files at each point
        """
        FileList=sorted(FileList,key=lambda s:self.get_position_from_file_name(s,axis=axis_to_plot_along))
        StructuredFileList,Positions=self.Create2DListOfFiles(FileList,axis=axis_to_plot_along)
        NumberOfPointsScanAxis=len(StructuredFileList)
        #Data = np.loadtxt(DirName+ '\\Signal' + '\\' +FileList[0])
        print(DirName+ '\\' +FileList[0])
        """
        Create data array
        """
        Data = np.genfromtxt(DirName+ '\\' +FileList[0],skip_header=self.skip_Header)
        if np.size(Data[0])>1:
            Data=Data[channel_number,:]
        NumberOfTimePoints=len(Data)
        SignalArray=np.zeros((NumberOfTimePoints,NumberOfPointsScanAxis))
        
       
        """
        Process files at each group
        """
        for ii,FileNameListAtPoint in enumerate(StructuredFileList):
            NumberOfArraysToAverage=len(FileNameListAtPoint)
            SmallSignalArray=np.zeros((NumberOfTimePoints,NumberOfArraysToAverage))
            print(FileNameListAtPoint[0])
           
            if Averaging:
                """
                Apply averaging across the spectra at one point
                """
                for jj, FileName in enumerate(FileNameListAtPoint):
                    Data= np.genfromtxt(DirName+ '\\' +FileName,skip_header=self.skip_Header)
                    if np.size(Data[0])>1:
                        SmallSignalArray[:,jj]=Data[channel_number,:]
                    else:
                        SmallSignalArray[:,jj]=Data
                SignalArray[:,ii]=np.mean(SmallSignalArray,axis=1)
            else:
                """
                    If shifting and averaging are OFF, just take the first spectrum from the bundle correpsonding to a measuring point
                """
                Data= np.genfromtxt(DirName+ '\\' +FileNameListAtPoint[0],skip_header=self.skip_Header)
                if np.size(Data[0])>1:
                    SignalArray[:,ii]=Data[channel_number,:]
                else:
                    SignalArray[:,ii]=Data

        TimeArray=np.arange(0,sampling_rate*NumberOfTimePoints,sampling_rate)
        
        np.savetxt(self.ProcessedDataFolder+'TDArray.txt',SignalArray)
        np.savetxt(self.ProcessedDataFolder+'TimesArray.txt', TimeArray)
        np.savetxt(self.ProcessedDataFolder+'TD_Positions.txt', Positions)

                

        plt.figure()
        Positions_at_given_axis=np.array([s[self.number_of_axis[self.axis_to_plot_along]] for s in Positions])
        Img=plt.contourf(Positions_at_given_axis,TimeArray,SignalArray,200,cmap='RdBu_r')
        plt.xlabel('Position, steps (2.5 um each)')
        plt.ylabel('Time,s')
        ax1=plt.gca()
        ax2=(ax1).twiny()
        ax2.set_xlabel('Distance, um')
        ax2.set_xlim([0,(np.max(Positions_at_given_axis)-np.min(Positions_at_given_axis))*2.5])
        time2=time.time()
        cbar=plt.colorbar(Img,ax=ax1)
        plt.savefig(self.ProcessedDataFolder+'Scanned TD')
        print('Time used =', time2-time1 ,' s')

if __name__ == "__main__":
    os.chdir('..')
    ProcessTD=ProcessAndPlotTD()
    ProcessTD.run(Averaging=True,
                  DirName='TimeDomainData',axis_to_plot_along='Y',
                  channel_number=0)