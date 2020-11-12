"""
Version 10.06.2020
"""
import os
import numpy as np
import matplotlib.pyplot as plt
import time
from scipy import interpolate
from PyQt5.QtCore import QObject
import pickle


class ProcessSpectra(QObject):

    def __init__(self, path_to_main):
        QObject.__init__(self)
        self.ProcessedDataFolder=path_to_main+'\\ProcessedData\\'
        self.Source_DirName=path_to_main+'\\SpectralData\\'
    skip_Header=3
    LowFreqEdge=0.000 ##For FFT filter. Set <0 to avoid
    HighFreqEdge=30 ##For FFT filter. Set >1 to avoid
    StepSize=30*2.5 # um, Step in Z direction

    MinimumPeakDepth=2  ## For peak searching
    MinimumPeakDistance=500 ## For peak searching
    file_naming_style='new'
    axis_to_plot_along='X'
    number_of_axis={'X':0,'Y':1,'Z':2,'W':3,'p':4}
    AccuracyOfWavelength=0.008 # in nm. Maximum expected shift to define the correlation window
    type_of_data='bin'
    Cmap='jet'
#
    def define_file_naming_style(self,FileName): # legacy code
        if FileName.find('X=')==-1:
            self.file_naming_style='old'
        else:
            self.file_naming_style='new'

    def find_between(self, s, first, last ): ## local function to find the substring between two given strings
        try:
            start = s.index( first ) + len( first )
            end = s.index( last, start )
            return s[start:end]
        except ValueError:
            return ""

    def get_min_max_wavelengths_from_file(self,file): # fastly extract min, maximum wavelength from the file
        def extract_wavelength_from_line(bytes_array):
            s=bytes_array.decode()
            a=s.find(' ')
            s=s[0:a]
            return float(s)
        if self.type_of_data=='txt':
            with open(file, "rb") as f:
                min_wavelength = extract_wavelength_from_line(f.readline())        # Read the first line.
                f.seek(-2, os.SEEK_END)     # Jump to the second last byte.
                while f.read(1) != b"\n":   # Until EOL is found...
                    f.seek(-2, os.SEEK_CUR) # ...jump back the read byte plus one more.
                max_wavelength = extract_wavelength_from_line(f.readline())         # Read last line.
            f.close()
            return min_wavelength,max_wavelength
        else:
            Data=pickle.load(open(file,"rb"))
            return Data[0,0],Data[-1,0]

    def get_position_from_file_name(self,string,axis): # extract postitions of the contact from the file name
        if self.file_naming_style=='old':
            string=string.split('_');
            return float(string[2])
        else:
            if axis=='X':
                return int(self.find_between(string,'X=','_Y'))
            if axis=='Y':
                return int(self.find_between(string,'Y=','_Z'))
            if axis=='Z':
                return int(self.find_between(string,'Z=','_.'))
            if axis=='W':
                try:
                    a=float(self.find_between(string,'W=','_'))
                except:
                    a=0
                return a
            if axis=='p':
                try:
                    a=int(self.find_between(string,'p=','_'))
                except:
                    a=0
                return a

    def Create2DListOfFiles(self,FileList,axis='X'):  #Find all files which acqured at the same point
        NewFileList=[]
        Positions=[]
        ## if Files are named with X position then Using new
        if self.file_naming_style=='old':
            while FileList:
                Name=FileList[0]
                s=Name[:Name.rfind('_')+1]
                 #s=s[2] # take signature of the position,  etc
                Temp=[T for T in FileList if s in T]  # take all 'signature' + 'i' instances
                NewFileList.append(Temp)
                FileList=[T for T in FileList if not (T in Temp)]
            return NewFileList,Positions
        else:
        ## if Files are named with X position then Using new
            while FileList:
                Name=FileList[0]
                s=axis+'='+str(self.get_position_from_file_name(Name,axis=axis))+'_'
                 #s=s[2] # take signature of the position,  etc
                Temp=[T for T in FileList if s in T]  # take all 'signature' + 'i' instances
                NewFileList.append(Temp)
                Positions.append([self.get_position_from_file_name(Name,axis='X'),
                                  self.get_position_from_file_name(Name,axis='Y'),
                                  self.get_position_from_file_name(Name,axis='Z'),
                                  self.get_position_from_file_name(Name,axis='W'),
                                  self.get_position_from_file_name(Name,axis='p')])
                FileList=[T for T in FileList if not (T in Temp)]
            return NewFileList,Positions




    def InterpolateInDesiredPoint(self, YArray,XOldArray,XNewarray):
        f=interpolate.interp1d(XOldArray,YArray,bounds_error=False,fill_value=np.nan)
        Output=f(XNewarray)
        return Output

    def plot_sample_shape(self,axis_to_plot_along):
        from mpl_toolkits.mplot3d import Axes3D
        FileList=os.listdir(self.Source_DirName)
        if '.gitignore' in FileList:FileList.remove('.gitignore')
        FileList=sorted(FileList,key=lambda s:self.get_position_from_file_name(s,axis=axis_to_plot_along))
        StructuredFileList,Positions=self.Create2DListOfFiles(FileList,axis=axis_to_plot_along)
        Positions=np.array(Positions)
        plt.figure()
        ax = plt.axes(projection='3d')
        ax.plot(Positions[:,2],Positions[:,0],Positions[:,1])
        ax.set_xlabel('Z,steps')
        ax.set_ylabel('X,steps')
        ax.set_zlabel('Y,steps')
        plt.gca().invert_zaxis()
        plt.gca().invert_xaxis()




    def run(self,StepSize,Averaging:bool,Shifting:bool,axis_to_plot_along='X',type_of_data='bin'):
        self.type_of_data=type_of_data
        self.axis_to_plot_along=axis_to_plot_along
        AccuracyOfWavelength=self.AccuracyOfWavelength
        time1=time.time()
        FileList=os.listdir(self.Source_DirName)
        if '.gitignore' in FileList:FileList.remove('.gitignore')
        self.define_file_naming_style(FileList[0])
        """
        group files at each point
        """
        FileList=sorted(FileList,key=lambda s:self.get_position_from_file_name(s,axis=axis_to_plot_along))
        StructuredFileList,Positions=self.Create2DListOfFiles(FileList,axis=axis_to_plot_along)
        NumberOfPointsZ=len(StructuredFileList)
        #Data = np.loadtxt(DirName+ '\\Signal' + '\\' +FileList[0])
        print(self.Source_DirName+ FileList[0])
        """
        Create main wavelength array
        """
        MinWavelength,MaxWavelength=self.get_min_max_wavelengths_from_file(self.Source_DirName +FileList[0])
        if type_of_data=='bin':
            Data = pickle.load(open(self.Source_DirName +FileList[0], "rb"))[:,0]
        elif type_of_data=='txt':
            Data=np.genfromtxt(self.Source_DirName +FileList[0],skip_header=self.skip_Header)[:,0]
        WavelengthStep=np.max(np.diff(Data))
        for File in FileList:
            try:
                minw,maxw=self.get_min_max_wavelengths_from_file(self.Source_DirName +File)
            except UnicodeDecodeError:
                print('Error while getting wavelengths from file {}'.format(File))

            if minw<MinWavelength:
                MinWavelength=minw
            if maxw>MaxWavelength:
                MaxWavelength=maxw
        MainWavelengths=np.arange(MinWavelength,MaxWavelength,WavelengthStep)
        NumberOfWavelengthPoints=len(MainWavelengths)
        SignalArray=np.zeros((NumberOfWavelengthPoints,NumberOfPointsZ))


        """
        Process files at each group
        """
        for ii,FileNameListAtPoint in enumerate(StructuredFileList):
            NumberOfArraysToAverage=len(FileNameListAtPoint)
            SmallSignalArray=np.zeros((NumberOfWavelengthPoints,NumberOfArraysToAverage))
            ShiftIndexesMatrix=np.zeros((NumberOfArraysToAverage,NumberOfArraysToAverage))
            print(FileNameListAtPoint[0])
            for jj, FileName in enumerate(FileNameListAtPoint):
                try:
                    if type_of_data=='bin':
                        Data = pickle.load(open(self.Source_DirName +FileName, "rb"))
                    elif type_of_data=='txt':
                        Data = np.genfromtxt(self.Source_DirName +FileName,skip_header=self.skip_Header)
                except UnicodeDecodeError:
                    print('Error while getting data from file {}'.format(FileName))
                SmallSignalArray[:,jj]=self.InterpolateInDesiredPoint(Data[:,1],Data[:,0],MainWavelengths)
            SignalLog=np.zeros(NumberOfWavelengthPoints)
            MeanLevel=np.mean(SmallSignalArray)
            ShiftArray=np.zeros(NumberOfArraysToAverage)
            if Averaging or Shifting:
                if Shifting:
                    """
                    Apply cross-correlation for more accurate absolute wavelength determination
                    """
                    for jj, FileName in enumerate(FileNameListAtPoint):
                        for kk, FileName in enumerate(FileNameListAtPoint):
                            if jj<kk:
                                Temp=np.correlate(SmallSignalArray[int(AccuracyOfWavelength/WavelengthStep):-int(AccuracyOfWavelength/WavelengthStep),kk],SmallSignalArray[:,jj], mode='valid')/ \
                                    np.sum(SmallSignalArray[int(AccuracyOfWavelength/WavelengthStep):-int(AccuracyOfWavelength/WavelengthStep),jj]**2)
                                ShiftIndexesMatrix[jj,kk]=np.nanargmax(Temp)-np.floor(AccuracyOfWavelength/WavelengthStep)
                                ShiftIndexesMatrix[kk,jj]=-ShiftIndexesMatrix[jj,kk]
                    ShiftArray=(np.mean(ShiftIndexesMatrix,1))
                   
                if Averaging:
                    """
                    Apply averaging across the spectra at one point
                    """
                    for jj, FileName in enumerate(FileNameListAtPoint):
                        Temp=np.ones(NumberOfWavelengthPoints)*MeanLevel
                        Temp[int(AccuracyOfWavelength/WavelengthStep)+int(ShiftArray[jj]):-int(AccuracyOfWavelength/WavelengthStep)+int(ShiftArray[jj])]=SmallSignalArray[int(AccuracyOfWavelength/WavelengthStep):-int(AccuracyOfWavelength/WavelengthStep),jj]
                        SignalLog+=Temp
                    SignalArray[:,ii]=SignalLog/NumberOfArraysToAverage#-np.nanmax(SignalLog)
                elif Shifting:
                    Temp=np.ones(NumberOfWavelengthPoints)*MeanLevel
                    Temp[int(AccuracyOfWavelength/WavelengthStep)+int(ShiftArray[0]):-int(AccuracyOfWavelength/WavelengthStep)+int(ShiftArray[0])]=SmallSignalArray[int(AccuracyOfWavelength/WavelengthStep):-int(AccuracyOfWavelength/WavelengthStep),0]
                    SignalArray[:,ii]=Temp
            else:
                """
                    If shifting and averaging are OFF, just take the first spectrum from the bundle correpsonding to a measuring point
                """
                SignalArray[:,ii]=SmallSignalArray[:,0]

        f=open(self.ProcessedDataFolder+'Processed_spectrogram.pkl','wb')
        D={}
        D['axis']=axis_to_plot_along
        D['Positions']=Positions
        D['Wavelengths']=MainWavelengths
        D['Signal']=SignalArray
        pickle.dump(D,f)
        f.close()

        if self.file_naming_style=='old': # legacy code
            plt.figure()
            X_0=0
            X_max=StepSize*NumberOfPointsZ
            plt.imshow(SignalArray, interpolation = 'bilinear',aspect='auto',cmap=self.Cmap,extent=[X_0,X_max,MainWavelengths[0],MainWavelengths[-1]],origin='lower')# vmax=0, vmin=-1)

            plt.show()
            plt.colorbar()
            plt.xlabel(r'Position, steps (2.5 $\mu$m each)')
            plt.ylabel('Wavelength, nm')
            ax2=(plt.gca()).twiny()
            ax2.set_xlabel(r'Distance, $\mu$m')
            ax2.set_xlim([0,StepSize*NumberOfPointsZ*2.5])
            plt.tight_layout()
            plt.savefig(self.ProcessedDataFolder+'Scanned WGM spectra')
            Positions=[np.linspace(0, StepSize*NumberOfPointsZ,NumberOfPointsZ),np.linspace(0, StepSize*NumberOfPointsZ,NumberOfPointsZ),np.linspace(0, StepSize*NumberOfPointsZ,NumberOfPointsZ)]
            Positions=np.transpose(Positions)
            np.savetxt(self.ProcessedDataFolder+'Sp_Positions.txt', Positions)

        if self.file_naming_style=='new':
            plt.figure()
            Positions_at_given_axis=np.array([s[self.number_of_axis[self.axis_to_plot_along]] for s in Positions])
#            try:
#                plt.pcolorfast(Positions_at_given_axis,MainWavelengths,SignalArray,cmap=self.Cmap)
#            except:
            plt.contourf(Positions_at_given_axis,MainWavelengths,SignalArray,200,cmap=self.Cmap)
#            plt.gca().pcolorfast(Positions_at_given_axis,MainWavelengths,SignalArray)
            plt.ylabel('Wavelength, nm')
            if self.axis_to_plot_along!='W':
                plt.xlabel(r'Position, steps (2.5 $\mu$m each)')
                ax2=(plt.gca()).twiny()
                ax2.set_xlabel(r'Distance, $\mu$m')
                ax2.set_xlim([np.min(Positions_at_given_axis)*2.5, np.max(Positions_at_given_axis)*2.5])
            else:
                plt.xlabel('Wavelength,nm')
            plt.colorbar()
            plt.tight_layout()
            plt.savefig(self.ProcessedDataFolder+'Scanned WGM spectra')
            time2=time.time()
        print('Time used =', time2-time1 ,' s')

if __name__ == "__main__":
    os.chdir('..')
    path= os.getcwd()
    
    ProcessSpectra=ProcessSpectra(path)
#    ProcessSpectra.plot_sample_shape(DirName='SpectralData',
#                                     axis_to_plot_along='Z')

    ProcessSpectra.run(StepSize=20,Shifting=True, Averaging=True,axis_to_plot_along='p',type_of_data='bin')