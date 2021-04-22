# -*- coding: utf-8 -*-


import os
import numpy as np

from PyQt5.QtCore import pyqtSignal, QThread
from PyQt5.QtWidgets import QMainWindow, QFileDialog

from Common.Consts import Consts
from Hardware.Config import Config
from Hardware.Interrogator import Interrogator
from Hardware.YokogawaOSA import OSA_AQ6370
from Hardware.ova5000 import Luna
from Hardware.KeysightOscilloscope import Scope
from Hardware.APEX_OSA import APEX_OSA_with_additional_features
from Logger.Logger import Logger
from Visualization.Painter import MyPainter
from Utils.PyQtUtils import pyqtSlotWExceptions
from Windows.UIs.MainWindowUI import Ui_MainWindow
from Scripts import AnalyzerForSpectrogram
from Scripts import ProcessAndPlotSpectra


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
        self.OSA=None
        self.scope=None
        self.laser=None

    def add_thread(self, objects):
        """
        Creates thread, adds it into to-destroy list and moves objects to it.
        Thread is QThread there.
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
    force_laser_scanning_process=pyqtSignal()
    force_laser_sweeping_process=pyqtSignal()
    '''
    Initialization
    '''
    def __init__(self, parent=None,version='0.0'):
        super().__init__(parent)
        self.path_to_main=os.getcwd()
        # GUI
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("ScanLoop V."+version)

        self.ui.tabWidget_instruments.currentChanged.connect(self.on_TabChanged_instruments_changed)


# =============================================================================
#         Stages interface
# =============================================================================
        self.ui.pushButton_StagesConnect.pressed.connect(self.connectStages)
        self.X_0,self.Y_0,self.Z_0=[0,0,0]

# =============================================================================
#         # OSA interface
# =============================================================================
        self.ui.pushButton_OSA_connect.pressed.connect(self.connectOSA)
        self.ui.pushButton_OSA_Acquire.pressed.connect(
            self.on_pushButton_acquireSpectrum_pressed)
        self.ui.pushButton_OSA_AcquireAll.pressed.connect(
            self.on_pushButton_AcquireAllSpectra_pressed)
        self.ui.pushButton_OSA_AcquireRep.clicked[bool].connect(
            self.on_pushButton_acquireSpectrumRep_pressed)
        self.ui.comboBox_APEX_mode.currentIndexChanged[int].connect(
            lambda x: self.OSA.SetMode(x+3))

# =============================================================================
#         # scope interface
# =============================================================================
        self.ui.pushButton_scope_connect.pressed.connect(self.connectScope)
        self.ui.pushButton_scope_single.pressed.connect(
            self.on_pushButton_scope_single_measurement_pressed)
        self.ui.pushButton_scope_repeat.clicked[bool].connect(
            self.on_pushButton_scope_repeat__pressed)

# =============================================================================
#         # painter and drawing interface
# =============================================================================
        self.painter = MyPainter(self.ui.groupBox_spectrum)
        self.add_thread([self.painter])
        self.ui.CheckBox_FreezeSpectrum.stateChanged.connect(self.on_stateChangeOfFreezeSpectrumBox)
        self.ui.CheckBox_ApplyFFTFilter.stateChanged.connect(self.on_stateChangeOfApplyFFTBox)
        self.ui.checkBox_HighRes.stateChanged.connect(self.on_stateChangeOfIsHighResolution)
        self.ui.pushButton_getRange.pressed.connect(self.on_pushButton_getRange)
        self.ui.EditLine_StartWavelength.textChanged[str].connect(
            lambda S: self.OSA.change_range(start_wavelength=float(S))
            if (isfloat(S) and float(S)>1500 and float(S)<1600) else 0)
        self.ui.EditLine_StopWavelength.textChanged[str].connect(
            lambda S: self.OSA.change_range(stop_wavelength=float(S))
            if (isfloat(S) and float(S)>1500 and float(S)<1600) else 0)

# =============================================================================
#         saving interface
# =============================================================================
        self.logger = Logger(parent=None)
        self.add_thread([self.logger])
        self.ui.pushButton_SaveParameters.pressed.connect(self.saveParametersToFile)
        self.ui.pushButton_LoadParameters.pressed.connect(self.loadParametersFromFile)
        self.ui.pushButton_save_data.pressed.connect(self.on_pushButton_save_data)

# =============================================================================
#         #scanning process
# =============================================================================
        self.ui.checkBox_searchContact.stateChanged.connect(self.on_stateSearchContact)
        self.ui.pushButton_Scanning.clicked[bool].connect(self.on_pushButton_Scanning_pressed)

# =============================================================================
#         # processing
# =============================================================================
        self.processSpectra=ProcessAndPlotSpectra.ProcessSpectra(self.path_to_main)
        self.add_thread([self.processSpectra])
        self.ui.pushButton_processSpectralData.pressed.connect(self.on_Push_Button_ProcessSpectra)
        self.ui.pushButton_processTDData.pressed.connect(self.on_Push_Button_ProcessTD)

# =============================================================================
#         # analyzer logic
# =============================================================================
        self.analyzer=AnalyzerForSpectrogram.AnalyzerForSpectrogram(
            os.getcwd()+'\\ProcessedData\\Processed_spectrogram.pkl')
        self.add_thread([self.analyzer])
        self.ui.pushButton_process_arb_spectral_data.clicked.connect(
            self.process_arb_spectral_data_clicked)
        self.ui.pushButton_process_arb_TD_data.clicked.connect(self.process_arb_TD_data_clicked)
        self.ui.pushButton_choose_folder_to_process.clicked.connect(self.choose_folder_to_process)
        self.ui.pushButton_plotSampleShape.clicked.connect(
            lambda: self.plotSampleShape(DirName='SpectralData',
            axis=self.ui.comboBox_axis_to_plot_along.currentText()))
        self.ui.pushButton_plotSampleShape_arb_data.clicked.connect(
            lambda: self.plotSampleShape(DirName=self.Folder,
            axis=self.ui.comboBox_axis_to_plot_along_arb_data.currentText()))
        self.ui.pushButton_analyzer_plot_single_spectrum_from_file.clicked.connect(
            self.plot_single_spectrum_from_file)
        self.ui.pushButton_analyzer_choose_file_spectrogram.clicked.connect(
            self.choose_folder_for_analyzer)
        self.ui.pushButton_analyzer_plotSampleShape.clicked.connect(
            self.analyzer.plot_sample_shape)
        self.ui.pushButton_analyzer_plot2D.clicked.connect(lambda: self.analyzer.plot2D())
        self.ui.pushButton_analyzer_plotSlice.clicked.connect(
            lambda: self.analyzer.plotSlice(float(self.ui.lineEdit_slice_position.text()),
            float(self.ui.lineEdit_analyzer_resonance_level.text()),
            self.ui.comboBox_axis_to_analyze_along_arb_data.currentText()))
        self.ui.pushButton_analyzer_extractERV.clicked.connect(
            lambda: self.analyzer.extractERV(
                float(self.ui.lineEdit_analyzer_resonance_level.text()),
            float(self.ui.lineEdit_analyzer_wavelength_min.text()),
            float(self.ui.lineEdit_analyzer_wavelength_max.text()),
            self.ui.comboBox_axis_to_analyze_along_arb_data.currentText()))
        self.ui.pushButton_analyzer_save_cropped_data.clicked.connect(
            self.analyzer.save_cropped_data)

# =============================================================================
#         Pure Photonics Tunable laser
# =============================================================================
        self.ui.pushButton_laser_connect.clicked.connect(self.connect_laser)
        self.ui.pushButton_laser_On.clicked[bool].connect(self.on_pushButton_laser_On)
        self.ui.comboBox_laser_mode.currentIndexChanged.connect(self.change_laser_mode)
        self.ui.lineEdit_laser_fine_tune.textChanged.connect(self.laser_fine_tuning)
        self.ui.pushButton_scan_laser_wavelength.clicked[bool].connect(self.laser_scanning)
        self.ui.pushButton_sweep_laser_wavelength.clicked[bool].connect(self.laser_sweeping)

    def connectScope(self):
        self.scope=Scope(Consts.Scope.HOST)
        self.add_thread([self.scope])
        self.scope.received_data.connect(self.painter.set_data)
        self.ui.tabWidget_instruments.setEnabled(True)
        self.ui.tabWidget_instruments.setCurrentIndex(1)
        self.ui.groupBox_scope_control.setEnabled(True)
        self.enableScanningProcess()
        widgets = (self.ui.horizontalLayout_3.itemAt(i).widget()
                   for i in range(self.ui.horizontalLayout_3.count()))
        for i,widget in enumerate(widgets):
            widget.setChecked(self.scope.channels_states[i])
            widget.stateChanged.connect(self.update_scope_channel_state)
        self.painter.TypeOfData='FromScope'
        print('Connected to scope')

    def update_scope_channel_state(self):
        widgets = (self.ui.horizontalLayout_3.itemAt(i).widget()
                   for i in range(self.ui.horizontalLayout_3.count()))
        for i,widget in enumerate(widgets):
            self.scope.channels_states[i]=widget.isChecked()
            self.scope.set_channel_state(i+1,widget.isChecked())



    def connectOSA(self):
        if self.ui.comboBox_Type_of_OSA.currentText()=='Luna':
            self.OSA=Luna()
        if self.ui.comboBox_Type_of_OSA.currentText()=='Yokogawa':
            HOST = Consts.Yokogawa.HOST
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

            self.ui.comboBox_interrogatorChannel.currentIndexChanged.connect(
                self.OSA.set_channel_num)
            self.ui.comboBox_interrogatorChannel.setEnabled(True)
            self.ui.pushButton_OSA_AcquireRepAll.setEnabled(True)
            self.ui.pushButton_OSA_AcquireAll.setEnabled(True)


        elif self.ui.comboBox_Type_of_OSA.currentText()=='APEX':
            self.OSA = APEX_OSA_with_additional_features(Consts.APEX.HOST)
            self.ui.checkBox_HighRes.setChecked(self.OSA.IsHighRes)
            self.ui.comboBox_APEX_mode.setEnabled(True)
            self.ui.comboBox_APEX_mode.setCurrentIndex(self.OSA.GetMode()-3)

        self.add_thread([self.OSA])
        self.OSA.received_spectrum.connect(self.painter.set_data)

        self.force_OSA_acquire.connect(self.OSA.acquire_spectrum)
        self.ui.tabWidget_instruments.setEnabled(True)
        self.ui.tabWidget_instruments.setCurrentIndex(0)
        self.ui.EditLine_StartWavelength.setText(str(self.OSA._StartWavelength))
        self.ui.EditLine_StopWavelength.setText(str(self.OSA._StopWavelength))

        self.ui.groupBox_OSA_control.setEnabled(True)
        print('Connected with OSA')
        self.on_pushButton_acquireSpectrum_pressed()
        self.enableScanningProcess()
        self.painter.TypeOfData='FromOSA'

    def connectStages(self):
        if self.ui.comboBox_Type_of_Stages.currentText()=='3x Standa':
            from Hardware.MyStanda import StandaStages
            self.stages=StandaStages()
        elif self.ui.comboBox_Type_of_Stages.currentText()=='2x Thorlabs':
            from Hardware.MyThorlabsStages import ThorlabsStages
            self.stages=ThorlabsStages()
            self.ui.pushButton_MovePlusY.setEnabled(False)
            self.ui.pushButton_MoveMinusY.setEnabled(False)

        if self.stages.IsConnected>0:
            print('Connected to stages')
            self.add_thread([self.stages])
            self.X_0,self.Y_0,self.Z_0=self.logger.load_zero_position()
            self.updatePositions()
            self.ui.pushButton_MovePlusX.pressed.connect(
                lambda :self.setStageMoving('X',int(self.ui.lineEdit_StepX.text())))
            self.ui.pushButton_MoveMinusX.pressed.connect(
                lambda :self.setStageMoving('X',-1*int(self.ui.lineEdit_StepX.text())))
            self.ui.pushButton_MovePlusY.pressed.connect(
                lambda :self.setStageMoving('Y',int(self.ui.lineEdit_StepY.text())))
            self.ui.pushButton_MoveMinusY.pressed.connect(
                lambda :self.setStageMoving('Y',-1*int(self.ui.lineEdit_StepY.text())))
            self.ui.pushButton_MovePlusZ.pressed.connect(
                lambda :self.setStageMoving('Z',int(self.ui.lineEdit_StepZ.text())))
            self.ui.pushButton_MoveMinusZ.pressed.connect(
                lambda :self.setStageMoving('Z',-1*int(self.ui.lineEdit_StepZ.text())))
            self.ui.pushButton_zeroingPositions.pressed.connect(self.zeroingPosition)
            self.force_stage_move[str,int].connect(lambda S,i:self.stages.shiftOnArbitrary(S,i))
            self.stages.stopped.connect(self.updatePositions)
            self.ui.groupBox_stand.setEnabled(True)
            self.ui.pushButton_StagesConnect.setEnabled(False)
            self.ui.pushButton_zeroing_stages.pressed.connect(
                self.on_pushBatton_pushButton_zeroing_stages)

            self.enableScanningProcess()

    def on_pushBatton_pushButton_zeroing_stages(self):
        self.stages.Stage_key['X'].move_home(True)
        self.stages.Stage_key['Z'].set_move_home_parameters(2, 1, 2.0, 0.0001)
        self.stages.Stage_key['Z'].move_home(False)

    def connect_laser(self):
        COMPort='COM'+self.ui.lineEdit_laser_COMport.text()
        try:
            from Hardware.PurePhotonicsLaser import Laser
            self.laser=Laser(COMPort)
            self.laser.fineTuning(0)
            print('Laser has been connected')
    #            self.add_thread([self.laser])
        except:
            print('Connection to laser failed. Check the COM port number')


    def on_pushButton_laser_On(self,pressed:bool):
        if pressed:
            self.ui.pushButton_scan_laser_wavelength.setEnabled(False)
            self.laser.setPower(float(self.ui.lineEdit_laser_power.text()))
            self.laser.setWavelength(float(self.ui.lineEdit_laser_lambda.text()))
            self.laser.setOn()
            self.ui.comboBox_laser_mode.setEnabled(True)
            self.ui.lineEdit_laser_fine_tune.setEnabled(True)
        else:
            self.laser.setOff()
            self.ui.pushButton_scan_laser_wavelength.setEnabled(True)
            self.ui.comboBox_laser_mode.setEnabled(False)
            self.ui.lineEdit_laser_fine_tune.setEnabled(False)

    def change_laser_mode(self):
        self.laser.setMode(self.ui.comboBox_laser_mode.currentText())

    def laser_fine_tuning(self):
        self.laser.fineTuning(float(self.ui.lineEdit_laser_fine_tune.text()))

    def laser_scanning(self,pressed:bool):
        if pressed:
            self.ui.pushButton_laser_On.setEnabled(False)
            from Scripts.ScanningProcessLaser import LaserScanningProcess
            self.laser_scanning_process=LaserScanningProcess(OSA=self.OSA,
                laser=self.laser, laser_power=float(self.ui.lineEdit_laser_power.text()),
                scanstep=float(self.ui.lineEdit_laser_lambda_scanning_step.text()),
                wavelength_start=float(self.ui.lineEdit_laser_lambda_scanning_min.text()),
                wavelength_stop=float(self.ui.lineEdit_laser_lambda_scanning_max.text()))
            self.laser_scanning_process.S_saveSpectrumToOSA.connect(
                    lambda FilePrefix: self.OSA.SaveToFile(
                        'D:'+'Sp_'+FilePrefix, TraceNumber=1, Type="txt"))
            self.add_thread([self.laser_scanning_process])
            self.laser_scanning_process.S_updateCurrentWavelength.connect(
                lambda S:self.ui.label_current_scanning_laser_wavelength.setText(S))
            self.force_laser_scanning_process.connect(self.laser_scanning_process.run)
            self.laser_scanning_process.S_saveData.connect(
                lambda Data,prefix: self.logger.save_data(Data,prefix,0,0,0,'FromOSA'))
            print('Start laser scanning')
            self.laser_scanning_process.S_finished.connect(
                self.ui.pushButton_scan_laser_wavelength.toggle)
            self.laser_scanning_process.S_finished.connect(lambda : self.laser_scanning(False))
            self.ui.tabWidget_instruments.setEnabled(False)
            self.ui.pushButton_Scanning.setEnabled(False)
            self.ui.pushButton_sweep_laser_wavelength.setEnabled(False)
            self.force_laser_scanning_process.emit()

        else:
            self.ui.pushButton_laser_On.setEnabled(True)
            self.laser_scanning_process.is_running=False
            self.ui.tabWidget_instruments.setEnabled(True)
            self.ui.pushButton_Scanning.setEnabled(True)
            self.ui.pushButton_sweep_laser_wavelength.setEnabled(True)
            del self.laser_scanning_process

    def laser_sweeping(self,pressed:bool):
        if pressed:
            self.ui.pushButton_laser_On.setEnabled(False)
            from Scripts.ScanningProcessLaser import LaserSweepingProcess
            self.laser_sweeping_process=LaserSweepingProcess(laser=self.laser,
                laser_power=float(self.ui.lineEdit_laser_power.text()),
                scanstep=float(self.ui.lineEdit_laser_lambda_sweeping_step.text()),
                wavelength_central=float(self.ui.lineEdit_laser_lambda_sweeping_central.text()),
                max_detuning=float(self.ui.lineEdit_laser_sweeping_max_detuning.text()),
                delay=float(self.ui.lineEdit_laser_lambda_sweeping_delay.text()))
            print(float(self.ui.lineEdit_laser_lambda_sweeping_delay.text()))
            self.add_thread([self.laser_sweeping_process])
            self.laser_sweeping_process.S_updateCurrentWavelength.connect(
                lambda S:self.ui.label_current_scanning_laser_wavelength.setText(S))
            self.force_laser_sweeping_process.connect(self.laser_sweeping_process.run)
            print('Start laser sweeping')
            self.laser_sweeping_process.S_finished.connect(
                self.ui.pushButton_sweep_laser_wavelength.toggle)
            self.laser_sweeping_process.S_finished.connect(lambda : self.laser_sweeping(False))
            self.ui.pushButton_scan_laser_wavelength.setEnabled(False)
            self.force_laser_sweeping_process.emit()

        else:
            self.ui.pushButton_laser_On.setEnabled(True)
            self.ui.pushButton_scan_laser_wavelength.setEnabled(True)
            self.laser_sweeping_process.is_running=False
            del self.laser_sweeping_process

    @pyqtSlotWExceptions()
    def enableScanningProcess(self):
        if (self.ui.groupBox_stand.isEnabled() and self.ui.tabWidget_instruments.isEnabled()):
            self.ui.groupBox_Scanning.setEnabled(True)
            self.ui.tabWidget_instruments.setCurrentIndex(0)
            self.ui.lineEdit_BackStep.setEnabled(False)
            self.ui.lineEdit_LevelToDetectContact.setEnabled(False)


    @pyqtSlotWExceptions()
    def on_equipment_ready(self, is_ready):
        self.ui.groupBox_theExperiment.setEnabled(is_ready)


    def setStageMoving(self,key,step):
        self.force_stage_move.emit(key,step)

    @pyqtSlotWExceptions("PyQt_PyObject")
    def updatePositions(self):
        X_abs=(self.stages.position['X'])
        Y_abs=(self.stages.position['Y'])
        Z_abs=(self.stages.position['Z'])

        self.ui.label_PositionX.setText(str(X_abs-self.X_0))
        self.ui.label_PositionY.setText(str(Y_abs-self.Y_0))
        self.ui.label_PositionZ.setText(str(Z_abs-self.Z_0))

        self.ui.label_AbsPositionX.setText(str(X_abs))
        self.ui.label_AbsPositionY.setText(str(Y_abs))
        self.ui.label_AbsPositionZ.setText(str(Z_abs))



    def zeroingPosition(self):
        self.X_0=(self.stages.position['X'])
        self.Y_0=(self.stages.position['Y'])
        self.Z_0=(self.stages.position['Z'])
        self.logger.save_zero_position(self.X_0,self.Y_0,self.Z_0)
        self.updatePositions()

    '''
    Interface logic
    '''

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
            self.ui.pushButton_scope_single.setEnabled(True)
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
            self.ui.pushButton_OSA_Acquire.setEnabled(False)
            self.ui.pushButton_OSA_AcquireAll.setEnabled(False)
            self.ui.pushButton_Scanning.setEnabled(False)
            self.ui.pushButton_scan_laser_wavelength.setEnabled(False)
            self.force_OSA_acquire.emit()
        else:
            self.painter.ReplotEnded.disconnect(self.force_OSA_acquire)
            self.ui.pushButton_OSA_Acquire.setEnabled(True)
            self.ui.pushButton_OSA_AcquireAll.setEnabled(True)
            self.ui.pushButton_Scanning.setEnabled(True)
            self.ui.pushButton_scan_laser_wavelength.setEnabled(True)

#
#    @pyqtSlotWExceptions()
#    def on_pushButton_AcquireAllSpectraRep_pressed(self,pressed):
#        if pressed:
#
#            self.painter.ReplotEnded.connect(self.on_pushButton_AcquireAllSpectra_pressed)
#            self.ui.pushButton_OSA_AcquireAll.setEnabled(False)
#            self.ui.pushButton_OSA_Acquire.setEnabled(False)
#            self.ui.pushButton_OSA_AcquireRep.setEnabled(False)
#            self.ui.pushButton_Scanning.setEnabled(False)
#            self.force_OSA_acquireAll.emit()
#
#        else:
#
#            self.painter.ReplotEnded.disconnect(self.on_pushButton_AcquireAllSpectra_pressed)
#            self.ui.pushButton_OSA_AcquireAll.setEnabled(True)
#            self.ui.pushButton_OSA_Acquire.setEnabled(True)
#            self.ui.pushButton_OSA_AcquireRep.setEnabled(True)
#            self.ui.pushButton_Scanning.setEnabled(True)

    def on_stateSearchContact(self):
        if self.ui.checkBox_searchContact.isChecked():
            self.ui.lineEdit_BackStep.setEnabled(True)
            self.ui.lineEdit_LevelToDetectContact.setEnabled(True)
        else:
            self.ui.lineEdit_BackStep.setEnabled(False)
            self.ui.lineEdit_LevelToDetectContact.setEnabled(False)


    def on_pushButton_Scanning_pressed(self,pressed:bool):
        if pressed:
            if self.ui.tabWidget_instruments.currentIndex()==0: ## if OSA is active, scanning
                                                                ## with OSA
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
                    numberofscans=int(self.ui.lineEdit_numberOfScans.text()),
                    searchcontact=self.ui.checkBox_searchContact.isChecked(),
                    followPeak=self.ui.checkBox_followPeak.isChecked(),
                    saveDifference=self.ui.checkBox_saveDifference.isChecked())
                self.scanningProcess.S_saveData.connect(
                    lambda Data,prefix: self.logger.save_data(Data,prefix,
                        self.stages.position['X']-self.X_0, self.stages.position['Y']-self.Y_0,
                        self.stages.position['Z']-self.Z_0,'FromOSA'))
                self.scanningProcess.S_saveSpectrumToOSA.connect(
                    lambda FilePrefix: self.OSA.SaveToFile(
                        'D:'+'Sp_'+FilePrefix, TraceNumber=1, Type="txt"))

            elif self.ui.tabWidget_instruments.currentIndex()==1: ## if scope is active,
                                                                  ## scanning with scope
                from Scripts.ScanningProcessScope import ScanningProcess
                self.scanningProcess=ScanningProcess(Scope=self.scope,Stages=self.stages,
                    scanstep=int(self.ui.lineEdit_ScanningStep.text()),
                    seekcontactstep=int(self.ui.lineEdit_SearchingStep.text()),
                    backstep=int(self.ui.lineEdit_BackStep.text()),
                    seekcontactvalue=float(self.ui.lineEdit_LevelToDetectContact.text()),
                    ScanningType=int(self.ui.comboBox_ScanningType.currentIndex()),
                    CurrentFileIndex=int(self.ui.lineEdit_CurrentFile.text()),
                    StopFileIndex=int(self.ui.lineEdit_StopFile.text()),
                    numberofscans=int(self.ui.lineEdit_numberOfScans.text()),
                    searchcontact=self.ui.checkBox_searchContact.isChecked())
                self.scanningProcess.S_saveData.connect(
                    lambda Data,prefix: self.logger.save_data(Data,prefix,
                        self.stages.position['X']-self.X_0,
                        self.stages.position['Y']-self.Y_0,
                        self.stages.position['Z']-self.Z_0, 'FromScope'))
            self.scanningProcess.S_finished.connect(self.ui.pushButton_Scanning.toggle)
            self.scanningProcess.S_finished.connect(
                lambda : self.on_pushButton_Scanning_pressed(False))
            self.scanningProcess.S_updateCurrentFileName.connect(
                lambda S: self.ui.lineEdit_CurrentFile.setText(S))
            self.add_thread([self.scanningProcess])
            self.ui.tabWidget_instruments.setEnabled(False)
            self.ui.groupBox_stand.setEnabled(False)
            self.force_scanning_process.connect(self.scanningProcess.run)
            print('Start Scanning')
            self.force_scanning_process.emit()

        else:
            self.scanningProcess.is_running=False
            del self.scanningProcess
            self.ui.tabWidget_instruments.setEnabled(True)
            self.ui.groupBox_scope_control.setEnabled(True)
            self.ui.groupBox_stand.setEnabled(True)


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

        FilePrefix=self.ui.EditLine_saveSpectrumName.text()
        self.logger.save_data(Data,FilePrefix,X,Y,Z,self.painter.TypeOfData)

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
        self.processSpectra.ProcessedDataFolder=self.path_to_main+'\\ProcessedData\\'
        self.processSpectra.Source_DirName=self.path_to_main+'\\SpectralData\\'
        self.processSpectra.run(
            StepSize=float(self.ui.lineEdit_ScanningStep.text()),
            Averaging=self.ui.checkBox_IsAveragingWhileProcessing.isChecked(),
            Shifting=self.ui.checkBox_IsShiftingWhileProcessing.isChecked(),
            axis_to_plot_along=self.ui.comboBox_axis_to_plot_along.currentText())

    def on_Push_Button_ProcessTD(self):
        from Scripts.ProcessAndPlotTD import ProcessAndPlotTD
        self.ProcessTD=ProcessAndPlotTD()
        Thread=self.add_thread([self.ProcessTD])
        self.ProcessTD.run(Averaging=self.ui.checkBox_IsAveragingWhileProcessing.isChecked(),
            DirName='TimeDomainData',
            axis_to_plot_along=self.ui.comboBox_axis_to_plot_along.currentText(),
            channel_number=self.ui.comboBox_TD_channel_to_plot.currentIndex())
        Thread.quit()

    def plotSampleShape(self,DirName,axis):
        self.processSpectra.plot_sample_shape(axis_to_plot_along=axis)


    def saveParametersToFile(self):
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
        Dict['SearchingContact?']=str(self.ui.checkBox_searchContact.isChecked())
        Dict['AverageShapeWhileProcessing?']=str(
            self.ui.checkBox_IsAveragingWhileProcessing.isChecked())
        Dict['ShiftingWhileProcessing?']=str(self.ui.checkBox_IsShiftingWhileProcessing.isChecked())
        Dict['axis_to_plot_along']=str(self.ui.comboBox_axis_to_plot_along.currentIndex())
        Dict['Channel_TD_to_plot']=str(self.ui.comboBox_TD_channel_to_plot.currentIndex())
        Dict['analyzer_axis_to_plot_along']=str(
            self.ui.comboBox_axis_to_analyze_along_arb_data.currentIndex())
        Dict['analyzer_min_wavelength']=float(self.ui.lineEdit_analyzer_wavelength_min.text())
        Dict['analyzer_max_wavelength']=float(self.ui.lineEdit_analyzer_wavelength_max.text())
        Dict['analyzer_resonance_level']=float(self.ui.lineEdit_analyzer_resonance_level.text())
        Dict['save_difference?']=str(self.ui.checkBox_saveDifference.isChecked())

        self.logger.SaveParameters(Dict)

    def loadParametersFromFile(self):
        Dict=self.logger.LoadParameters()
        self.ui.EditLine_saveSpectrumName.setText(str(Dict['saveSpectrumName']))
        self.ui.EditLine_StartWavelength.setText('{:.5f}'.format(Dict['StartWavelength']))
        self.ui.EditLine_StopWavelength.setText('{:.5f}'.format(Dict['StopWavelength']))


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
        self.ui.checkBox_searchContact.setChecked(Dict['SearchingContact?']=='True')
        self.ui.checkBox_IsAveragingWhileProcessing.setChecked(
            Dict['AverageShapeWhileProcessing?']=='True')
        self.ui.checkBox_IsShiftingWhileProcessing.setChecked(
            Dict['ShiftingWhileProcessing?']=='True')
        self.ui.checkBox_saveDifference.setChecked(Dict['save_difference?']=='True')
        self.ui.lineEdit_numberOfScans.setText(str(Dict['NumberOfScans']))

        self.ui.comboBox_axis_to_plot_along.setCurrentIndex(int(Dict['axis_to_plot_along']))
        self.ui.comboBox_TD_channel_to_plot.setCurrentIndex(int(Dict['Channel_TD_to_plot']))

        self.ui.comboBox_axis_to_analyze_along_arb_data.setCurrentIndex(
            int(Dict['analyzer_axis_to_plot_along']))
        self.ui.lineEdit_analyzer_wavelength_min.setText(
            '{:.2f}'.format(Dict['analyzer_min_wavelength']))
        self.ui.lineEdit_analyzer_wavelength_max.setText(
            '{:.2f}'.format(Dict['analyzer_max_wavelength']))
        self.ui.lineEdit_analyzer_resonance_level.setText(
            '{:.2f}'.format(Dict['analyzer_resonance_level']))

        if Dict['IsHighRes']=='True':
            self.ui.checkBox_HighRes.setChecked(True)
            if self.OSA is not None:
                self.OSA.SetWavelengthResolution('High')
                self.OSA.change_range(float(Dict['StartWavelength']), float(Dict['StopWavelength']))
                self.force_OSA_acquire.emit()
        else:
            self.ui.checkBox_HighRes.setChecked(False)
            if self.OSA is not None:
                self.OSA.SetWavelengthResolution('Low')
                self.OSA.change_range(float(Dict['StartWavelength']), float(Dict['StopWavelength']))
                self.force_OSA_acquire.emit()
        print('Parameters loaded')

    def choose_folder_to_process(self):
        self.processSpectra.Source_DirName = str(
            QFileDialog.getExistingDirectory(self, "Select Directory"))+'\\'
        self.processSpectra.ProcessedDataFolder=os.path.dirname(
            os.path.dirname(self.processSpectra.Source_DirName))+'\\'
        self.ui.label_folder_to_process_files.setText(self.processSpectra.Source_DirName+'\\')

    def process_arb_spectral_data_clicked(self):
        Folder=self.processSpectra.Source_DirName
        try:
            StepSize=int(Folder[Folder.index('Step=')+len('Step='):len(Folder)])
        except ValueError:
            StepSize=float(self.ui.lineEdit_ScanningStep.text())
        self.processSpectra.run(StepSize=StepSize,
            Averaging=self.ui.checkBox_IsAveragingWhileProcessingArbData.isChecked(),
            Shifting=self.ui.checkBox_IsShiftingWhileProcessingArbData.isChecked(),
            axis_to_plot_along=self.ui.comboBox_axis_to_plot_along_arb_data.currentText(),
            type_of_data=self.ui.comboBox_type_of_data.currentText())

    def process_arb_TD_data_clicked(self):
        from Scripts.ProcessAndPlotTD import ProcessAndPlotTD
        self.ProcessTD=ProcessAndPlotTD()
        Thread=self.add_thread([self.ProcessTD])
        self.ProcessTD.run(Averaging=self.ui.checkBox_IsAveragingWhileProcessingArbData.isChecked(),
            DirName=self.Folder,
            axis_to_plot_along=self.ui.comboBox_axis_to_plot_along_arb_data.currentText(),
            channel_number=self.ui.comboBox_TD_channel_to_plot_arb_data.currentIndex())
        Thread.quit()

    def plot_single_spectrum_from_file(self):
        DataFilePath= str(QFileDialog.getOpenFileName(
            self, "Select Data File",'','*.pkl')).split("\',")[0].split("('")[1]
        self.analyzer.single_spectrum_path=DataFilePath
        self.analyzer.plot_single_spectrum_from_file()
        self.ui.label_analyzer_single_spectrum_file.setText(self.analyzer.single_spectrum_path)

    def choose_folder_for_analyzer(self):
        DataFilePath= str(QFileDialog.getOpenFileName(
            self, "Select Data File",'','*.pkl')).split("\',")[0].split("('")[1]
        self.analyzer.FilePath=DataFilePath
        self.analyzer.Data=None
        self.ui.label_analyzer_folder.setText(self.analyzer.FilePath)

    def closeEvent(self, event):
#         here you can terminate your threads and do other stuff
#        try:
        del self.stages
        print('Stages object is deleted')
        del self.OSA
        print('OSA object is deleted')
        del self.painter
        print('Painter object is deleted')
        del self.logger
        print('Logger is deleted')
        del self.analyzer
        print('Analyzer is deleted')
        try:
            self.laser.setOff()
            del self.laser
            print('laser is deleted')
        except:
            pass
        try:
            del self.scanningProcess
            print('Scanning object is deleted')
        except:
            pass
        del self.processSpectra
        print('Processing is deleted')
        super(QMainWindow, self).closeEvent(event)
