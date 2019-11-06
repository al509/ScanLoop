import datetime
import os
import numpy as np
import json

from PyQt5.QtCore import QObject, pyqtSignal, QFile, QIODevice

from Common.Consts import Consts
from Utils.PyQtUtils import pyqtSlotWExceptions

import time


class Logger(QObject):
    updated = pyqtSignal()
    t = 0
    ZeroPositionFileName='ZeroPosition.txt'
    SavedDataFolderName='SavedData'
    ParametersFileName='Parameters.txt'

    def __init__(self, parent=None):
        super().__init__(parent)

        self.counter = 0
        self.spectra = None
        self.wavelengths = None
        self.positions = list()
        self.file=None



    def save_data(self, Data,FilePrefix,X,Y,Z):
        FileName=self.SavedDataFolderName+ '\\'+FilePrefix+'_{}_{}_{}.txt'.format(X,Y,Z)
        np.savetxt(FileName, Data)
        print('\nData saved\n')

    def SaveParameters(self, Dict):
        f=open(ParametersFileName,'w')
        json.dump(Dict,f)
        f.close()
        print('\nParameters saved\n')

    def LoadParameters(self):
        f=open(ParametersFileName)
        dictionary=json.load(f)
        f.close()
        return dictionary
    
    def save_zero_position(self,X:int,Y:int,Z:int):
        Dict={}
        Dict['X']=str(X)
        Dict['Y']=str(Y)
        Dict['Z']=str(Z)
        f=open(ZeroPositionFileName,'w')
        json.dump(Dict,f)
        f.close()
        print('\nzero position saved\n')
        
    def load_zero_position(self):
        f=open(ZeroPositionFileName)
        dictionary=json.load(f)
        f.close()
        return dictionary['X'],dictionary['Y'],dictionary['Z']




if __name__ == "__main__":
    logger = Logger()
    logger.savePosition(10,323,0,'54')
    logger.savePosition(10,423,40,'545')
    del logger