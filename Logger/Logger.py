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
    PositionsFileName='Positions.txt'
    SavedDataFolderName='SavedData'

    def __init__(self, parent=None):
        super().__init__(parent)

        self.counter = 0
        self.spectra = None
        self.wavelengths = None
        self.positions = list()
        self.file=None


        self.logs_path = Consts.Logger.LOGS_PATH
        if not os.path.exists(self.logs_path):
            os.makedirs(self.logs_path)
        if not os.path.exists(self.logs_path + "sensor_data.log"):
            f = QFile(self.logs_path + "sensor_data.log")
            f.open(QIODevice.WriteOnly | QIODevice.Append)
            f.write("Номер измерения, дата+время, позиция энкодера, канал 1:длина волны решетки 1, ... \r\n".encode())
            f.close()

    @pyqtSlotWExceptions(object)
    def add_position(self, position: int) -> None:
        self.position = position
        self.save()

    @pyqtSlotWExceptions(object)
    def add_wavelengths(self, wavelengths: list) -> None:
        self.wavelengths = wavelengths
        self.save()

    @pyqtSlotWExceptions(object)
    def add_spectra(self, spectra: np.array) -> None:
        self.spectra = spectra
        self.save()

    def save(self):
        if self.spectra is None:
            return
        if self.wavelengths is None:
            return
        if self.position is None:
            return

        self.counter += 1

        print(time.time() - self.t)
        self.t = time.time()

        np.save(
            "{0}{1:08} {2}".format(
                self.logs_path,
                self.counter,
                datetime.datetime.now().strftime("%y-%m-%d %H-%M-%S")),
            self.spectra)

        wls = []
        for channel_num in range(len(self.wavelengths)):
            if self.wavelengths[channel_num] is None:
                continue
            for wl in self.wavelengths[channel_num]:
                wls += ["{0}:{1}".format(channel_num, wl)]
        d = "{0},{1},{2},{3}\r\n".format(
            self.counter,
            datetime.datetime.now().strftime("%y-%m-%d %H-%M-%S"),
            self.position,
            ",".join(wls))

        f = QFile(self.logs_path + "sensor_data.log")
        f.open(QIODevice.WriteOnly | QIODevice.Append)
        f.write(d.encode())
        f.close()

        self.spectra = None
        self.wavelengths = None
        self.position = None

        self.updated.emit()

    def SaveData(self, Data,FileName):
        FileName=self.SavedDataFolderName+ '\\'+FileName
        np.savetxt(FileName, Data)
        print('\nData saved\n')

    def SaveParameters(self, Dict):
        json.dump(Dict,open('Parameters.txt','w'))
        print('\nParameters saved\n')

    def LoadParameters(self):
        dictionary=json.load(open('Parameters.txt'))
        return dictionary

    def addPosition(self,X,Y,Z,string):
        self.positions.append([X,Y,Z,string])

    def savePosition(self,X,Y,Z,FileName):
#        json.dump([X,Y,Z,string],open('Positions.txt','a'))
        self.file.write(str(X)+' ' +str(Y)+' ' +str(Z)+' ' +FileName+'\n')

    def savePosition_single(self,X,Y,Z,FileName):
#        json.dump([X,Y,Z,string],open('Positions.txt','a'))
        self.open_file()
        self.file.write(str(X)+' ' +str(Y)+' ' +str(Z)+' ' +FileName+'\n')
        self.close_file()


    def open_file(self):
        if not self.file:
            self.file=open(self.PositionsFileName,'a')

    def close_file(self):
        if self.file:
            self.file=open(self.PositionsFileName,'a')


if __name__ == "__main__":
    logger = Logger()
    logger.savePosition(10,323,0,'54')
    logger.savePosition(10,423,40,'545')
    del logger