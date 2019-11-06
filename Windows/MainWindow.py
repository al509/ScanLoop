# -*- coding: utf-8 -*-
"""
Version Oct 18 2019
@author: Ilya
"""

import numpy as np
import os
import time
#
#from Analyzer.SpectrumAnalyzer import SpectrumAnalyzer
#import Analyzer.PrecisePeakSearchers as pps
#import Analyzer.RudePeaksSearchers as rps
if __name__ is "__main__":
    os.chdir('..')

from PyQt5.QtCore import pyqtSignal, QThread, QState, QStateMachine, QObject
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QPushButton
from PyQt5 import QtCore

from Common.Consts import Consts
from Hardware.Config import Config
from Hardware.Interrogator import Interrogator
from Hardware.YokogawaOSA import OSA_AQ6370
from Hardware.KeysightOscilloscope import Scope
from Hardware.MyStanda import *
from Hardware.APEX_OSA import APEX_OSA_with_additional_features
from Logger.Logger import Logger
from Visualization.Painter import MyPainter
from Utils.PyQtUtils import pyqtSlotWExceptions
from Windows.UIs.MainWindowUI import Ui_MainWindow


def isfloat(value):
    try:
        float(value)
        return True
    except ValueError:
        return False

class ThreadedMainWindow(QMainWindow):

    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)

        # Handle threads
        self.threads = []
        self.destroyed.connect(self.kill_threads)
        self.stages=None
        self.interrogator=None

    def add_thread(self, objects):
        """
        Creates thread, adds it into to-destroy list and moves objects to it. Thread is QThread there.
        :param objects -- list of QObjects.
        :return None
        """
        # Create new thread
        thread = QThread()

        # Add new thread to list of threads to close on app destroy.
        self.threads.append(thread)

        # Move objects to new thread.
        for obj in objects:
            obj.moveToThread(thread)

        thread.start()
        return thread

    def kill_threads(self):
        """
        Closes all of created threads for this window.
        :return: None
        """
        # Iterate over all the threads and call wait() and quit().
        for thread in self.threads:
#            thread.wait()
            thread.quit()



class MainWindow(ThreadedMainWindow):
    force_OSA_acquireAll = pyqtSignal()
    force_OSA_acquire = pyqtSignal()
    force_stage_move = pyqtSignal(str,int)
    force_scope_acquire = pyqtSignal()
    force_scanning_process=pyqtSignal()


    def __init__(self, parent=None):
        super().__init__(parent)
        # GUI
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("Scanning spectra")
        self.logger = Logger(parent=None)
        self.add_thread([self.logger])
        self.ui.pushButton_StagesConnect.pressed.connect(self.ConnectStages)
        self.ui.pushButton_OSA_connect.pressed.connect(self.ConnectOSA)

        self.ui.pushButton_ProcessData.pressed.connect(self.on_Push_Button_ProcessSpectra)
        self.ui.pushButton_ProcessDataWithAveraging.pressed.connect(self.on_Push_Button_ProcessSpectraWithAveraging)
        self.ui.pushButton_OSA_Acquire.pressed.connect(self.on_pushButton_acquireSpectrum_pressed)
        self.ui.pushButton_save_data.pressed.connect(self.on_pushButton_save_data)
        self.ui.pushButton_OSA_AcquireAll.pressed.connect(self.on_pushButton_AcquireAllSpectra_pressed)
        self.ui.pushButton_OSA_AcquireRep.clicked[bool].connect(self.on_pushButton_acquireSpectrumRep_pressed)
        self.ui.pushButton_OSA_AcquireRepAll.clicked[bool].connect(self.on_pushButton_AcquireAllSpectraRep_pressed)


        self.ui.pushButton_scope_single.pressed.connect(self.on_pushButton_scope_single_measurement_pressed)
        self.ui.pushButton_scope_connect.pressed.connect(self.connectScope)
        self.ui.pushButton_scope_repeat.clicked[bool].connect(self.on_pushButton_scope_repeat__pressed)

        self.ui.CheckBox_FreezeSpectrum.stateChanged.connect(self.on_stateChangeOfFreezeSpectrumBox)
        self.ui.CheckBox_ApplyFFTFilter.stateChanged.connect(self.on_stateChangeOfApplyFFTBox)
        self.ui.checkBox_HighRes.stateChanged.connect(self.on_stateChangeOfIsHighResolution)
        self.ui.pushButton_getRange.pressed.connect(self.on_pushButton_getRange)
        self.painter = MyPainter(self.ui.groupBox_spectrum)
        self.add_thread([self.painter])

        self.ui.EditLine_StartWavelength.textChanged[str].connect(lambda S: self.OSA.change_range(start_wavelength=float(S)) if (isfloat(S) and float(S)>1500 and float(S)<1600) else 0)
    #        self.ui.EditLine_StartWavelength.textChanged[str].connect(lambda Str:print(Str))
        self.ui.EditLine_StopWavelength.textChanged[str].connect(lambda S: self.OSA.change_range(stop_wavelength=float(S)) if (isfloat(S) and float(S)>1500 and float(S)<1600) else 0)
        self.ui.pushButton_SaveParameters.pressed.connect(self.SaveParametersToFile)
        self.ui.pushButton_LoadParameters.pressed.connect(self.LoadParametersFromFile)
        self.ui.tabWidget_instruments.currentChanged.connect(self.on_TabChanged_instruments_changed)
        
        self.X_0,self.Y_0,self.Z_0=[0,0,0]


    def connectScope(self):
        self.scope=Scope(Consts.Scope.HOST)
        self.add_thread([self.scope])
#        self.force_scope_acquire.connect(self.scope.acquire)
        self.scope.received_data.connect(self.painter.set_data)
        #        self.ui.pushButton_scope_repeat.clicked[bool].connect(self.on_pushButton_scope_repeat__pressed)
        self.ui.tabWidget_instruments.setEnabled(True)
        self.ui.tabWidget_instruments.setCurrentIndex(1)
        self.ui.groupBox_scope_control.setEnabled(True)
        self.EnableScanningProcess()
        
        widgets = (self.ui.horizontalLayout_3.itemAt(i).widget() for i in range(self.ui.horizontalLayout_3.count())) 
        for i,widget in enumerate(widgets):
            widget.setChecked(self.scope.channels_states[i])
            widget.stateChanged.connect(self.update_scope_channel_state)
#            print("checkBox: %s  - %s" %(widget.objectName(), widget.checkState()))
        
        print('Connected to scope')
        
    def update_scope_channel_state(self):
        widgets = (self.ui.horizontalLayout_3.itemAt(i).widget() for i in range(self.ui.horizontalLayout_3.count())) 
        for i,widget in enumerate(widgets):
            self.scope.channels_states[i]=widget.isChecked()
            self.scope.set_channel_state(i+1,widget.isChecked())



    def ConnectOSA(self):
        if self.ui.comboBox_Type_of_OSA.currentText()=='Yokogawa':
            HOST = Consts.Interrogator.HOST
            PORT = 10001
            timeout_short = 0.2
            timeout_long = 100
            self.OSA=OSA_AQ6370(None,HOST, PORT, timeout_long,timeout_short)
#            self.OSA.received_spectra.connect(self.painter.set_spectra)



        elif self.ui.comboBox_Type_of_OSA.currentText()=='Astro interrogator':
            cfg = Config("config_interrogator.json")
            self.repeatmode=False
            self.OSA = Interrogator(
                parent=None,
                host=Consts.Interrogator.HOST,
                command_port=Consts.Interrogator.COMMAND_PORT,
                data_port=Consts.Interrogator.DATA_PORT,
                short_timeout=Consts.Interrogator.SHORT_TIMEOUT,
                long_timeout=Consts.Interrogator.LONG_TIMEOUT,
                config=cfg.config["channels"])

#            self.OSA.set_config(cfg.config["channels"])
            self.ui.comboBox_interrogatorChannel.currentIndexChanged.connect(self.OSA.set_channel_num)
            self.ui.comboBox_interrogatorChannel.setEnabled(True)
            self.ui.pushButton_OSA_AcquireRepAll.setEnabled(True)
            self.ui.pushButton_OSA_AcquireAll.setEnabled(True)
#            self.ui.comboBox_interrogatorChannel.currentIndexChanged.connect(self.painter.set_color)
#            self.OSA.renew_config.connect(self.painter.set_config)


        elif self.ui.comboBox_Type_of_OSA.currentText()=='ApEx':
            self.OSA = APEX_OSA_with_additional_features(Consts.APEX.HOST)
            self.ui.checkBox_HighRes.setChecked(self.OSA.IsHighRes)
        self.add_thread([self.OSA])
#        self.OSA.received_spectra.connect(self.painter.set_spectra)
        self.OSA.received_spectrum.connect(self.painter.set_data)
            # self.interrogator.received_wavelengths.connect(self.painter.set_wavelengths)
#            self.force_OSA_acquireAll.connect(self.OSA.acquire_spectra)
       
        self.force_OSA_acquire.connect(self.OSA.acquire_spectrum)
        self.ui.tabWidget_instruments.setEnabled(True)
        self.ui.tabWidget_instruments.setCurrentIndex(0)
#        self.ui.pushButton_OSA_connect.setEnabled(False)
        self.ui.EditLine_StartWavelength.setText(str(self.OSA._StartWavelength))
        self.ui.EditLine_StopWavelength.setText(str(self.OSA._StopWavelength))
    
        self.ui.groupBox_OSA_control.setEnabled(True)
        print('Connected with OSA')
        self.on_pushButton_acquireSpectrum_pressed()
        self.EnableScanningProcess()

    def ConnectStages(self):
        self.stages=Stages()
        if self.stages.IsConnected>0:
            print('Connected to stages')
            self.add_thread([self.stages])
            self.X_0,self.Y_0,self.Z_0=self.logger.load_zero_position()
            self.UpdatePositions()
            self.ui.pushButton_MovePlusX.pressed.connect(lambda :self.SetStageMoving('X',int(self.ui.lineEdit_StepX.text())))
            self.ui.pushButton_MoveMinusX.pressed.connect(lambda :self.SetStageMoving('X',-1*int(self.ui.lineEdit_StepX.text())))
            self.ui.pushButton_MovePlusY.pressed.connect(lambda :self.SetStageMoving('Y',int(self.ui.lineEdit_StepY.text())))
            self.ui.pushButton_MoveMinusY.pressed.connect(lambda :self.SetStageMoving('Y',-1*int(self.ui.lineEdit_StepY.text())))
            self.ui.pushButton_MovePlusZ.pressed.connect(lambda :self.SetStageMoving('Z',int(self.ui.lineEdit_StepZ.text())))
            self.ui.pushButton_MoveMinusZ.pressed.connect(lambda :self.SetStageMoving('Z',-1*int(self.ui.lineEdit_StepZ.text())))
            self.ui.pushButton_ZeroingPositions.pressed.connect(self.ZeroingPosition)
            self.force_stage_move[str,int].connect(lambda S,i:self.stages.shiftOnArbitrary(S,i))
            self.stages.stopped.connect(self.UpdatePositions)
            self.ui.groupBox_stand.setEnabled(True)
            self.ui.pushButton_StagesConnect.setEnabled(False)
            
            self.EnableScanningProcess()


    @pyqtSlotWExceptions()
    def EnableScanningProcess(self):
        if (self.ui.groupBox_stand.isEnabled() and self.ui.tabWidget_instruments.isEnabled()):
            self.ui.groupBox_Scanning.setEnabled(True)
            self.ui.pushButton_Scanning.clicked[bool].connect(self.on_pushButton_Scanning_pressed)
            self.ui.toolBox.setCurrentIndex(1)


    @pyqtSlotWExceptions()
    def on_equipment_ready(self, is_ready):
        self.ui.groupBox_theExperiment.setEnabled(is_ready)


    def SetStageMoving(self,key,step):
        self.force_stage_move.emit(key,step)

    @pyqtSlotWExceptions("PyQt_PyObject")
    def UpdatePositions(self):
        X_abs=(self.stages.position['X'])
        Y_abs=(self.stages.position['Y'])
        Z_abs=(self.stages.position['Z'])
        
        self.ui.label_PositionX.setText(str(X_abs-self.X_0))
        self.ui.label_PositionY.setText(str(Y_abs-self.Y_0))
        self.ui.label_PositionZ.setText(str(Z_abs-self.Z_0))

        self.ui.label_AbsPositionX.setText(str(X_abs))
        self.ui.label_AbsPositionY.setText(str(Y_abs))
        self.ui.label_AbsPositionZ.setText(str(Z_abs))
        
        
        
    def ZeroingPosition(self):
        self.X_0=(self.stages.position['X'])
        self.Y_0=(self.stages.position['Y'])
        self.Z_0=(self.stages.position['Z'])
        self.logger.save_zero_position(self.X_0,self.Y_0,self.Z_0)
        self.UpdatePositions()
    
    def on_pushButton_scope_single_measurement_pressed(self):
        self.scope.acquire()

    def on_pushButton_scope_repeat__pressed(self,pressed):
        if pressed:
            self.painter.ReplotEnded.connect(self.scope.acquire)
            self.ui.pushButton_scope_single.setEnabled(False)
            self.ui.pushButton_Scanning.setEnabled(False)
            self.scope.acquire()
        else:
            self.painter.ReplotEnded.disconnect(self.scope.acquire)
#            self.painter.ReplotEnded.disconnect(self.force_scope_acquire)
            self.ui.pushButton_OSA_AcquireRepAll.setEnabled(True)
            self.ui.pushButton_scope_single.setEnabled(True)
            self.ui.pushButton_OSA_AcquireAll.setEnabled(True)
            self.ui.pushButton_Scanning.setEnabled(True)
    
    @pyqtSlotWExceptions()
    def on_pushButton_AcquireAllSpectra_pressed(self):
        self.force_OSA_acquireAll.emit()

    @pyqtSlotWExceptions()
    def on_pushButton_acquireSpectrum_pressed(self):
        self.force_OSA_acquire.emit()


    @pyqtSlotWExceptions()
    def on_pushButton_acquireSpectrumRep_pressed(self,pressed):
        if pressed:
            self.painter.ReplotEnded.connect(self.force_OSA_acquire)
            self.ui.pushButton_OSA_AcquireRepAll.setEnabled(False)
            self.ui.pushButton_OSA_Acquire.setEnabled(False)
            self.ui.pushButton_OSA_AcquireAll.setEnabled(False)
            self.ui.pushButton_Scanning.setEnabled(False)
            self.force_OSA_acquire.emit()
        else:
            self.painter.ReplotEnded.disconnect(self.force_OSA_acquire)
            self.ui.pushButton_OSA_AcquireRepAll.setEnabled(True)
            self.ui.pushButton_OSA_Acquire.setEnabled(True)
            self.ui.pushButton_OSA_AcquireAll.setEnabled(True)
            self.ui.pushButton_Scanning.setEnabled(True)


    @pyqtSlotWExceptions()
    def on_pushButton_AcquireAllSpectraRep_pressed(self,pressed):
        if pressed:

            self.painter.ReplotEnded.connect(self.on_pushButton_AcquireAllSpectra_pressed)
            self.ui.pushButton_OSA_AcquireAll.setEnabled(False)
            self.ui.pushButton_OSA_Acquire.setEnabled(False)
            self.ui.pushButton_OSA_AcquireRep.setEnabled(False)
            self.ui.pushButton_Scanning.setEnabled(False)
            self.force_OSA_acquireAll.emit()

        else:

            self.painter.ReplotEnded.disconnect(self.on_pushButton_AcquireAllSpectra_pressed)
            self.ui.pushButton_OSA_AcquireAll.setEnabled(True)
            self.ui.pushButton_OSA_Acquire.setEnabled(True)
            self.ui.pushButton_OSA_AcquireRep.setEnabled(True)
            self.ui.pushButton_Scanning.setEnabled(True)


    def on_pushButton_Scanning_pressed(self,pressed:bool):
        if pressed and  self.ui.tabWidget_instruments.currentIndex()==0: ## if OSA is active
            from Scripts.ScanningProcessOSA import ScanningProcess
            self.scanningProcess=ScanningProcess(OSA=self.OSA,Stages=self.stages,
                                                 scanstep=int(self.ui.lineEdit_ScanningStep.text()),
                                                 seekcontactstep=int(self.ui.lineEdit_SearchingStep.text()),
                                                 backstep=int(self.ui.lineEdit_BackStep.text()),
                                                 seekcontactvalue=float(self.ui.lineEdit_LevelToDetectContact.text()),
                                                 ScanningType=int(self.ui.comboBox_ScanningType.currentIndex()),
                                                 SqueezeSpanWhileSearchingContact=self.ui.checkBox_SqueezeSpan.isChecked(),
                                                 CurrentFileIndex=int(self.ui.lineEdit_CurrentFile.text()),
                                                 StopFileIndex=int(self.ui.lineEdit_StopFile.text()),
                                                 numberofscans=int(self.ui.lineEdit_numberOfScans.text()))
            self.add_thread([self.scanningProcess])
            self.scanningProcess.S_updateCurrentFileName.connect(lambda S: self.ui.lineEdit_CurrentFile.setText(S))
            self.scanningProcess.S_saveSpectrum.connect(lambda Data,FilePrefix: self.logger.save_data(Data,'Sp_'+FilePrefix, self.stages.positin['X'],
                                                                                                      self.stages.position['Y'],self.stages.posiiton['Z']))
            self.scanningProcess.S_saveSpectrumToOSA.connect(lambda FilePrefix: self.OSA.SaveToFile('D:'+'Spec_Ch'+str(self.OSA.channel_num)+'_'+FilePrefix, TraceNumber=1, Type="txt"))
            self.scanningProcess.S_addPosition_and_FilePrefix.connect(self.addPositionToPositionList)
            self.scanningProcess.S_finished.connect(self.ui.pushButton_Scanning.toggle)
            self.scanningProcess.S_finished.connect(lambda : self.on_pushButton_Scanning_pressed(False))
            self.logger.open_file()
            self.ui.groupBox_OSA_control.setEnabled(False)
            self.ui.groupBox_stand.setEnabled(False)
            self.force_scanning_process.connect(self.scanningProcess.run)
            print('Start Scanning')
            self.force_scanning_process.emit()
        
        elif pressed and  self.ui.tabWidget_instruments.currentIndex()==1: ## if scope is active
            from Scripts.ScanningProcessScope import ScanningProcess
            self.scanningProcess=ScanningProcess(Scope=self.scope,Stages=self.stages,
                                                 scanstep=int(self.ui.lineEdit_ScanningStep.text()),
                                                 seekcontactstep=int(self.ui.lineEdit_SearchingStep.text()),
                                                 backstep=int(self.ui.lineEdit_BackStep.text()),
                                                 seekcontactvalue=float(self.ui.lineEdit_LevelToDetectContact.text()),
                                                 ScanningType=int(self.ui.comboBox_ScanningType.currentIndex()),
                                                 CurrentFileIndex=int(self.ui.lineEdit_CurrentFile.text()),
                                                 StopFileIndex=int(self.ui.lineEdit_StopFile.text()),
                                                 numberofscans=int(self.ui.lineEdit_numberOfScans.text()))
            self.add_thread([self.scanningProcess])
            self.scanningProcess.S_updateCurrentFileName.connect(lambda S: self.ui.lineEdit_CurrentFile.setText(S))
            self.scanningProcess.S_saveTimeTraces.connect(lambda Data,FilePrefix: self.logger.SaveData(Data,'TimeTraces_'+FilePrefix+'.txt'))
            self.scanningProcess.S_addPosition_and_FilePrefix.connect(self.addPositionToPositionList)
            self.scanningProcess.S_finished.connect(self.ui.pushButton_Scanning.toggle)
            self.scanningProcess.S_finished.connect(lambda : self.on_pushButton_Scanning_pressed(False))
            self.logger.open_file()
            self.ui.groupBox_scope_control.setEnabled(False)
            self.ui.groupBox_stand.setEnabled(False)
            self.force_scanning_process.connect(self.scanningProcess.run)
            print('Start Scanning')
            self.force_scanning_process.emit()
        else:
            self.scanningProcess.is_running=False
            del self.scanningProcess
            self.ui.groupBox_OSA_control.setEnabled(True)
            self.ui.groupBox_scope_control.setEnabled(True)
            self.ui.groupBox_stand.setEnabled(True)
            self.logger.close_file()


    def on_pushButton_save_data(self):
        if self.stages is not None:
            X=self.stages.position['X']-self.X_0
            Y=self.stages.position['Y']-self.Y_0
            Z=self.stages.position['Z']-self.Z_0
        else:
            X,Y,Z=[0,0,0]
        
        Ydata=self.painter.Ydata
        Data=self.painter.Xdata
        for YDataColumn in Ydata:
            if YDataColumn is not None:
                Data=np.column_stack((Data, YDataColumn))
        if self.painter.TypeOfData=='FromOSA':
            FilePrefix='Sp_'+self.ui.EditLine_saveSpectrumName.text()
            if self.OSA.IsHighRes:
                self.OSA.SaveToFile('D:'+self.ui.EditLine_saveSpectrumName.text(),TraceNumber=1, Type="txt")
        elif self.painter.TypeOfData=='FromScope':
            FilePrefix='TD_'+self.ui.EditLine_saveSpectrumName.text()
        self.logger.save_data(Data,FilePrefix,X,Y,Z)
        

    def on_pushButton_getRange(self):
        Range=(self.painter.ax.get_xlim())
        self.ui.EditLine_StartWavelength.setText(f'{Range[0]}:.1f')
        self.ui.EditLine_StopWavelength.setText(f'{Range[1]}:.1f')
        try:
            self.OSA.change_range(start_wavelength=float(Range[0]),stop_wavelength=float(Range[1]))
            print('Range is taken')
        except:
            print('Error while taking range')
            
#    def ChangeRange(self,Minimum=None,Maximum=None):
#        if Minimum is not None:
#            self.OSA.set_range(start_wavelength=float(Minimum))
#        if Maximum is not None:
#            self.OSA.set_range(stop_wavelength=float(Maximum))


    def on_stateChangeOfFreezeSpectrumBox(self):
        if self.ui.CheckBox_FreezeSpectrum.isChecked():
            self.painter.savedY=list(self.painter.Ydata)
            self.painter.savedX=list(self.painter.Xdata)
        else:
            self.painter.savedY=[None]*8

    def on_stateChangeOfApplyFFTBox(self):
        if self.ui.CheckBox_ApplyFFTFilter.isChecked():
            self.painter.ApplyFFTFilter=True
            self.painter.FilterLowFreqEdge=float(self.ui.EditLine_FilterLowFreqEdge.text())
            self.painter.FilterHighFreqEdge=float(self.ui.EditLine_FilterHighFreqEdge.text())
            self.painter.FFTPointsToCut=int(self.ui.EditLine_FilterPointsToCut.text())
        else:
            self.painter.ApplyFFTFilter=False

    def on_stateChangeOfIsHighResolution(self):
        if self.ui.checkBox_HighRes.isChecked():
            self.OSA.SetWavelengthResolution('High')
        else:
            self.OSA.SetWavelengthResolution('Low')

    def on_TabChanged_instruments_changed(self,i):
        if i==0:
            self.painter.TypeOfData='FromOSA'
        elif i==1:
            self.painter.TypeOfData='FromScope'



    def on_Push_Button_ProcessSpectra(self):
        from Scripts.ProcessAndPlotSpectra import ProcessSpectra
        self.ProcessSpectra=ProcessSpectra()
        Thread=self.add_thread([self.ProcessSpectra])
        self.ProcessSpectra.run(StepSize=float(self.ui.lineEdit_ScanningStep.text()),HighFreqEdge=0.01,
                                IsHighRes=self.ui.checkBox_HighRes.isChecked(),DoesSpanVary=self.ui.checkBox_DoesSpanVary.isChecked())
        Thread.quit()

    def on_Push_Button_ProcessSpectraWithAveraging(self):
        from Scripts.ProcessAndPlotSpectraWithAveraging import ProcessSpectraWithAveraging
        self.ProcessSpectra=ProcessSpectraWithAveraging()
        Thread=self.add_thread([self.ProcessSpectra])
        self.ProcessSpectra.run(StepSize=float(self.ui.lineEdit_ScanningStep.text()),Averaging=self.ui.checkBox_IsAveragingWhileProcessing.isChecked())
        Thread.quit()


    def SaveParametersToFile(self):
        Dict={}
        Dict['saveSpectrumName']=(self.ui.EditLine_saveSpectrumName.text())
        Dict['StartWavelength']=float(self.ui.EditLine_StartWavelength.text())
        Dict['StopWavelength']=float(self.ui.EditLine_StopWavelength.text())
        Dict['StepX']=int(self.ui.lineEdit_StepX.text())
        Dict['StepY']=int(self.ui.lineEdit_StepY.text())
        Dict['StepZ']=int(self.ui.lineEdit_StepZ.text())
        Dict['channel_num']=int(self.ui.comboBox_interrogatorChannel.currentIndex())
        Dict['Scanning_type']=int(self.ui.comboBox_ScanningType.currentIndex())
        Dict['ScanningStep']=int(self.ui.lineEdit_ScanningStep.text())
        Dict['SearchingStep']=int(self.ui.lineEdit_SearchingStep.text())
        Dict['BackStep']=int(self.ui.lineEdit_BackStep.text())
        Dict['LevelToDetectContact']=float(self.ui.lineEdit_LevelToDetectContact.text())
        Dict['CurrentFile']=int(self.ui.lineEdit_CurrentFile.text())
        Dict['StopFile']=int(self.ui.lineEdit_StopFile.text())
        Dict['FFTPointsToCut']=int(self.ui.EditLine_FilterPointsToCut.text())
        Dict['FFTLowerEdge']=float(self.ui.EditLine_FilterLowFreqEdge.text())
        Dict['FFTHigherEdge']=float(self.ui.EditLine_FilterHighFreqEdge.text())
        Dict['ApplyFFT']=str(self.ui.CheckBox_ApplyFFTFilter.isChecked())
        Dict['SqueezeSpan?']=str(self.ui.checkBox_SqueezeSpan.isChecked())
        Dict['NumberOfScans']=int(self.ui.lineEdit_numberOfScans.text())
        Dict['IsHighRes']=str(self.ui.checkBox_HighRes.isChecked())
        self.logger.SaveParameters(Dict)

    def LoadParametersFromFile(self):
        Dict=self.logger.LoadParameters()
        self.ui.EditLine_saveSpectrumName.setText(str(Dict['saveSpectrumName']))
        self.ui.EditLine_StartWavelength.setText('{:.5f}'.format(Dict['StartWavelength']))
        self.ui.EditLine_StopWavelength.setText('{:.5f}'.format(Dict['StopWavelength']))
        
        if Dict['IsHighRes']=='True':
            self.ui.checkBox_HighRes.setChecked(True)
            self.OSA.SetWavelengthResolution('High')
        else:
            self.ui.checkBox_HighRes.setChecked(False)
            self.OSA.SetWavelengthResolution('Low')
      
        self.OSA.change_range(float(Dict['StartWavelength']), float(Dict['StopWavelength']))
        self.ui.lineEdit_StepX.setText(str(Dict['StepX']))
        self.ui.lineEdit_StepY.setText(str(Dict['StepY']))
        self.ui.lineEdit_StepZ.setText(str(Dict['StepZ']))
        self.ui.comboBox_interrogatorChannel.setCurrentIndex(int(Dict['channel_num']))
        self.ui.comboBox_ScanningType.setCurrentIndex(int(Dict['Scanning_type']))
        self.ui.lineEdit_ScanningStep.setText(str(Dict['ScanningStep']))
        self.ui.lineEdit_SearchingStep.setText(str(Dict['SearchingStep']))
        self.ui.lineEdit_BackStep.setText(str(Dict['BackStep']))
        self.ui.lineEdit_LevelToDetectContact.setText(str(Dict['LevelToDetectContact']))
        self.ui.lineEdit_CurrentFile.setText(str(Dict['CurrentFile']))
        self.ui.lineEdit_StopFile.setText(str(Dict['StopFile']))
        self.ui.EditLine_FilterPointsToCut.setText(str(Dict['FFTPointsToCut']))
        self.ui.EditLine_FilterLowFreqEdge.setText(str(Dict['FFTLowerEdge']))
        self.ui.EditLine_FilterHighFreqEdge.setText(str(Dict['FFTHigherEdge']))
        self.ui.CheckBox_ApplyFFTFilter.setChecked(Dict['ApplyFFT']=='True')
        self.ui.checkBox_SqueezeSpan.setChecked(Dict['SqueezeSpan?']=='True')
        self.ui.lineEdit_numberOfScans.setText(str(Dict['NumberOfScans']))
        self.force_OSA_acquire.emit()
        print('Parameters loaded')

    def closeEvent(self, event):
#         here you can terminate your threads and do other stuff
        print('Deleting everything...')
        try:
            del self.stages
            print('Stages object is deleted')
            del self.OSA
            print('OSA object is deleted')
            del self.painter
            print('Painter object is deleted')
            del self.scanningProcess
            del self.ProcessSpectra
            del self.logger
        except:
            print('exception while closing')
        super(QMainWindow, self).closeEvent(event)
#
if __name__ == "__main__":
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
