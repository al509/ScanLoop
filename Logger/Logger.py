import numpy as np
import json
import sys,os
import pickle

from PyQt5.QtCore import QObject, pyqtSignal




class Logger(QObject):
    updated = pyqtSignal()
    path=os.getcwd()
    ZeroPositionFileName=path+'\\ZeroPosition.txt'
    SpectralDataFolder=path+'\\SpectralData\\'
    SpectralBinaryDataFolder=path+'\\SpectralBinData\\'
    TDFolder=path+'\\TimeDomainData\\'
    ParametersFileName=path+'\\Parameters.txt'
    
    def __init__(self, parent=None):
        super().__init__(parent)

        self.counter = 0
        self.spectra = None
        self.wavelengths = None
        self.positions = list()
        self.file=None
        self.saving_file_type='bin'



    def save_data(self, Data,name,X,Y,Z,SourceOfData:str):
        if SourceOfData=='FromScope':
            FilePrefix=self.TDFolder+'TD_'+name
        elif SourceOfData=='FromOSA':
            FilePrefix=self.SpectralDataFolder+'Sp_'+name
        FileName=FilePrefix+'_X={}_Y={}_Z={}_'.format(X,Y,Z)
        if self.saving_file_type=='txt':
            np.savetxt(FileName+'.txt', Data)
        elif self.saving_file_type=='bin':
            f = open(FileName+'.pkl',"wb")
            pickle.dump(Data,f)
            f.close()
        print('\nData saved\n')

    def save_parameters(self, list_dictionaries):
        f=open(self.ParametersFileName,'w')
        json.encoder.FLOAT_REPR = lambda x: format(x, '.5f') if (x<0.01) else x
        json.dump(list_dictionaries,f)
        f.close()
        print('\nParameters saved\n')

    def load_parameters(self):
        '''
        load dictionaries of the parameters from file to dict
        '''
        try:
            f=open(self.ParametersFileName)
            Dicts=json.load(f)
            f.close()
            print('\nParameters loaded\n')
            return Dicts
        except FileNotFoundError:
            print('Error while load parameters: Parameters file not found')
            return None
        except json.JSONDecodeError:
            print('Errpr while load parameters: file has wrong format')
            return None
        
    
    def save_zero_position(self,X:int,Y:int,Z:int):
        Dict={}
        Dict['X_0']=str(X)
        Dict['Y_0']=str(Y)
        Dict['Z_0']=str(Z)
        f=open(self.ZeroPositionFileName,'w')
        json.dump(Dict,f)
        f.close()
        print('\nzero position saved\n')
        
    def load_zero_position(self):
        try:
            f=open(self.ZeroPositionFileName)
        except FileNotFoundError:
            return 0,0,0,
        try:
            dictionary=json.load(f)
            f.close()
            return float(dictionary['X_0']),float(dictionary['Y_0']),float(dictionary['Z_0'])
        except:
            return 0,0,0


    


if __name__ == "__main__":
    logger = Logger()
    logger.savePosition(10,323,0,'54')
    logger.savePosition(10,423,40,'545')
    del logger