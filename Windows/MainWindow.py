# -*- coding: utf-8 -*-

__date__='2022.04.01'
import os
if __name__=='__main__':
    os.chdir('..')
import numpy as np
import matplotlib.pyplot as plt

from PyQt5.QtCore import pyqtSignal, QThread
from PyQt5.QtWidgets import QMainWindow, QFileDialog, QDialog,QLineEdit,QComboBox,QCheckBox,QMessageBox

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
# from Scripts import AnalyzerForSpectrogram
from Scripts import Analyzer
from Scripts import Spectral_processor
import sys


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
       
        self.stages=None
        self.OSA=None
        self.scope=None
        self.laser=None
        self.powermeter=None
        
        self.painter = MyPainter(self.ui.groupBox_spectrum)
        self.analyzer=Analyzer.Analyzer(os.getcwd()+'\\ProcessedData\\Processed_spectrogram.pkl3d')
        self.logger = Logger(parent=None)
        self.spectral_processor=Spectral_processor.Spectral_processor(self.path_to_main)
        from Scripts.ScanningProcessOSA import ScanningProcess
        self.scanningProcess=ScanningProcess()
        self.add_thread([self.painter,self.logger,self.analyzer,self.spectral_processor,self.scanningProcess])
        
        
        self.ui.tabWidget_instruments.currentChanged.connect(self.on_TabChanged_instruments_changed)
        self.init_OSA_interface()
        self.init_analyzer_interface()
        self.init_laser_interface()
        self.init_logger_interface()
        self.init_painter_interface()
        self.init_power_meter_interface()
        self.init_processing_interface()
        self.init_scanning_interface()
        self.init_scope_interface()
        self.init_stages_interface()
        self.init_menu_bar()
        
        self.load_parameters_from_file()
        
        
    def init_menu_bar(self):
        self.ui.action_save_parameters.triggered.connect(self.save_parameters_to_file)
        self.ui.action_load_parameters.triggered.connect(self.load_parameters_from_file)
        self.ui.action_delete_all_figures.triggered.connect(lambda:plt.close(plt.close('all')))
        self.ui.action_delete_all_measured_spectral_data.triggered.connect(self.delete_data_from_folders)
# =============================================================================
#         Stages interface
# =============================================================================
    def init_stages_interface(self):
        self.ui.pushButton_StagesConnect.pressed.connect(self.connect_stages)
        self.X_0,self.Y_0,self.Z_0=[0,0,0]

# =============================================================================
#         # OSA interface
# =============================================================================
    def init_OSA_interface(self):        
        self.ui.pushButton_OSA_connect.pressed.connect(self.connect_OSA)
        self.ui.pushButton_OSA_Acquire.pressed.connect(
            self.on_pushButton_acquireSpectrum_pressed)
        self.ui.pushButton_OSA_AcquireAll.pressed.connect(
            self.on_pushButton_AcquireAllSpectra_pressed)
        self.ui.pushButton_OSA_AcquireRep.clicked[bool].connect(
            self.on_pushButton_acquireSpectrumRep_pressed)

        self.ui.label_Luna_mode.setVisible(False)
        self.ui.comboBox_Luna_mode.setVisible(False)
        self.ui.comboBox_Luna_mode.currentTextChanged.connect(lambda : self.enable_scanning_process())
        self.ui.comboBox_Type_of_OSA.currentTextChanged.connect(self.features_visibility)
        
        

# =============================================================================
#         # scope interface
# =============================================================================
    def init_scope_interface(self):   
        self.ui.pushButton_scope_connect.pressed.connect(self.connect_scope)
        self.ui.pushButton_scope_single.pressed.connect(
            self.on_pushButton_scope_single_measurement)
        self.ui.pushButton_scope_repeat.clicked[bool].connect(
            self.on_pushButton_scope_repeat__pressed)
        
# =============================================================================
#         powermeter interface
# =============================================================================
    def init_power_meter_interface(self):        
        self.ui.pushButton_powermeter_connect.pressed.connect(self.connect_powermeter)


# =============================================================================
#         # painter and drawing interface
# =============================================================================
    def init_painter_interface(self):

        self.ui.checkBox_FreezeSpectrum.stateChanged.connect(self.on_stateChangeOfFreezeSpectrumBox)
        self.ui.checkBox_ApplyFFTFilter.stateChanged.connect(self.on_stateChangeOfApplyFFTBox)
        self.ui.checkBox_HighRes.stateChanged.connect(self.on_stateChangeOfIsHighResolution)
        self.ui.pushButton_getRange.pressed.connect(self.on_pushButton_getRange)
        self.ui.lineEdit_StartWavelength.editingFinished.connect(
            lambda:self.OSA.change_range(start_wavelength=float(self.ui.lineEdit_StartWavelength.text())) 
            if (isfloat(self.ui.lineEdit_StartWavelength.text())) else 0)
        self.ui.lineEdit_StopWavelength.editingFinished.connect(
            lambda:self.OSA.change_range(stop_wavelength=float(self.ui.lineEdit_StartWavelength.text())) 
            if (isfloat(self.ui.lineEdit_StartWavelength.text())) else 0)

# =============================================================================
#         saving interface
# =============================================================================
    def init_logger_interface(self):
        self.ui.pushButton_save_data.pressed.connect(self.on_pushButton_save_data)

# =============================================================================
#         #scanning process
# =============================================================================
    def init_scanning_interface(self):        
        self.ui.pushButton_scan_in_space.toggled[bool].connect(self.on_pushButton_scan_in_space)
        self.ui.pushButton_set_scanning_parameters.clicked.connect(self.on_pushButton_set_scanning_parameters)

# =============================================================================
#         # processing
# =============================================================================
    def init_processing_interface(self):
        self.ui.pushButton_process_measured_spectral_data.pressed.connect(self.on_Push_Button_ProcessSpectra)
        self.ui.pushButton_processTDData.pressed.connect(self.on_pushButton_ProcessTD)
        self.ui.pushButton_choose_folder_to_process.clicked.connect(self.choose_folder_for_spectral_processor)
                
        self.ui.pushButton_process_arb_spectral_data.clicked.connect(
            self.process_arb_spectral_data_clicked)
        self.ui.pushButton_process_arb_TD_data.clicked.connect(self.process_arb_TD_data_clicked)
        self.ui.pushButton_plotSampleShape.clicked.connect(lambda:self.spectral_processor.plot_sample_shape())
            
        self.ui.pushButton_plotSampleShape_arb_data.clicked.connect(lambda:self.spectral_processor.plot_sample_shape())
        self.ui.pushButton_set_spectral_processor_parameters.clicked.connect(self.on_pushButton_set_spectral_processor_parameters)
        self.ui.pushButton_set_spectral_processor_parameters_2.clicked.connect(self.on_pushButton_set_spectral_processor_parameters)
# =============================================================================
#         # analyzer logic
# =============================================================================

    def init_analyzer_interface(self):
        self.ui.pushButton_analyzer_choose_file_spectrogram.clicked.connect(
            self.choose_file_for_analyzer)
        self.ui.pushButton_analyzer_choose_plotting_param_file.clicked.connect(
            self.choose_file_for_analyzer_plotting_parameters)

        self.ui.pushButton_analyzer_plot_single_spectrum_from_file.clicked.connect(
            self.plot_single_spectrum_from_file)
        
        self.ui.pushButton_analyzer_plot_ERV_from_file.clicked.connect(
            self.plot_ERV_from_file)

        self.ui.pushButton_analyzer_plotSampleShape.clicked.connect(
            self.analyzer.plot_sample_shape)
        self.ui.pushButton_analyzer_plot2D.clicked.connect(lambda: self.analyzer.plot_spectrogram())
        self.ui.pushButton_analyzer_plotSlice.clicked.connect(lambda: self.analyzer.plot_slice(float(self.ui.lineEdit_slice_position.text())))
        self.ui.pushButton_analyzer_save_slice.clicked.connect(self.analyzer.save_slice_data)
        self.ui.pushButton_analyzer_analyze_spectrum.clicked.connect(lambda: self.analyzer.analyze_spectrum(self.analyzer.single_spectrum_figure))
            
        self.ui.pushButton_analyze_spectrum.clicked.connect(lambda: self.analyzer.analyze_spectrum( self.painter.figure))
     
        self.ui.pushButton_analyzer_extract_ERV.clicked.connect(lambda: self.analyzer.extract_ERV())
        
        self.ui.pushButton_analyzer_apply_FFT_filter.clicked.connect(lambda: self.analyzer.apply_FFT_to_spectrogram())
        
        self.ui.pushButton_analyzer_save_cropped_data.clicked.connect(
            self.analyzer.save_cropped_data)
        
        self.ui.pushButton_set_analyzer_parameters.clicked.connect(self.on_pushButton_set_analyzer_parameters)
        self.ui.pushButton_analyzer_save_as_pkl3d.clicked.connect(lambda: self.analyzer.save_as_pkl3d())

# =============================================================================
#         Pure Photonics Tunable laser
# =============================================================================
    def init_laser_interface(self):        
        self.ui.pushButton_laser_connect.clicked.connect(self.connect_laser)
        self.ui.pushButton_laser_On.clicked[bool].connect(self.on_pushButton_laser_On)
        self.ui.comboBox_laser_mode.currentIndexChanged.connect(self.change_laser_mode)
        self.ui.lineEdit_laser_fine_tune.textChanged.connect(self.laser_fine_tuning)
        self.ui.pushButton_scan_laser_wavelength.clicked[bool].connect(self.laser_scanning)
        self.ui.pushButton_hold_laser_wavelength.clicked[bool].connect(self.laser_scaning_hold_wavelength)
        self.ui.pushButton_sweep_laser_wavelength.clicked[bool].connect(self.laser_sweeping)

# =============================================================================
#   interface methods
# =============================================================================
    def connect_scope(self):
        '''
        create connection to scope

        Returns
        -------
        None.

        '''
        self.scope=Scope(Consts.Scope.HOST)
        self.add_thread([self.scope])
        self.scope.received_data.connect(self.painter.set_data)
        self.ui.tabWidget_instruments.setEnabled(True)
        self.ui.tabWidget_instruments.setCurrentIndex(1)
        self.ui.groupBox_scope_control.setEnabled(True)
        self.enable_scanning_process()
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

    
    def features_visibility(self, OSA):
        try:
            if OSA=='Luna':
                self.ui.groupBox_features.setVisible(True)
                flag = True
            elif OSA=='APEX':
                self.ui.groupBox_features.setVisible(True)
                flag = False
            else:
                self.ui.groupBox_features.setVisible(False)
                return
            self.ui.label_Luna_mode.setVisible(flag)
            self.ui.comboBox_Luna_mode.setVisible(flag)
            self.ui.label_29.setVisible(not flag)
            self.ui.comboBox_APEX_mode.setVisible(not flag)
        except:
            print(sys.exc_info())
    
    def connect_OSA(self):
        '''
        set connection to OSA: Luna, Yokogawa, ApEx Technologies or Astro interrogator

        Returns
        -------
        None.

        '''
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
            self.ui.comboBox_APEX_mode.currentIndexChanged[int].connect(lambda x: self.OSA.SetMode(x+3))
            self.spectral_processor.isInterpolation=True

        self.add_thread([self.OSA])
        self.OSA.received_spectrum.connect(self.painter.set_data)

        self.force_OSA_acquire.connect(self.OSA.acquire_spectrum)
        self.ui.tabWidget_instruments.setEnabled(True)
        self.ui.tabWidget_instruments.setCurrentIndex(0)
        self.ui.lineEdit_StartWavelength.setText(str(self.OSA._StartWavelength))
        self.ui.lineEdit_StopWavelength.setText(str(self.OSA._StopWavelength))

        self.ui.groupBox_OSA_control.setEnabled(True)
        self.ui.checkBox_OSA_for_laser_scanning.setEnabled(True)
        print('Connected with OSA')
        self.on_pushButton_acquireSpectrum_pressed()
        self.enable_scanning_process()
        self.painter.TypeOfData='FromOSA'

    def connect_stages(self):
        '''
        set connection to either Thorlabs or Standa stages 

        Returns
        -------
        None.

        '''
        if self.ui.comboBox_Type_of_Stages.currentText()=='3x Standa':
            from Hardware.MyStanda import StandaStages
            self.stages=StandaStages()
        elif self.ui.comboBox_Type_of_Stages.currentText()=='2x Thorlabs':
            import Hardware.MyThorlabsStages
            self.stages=Hardware.MyThorlabsStages.ThorlabsStages()
            self.ui.pushButton_MovePlusY.setEnabled(False)
            self.ui.pushButton_MoveMinusY.setEnabled(False)

        if self.stages.isConnected>0:
            print('Connected to stages')
            self.add_thread([self.stages])
            self.stages.set_zero_positions(self.logger.load_zero_position())
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
            self.ui.pushButton_zeroingPositions.pressed.connect(self.on_pushButton_zeroingPositions)
            self.force_stage_move[str,int].connect(lambda S,i:self.stages.shiftOnArbitrary(S,i))
            self.stages.stopped.connect(self.updatePositions)
            self.ui.groupBox_stand.setEnabled(True)
            self.ui.pushButton_zeroing_stages.pressed.connect(
                self.on_pushButton_zeroing_stages)

            self.enable_scanning_process()

    def on_pushButton_zeroing_stages(self):
        '''
        move stages to zero position

        Returns
        -------
        None.

        '''
        self.stages.move_home()
        
        
    def connect_powermeter(self):
        '''
        set connection to powermeter Thorlabs

        Returns
        -------
        None.

        '''
        try:
            from Hardware import ThorlabsPM100
            self.powermeter=ThorlabsPM100.PowerMeter(Consts.Powermeter.SERIAL_NUMBER)
            self.ui.checkBox_powermeter_for_laser_scanning.setEnabled(True)
        except:
            print('Connection to power meter failed')

    def connect_laser(self):
        '''
        set connection to Pure Photonics tunable laser

        Returns
        -------
        None.

        '''
        COMPort='COM'+self.ui.lineEdit_laser_COMport.text()
        try:
            from Hardware.PurePhotonicsLaser import Laser
            self.laser=Laser(COMPort)
            self.laser.fineTuning(0)
            print('Laser has been connected')
            self.ui.groupBox_laser_operation.setEnabled(True)
            self.ui.groupBox_laser_sweeping.setEnabled(True)
            self.ui.groupBox_laser_scanning.setEnabled(True)
    #            self.add_thread([self.laser])
        except:
            print('Connection to laser failed. Check the COM port number')


    def on_pushButton_laser_On(self,pressed:bool):
        '''
        switch tunable laser between ON and OFF state

        Parameters
        ----------
        pressed : bool
            DESCRIPTION. current state of the button

        Returns
        -------
        None.

        '''
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
        '''
        change between Whisper, Dittering, and No Dittering modes of Pure Photonics Laser

        Returns
        -------
        None.

        '''
        self.laser.setMode(self.ui.comboBox_laser_mode.currentText())

    def laser_fine_tuning(self):
        '''
        fine tune of the Pure Photonics laser for the spectral shift specified at 
        lineEdit_laser_fine_tune

        Returns
        -------
        None.

        '''
        self.laser.fineTuning(float(self.ui.lineEdit_laser_fine_tune.text()))

    def laser_scanning(self,pressed:bool):
        '''
        run scan of the Pure Photonics laser wavelength and save data from either OSA or powermeter at each laser wavelength
        Spectra are saved to 'SpectralData\\'
        Power VS wavelength is saved to 'ProcessedData\\Power_from_powermeter_VS_laser_wavelength.txt' when scanning is stopped

        Parameters
        ----------
        pressed : bool
            DESCRIPTION. Current state of the scanning button

        Returns
        -------
        None.

        '''
        if pressed:
            self.ui.pushButton_laser_On.setEnabled(False)
            from Scripts.ScanningProcessLaser import LaserScanningProcess
            self.laser_scanning_process=LaserScanningProcess(OSA=(self.OSA if self.ui.checkBox_OSA_for_laser_scanning.isChecked() else None),
                laser=self.laser,
                powermeter=(self.powermeter if self.ui.checkBox_powermeter_for_laser_scanning.isChecked() else None),
                laser_power=float(self.ui.lineEdit_laser_power.text()),
                scanstep=float(self.ui.lineEdit_laser_lambda_scanning_step.text()),
                wavelength_start=float(self.ui.lineEdit_laser_lambda_scanning_min.text()),
                wavelength_stop=float(self.ui.lineEdit_laser_lambda_scanning_max.text()),
                file_to_save='ProcessedData\\Power_from_powermeter_VS_laser_wavelength.txt')
            self.add_thread([self.laser_scanning_process])
            self.laser_scanning_process.S_updateCurrentWavelength.connect(
                lambda S:self.ui.label_current_scanning_laser_wavelength.setText(S))
            
            self.laser_scanning_process.S_saveData.connect(
                lambda Data,prefix: self.logger.save_data(Data,prefix,0,0,0,'FromOSA'))
            print('Start laser scanning')
            self.laser_scanning_process.S_toggle_button.connect(lambda:
                self.ui.pushButton_scan_laser_wavelength.setChecked(False))
            self.laser_scanning_process.S_toggle_button.connect(lambda : self.laser_scanning(False))
            self.ui.tabWidget_instruments.setEnabled(False)
            self.ui.pushButton_scan_in_space.setEnabled(False)
            self.ui.pushButton_sweep_laser_wavelength.setEnabled(False)
            self.ui.pushButton_hold_laser_wavelength.setEnabled(True)
            self.laser_scanning_process.initialize_laser()
            self.force_laser_scanning_process.connect(self.laser_scanning_process.run)
            self.force_laser_scanning_process.emit()

        else:
            self.ui.pushButton_laser_On.setEnabled(True)
            self.laser_scanning_process.is_running=False
            self.ui.tabWidget_instruments.setEnabled(True)
            self.ui.pushButton_scan_in_space.setEnabled(True)
            self.ui.pushButton_sweep_laser_wavelength.setEnabled(True)
            self.ui.pushButton_hold_laser_wavelength.setEnabled(False)
            del self.laser_scanning_process
            
    def laser_scaning_hold_wavelength(self,pressed:bool):
        '''
        hold PurePhotonics laser scanning process, and current wavelength unchanged, and save data continously

        Parameters
        ----------
        pressed : bool
            DESCRIPTION. Current state of the hold button within scanning proccess

        Returns
        -------
        None.
       
        '''
        self.laser_scanning_process.hold_wavelength=pressed
   

    def laser_sweeping(self,pressed:bool):
        '''
        run PurePhotonics laser 'fast' scanning without saving data

        Parameters
        ----------
        pressed : bool
            DESCRIPTION. Current state of the sweeping button

        Returns
        -------
        None.

        '''
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
    def on_equipment_ready(self, is_ready):
        self.ui.groupBox_theExperiment.setEnabled(is_ready)


    def setStageMoving(self,key,step):
        self.force_stage_move.emit(key,step)

    @pyqtSlotWExceptions("PyQt_PyObject")
    def updatePositions(self):
        X_abs=(self.stages.abs_position['X'])
        Y_abs=(self.stages.abs_position['Y'])
        Z_abs=(self.stages.abs_position['Z'])
        
        X_rel=(self.stages.relative_position['X'])
        Y_rel=(self.stages.relative_position['Y'])
        Z_rel=(self.stages.relative_position['Z'])

        self.ui.label_PositionX.setText(str(X_rel))
        self.ui.label_PositionY.setText(str(Y_rel))
        self.ui.label_PositionZ.setText(str(Z_rel))

        self.ui.label_AbsPositionX.setText(str(X_abs))
        self.ui.label_AbsPositionY.setText(str(Y_abs))
        self.ui.label_AbsPositionZ.setText(str(Z_abs))



    def on_pushButton_zeroingPositions(self):
        X_0=(self.stages.abs_position['X'])
        Y_0=(self.stages.abs_position['Y'])
        Z_0=(self.stages.abs_position['Z'])
        self.stages.zero_position=self.stages.abs_position.copy()
        self.stages.update_relative_positions()
        self.logger.save_zero_position(X_0,Y_0,Z_0)
        self.updatePositions()

    '''
    Interface logic
    '''

    def on_pushButton_scope_single_measurement(self):
        self.scope.acquire()

    def on_pushButton_scope_repeat__pressed(self,pressed):
        if pressed:
            self.painter.ReplotEnded.connect(self.scope.acquire)
            self.ui.pushButton_scope_single.setEnabled(False)
            self.ui.pushButton_scan_in_space.setEnabled(False)
            self.scope.acquire()
        else:
            self.painter.ReplotEnded.disconnect(self.scope.acquire)
#            self.painter.ReplotEnded.disconnect(self.force_scope_acquire)
            self.ui.pushButton_scope_single.setEnabled(True)
            self.ui.pushButton_scan_in_space.setEnabled(True)

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
            self.ui.pushButton_scan_in_space.setEnabled(False)
            self.ui.pushButton_scan_laser_wavelength.setEnabled(False)
            self.force_OSA_acquire.emit()
        else:
            self.painter.ReplotEnded.disconnect(self.force_OSA_acquire)
            self.ui.pushButton_OSA_Acquire.setEnabled(True)
            self.ui.pushButton_OSA_AcquireAll.setEnabled(True)
            self.ui.pushButton_scan_in_space.setEnabled(True)
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
#            self.ui.pushButton_scan_in_space.setEnabled(False)
#            self.force_OSA_acquireAll.emit()
#
#        else:
#
#            self.painter.ReplotEnded.disconnect(self.on_pushButton_AcquireAllSpectra_pressed)
#            self.ui.pushButton_OSA_AcquireAll.setEnabled(True)
#            self.ui.pushButton_OSA_Acquire.setEnabled(True)
#            self.ui.pushButton_OSA_AcquireRep.setEnabled(True)
#            self.ui.pushButton_scan_in_space.setEnabled(True)

    @pyqtSlotWExceptions()
    def enable_scanning_process(self):
        '''
        check whether both stages and measuring equipment have been connected to enable scanning features

        Returns
        -------
        None.

        '''
        if (self.ui.groupBox_stand.isEnabled() and self.ui.tabWidget_instruments.isEnabled()):
            self.scanningProcess.OSA=self.OSA
            self.scanningProcess.stages=self.stages
            self.ui.groupBox_Scanning.setEnabled(True)
            self.ui.tabWidget_instruments.setCurrentIndex(0)
            self.scanningProcess.S_saveData.connect(
                        lambda Data,prefix: self.logger.save_data(Data,prefix,
                            self.stages.relative_position['X'], self.stages.relative_position['Y'],
                            self.stages.relative_position['Z'],'FromOSA'))
            self.scanningProcess.S_finished.connect(lambda: self.ui.pushButton_scan_in_space.setChecked(False))
            self.scanningProcess.S_finished.connect(
                    lambda : self.on_pushButton_scan_in_space(False))
            self.scanningProcess.S_update_status.connect(lambda S: self.ui.label_scanning_index_status.setText(S))
            
            if (self.ui.comboBox_Type_of_OSA.currentText()=='Luna' and self.ui.comboBox_Luna_mode.currentText() == 'Luna .bin files'):
                self.scanningProcess.LunaJonesMeasurement=True
                self.scanningProcess.S_saveData.connect(lambda data, name: self.OSA.save_binary(
                    f"{self.logger.SpectralBinaryDataFolder}"
                    + f"Sp_{name}_X={self.stages.relative_position['X']}"
                    + f"_Y={self.stages.relative_position['Y']}"
                    + f"_Z={self.stages.relative_position['Z']}_.bin"))



    def on_pushButton_scan_in_space(self,pressed:bool):
        try:
            if pressed:

                if self.ui.tabWidget_instruments.currentIndex()==0: ## if OSA is active, scanning
                    self.scanningProcess.is_running=True
                    final_position=(self.scanningProcess.stop_file_index-self.scanningProcess.current_file_index)*self.scanningProcess.scanning_step+self.stages.relative_position[self.scanningProcess.axis_to_scan]
                    self.ui.label_scanning_final_position.setText(str(final_position))
                    self.ui.label_scanning_axis.setText(self.scanningProcess.axis_to_scan)
                                          ## with OSA
    
            #     elif self.ui.tabWidget_instruments.currentIndex()==1: ## if scope is active,
            #                                                           ## scanning with scope
            #         from Scripts.ScanningProcessScope import ScanningProcess
            #         self.scanningProcess=ScanningProcess(Scope=self.scope,Stages=self.stages,
            #             scanstep=int(self.ui.lineEdit_ScanningStep.text()),
            #             seekcontactstep=int(self.ui.lineEdit_SearchingStep.text()),
            #             backstep=int(self.ui.lineEdit_BackStep.text()),
            #             seekcontactvalue=float(self.ui.lineEdit_LevelToDetectContact.text()),
            #             ScanningType=int(self.ui.comboBox_ScanningType.currentIndex()),
            #             CurrentFileIndex=int(self.ui.lineEdit_CurrentFile.text()),
            #             StopFileIndex=int(self.ui.lineEdit_StopFile.text()),
            #             numberofscans=int(self.ui.lineEdit_numberOfScans.text()),
            #             searchcontact=self.ui.checkBox_searchContact.isChecked())
            #         self.scanningProcess.S_saveData.connect(
            #             lambda Data,prefix: self.logger.save_data(Data,prefix,
            #                 self.stages.relative_position['X'],
            #                 self.stages.relative_position['Y'],
            #                 self.stages.relative_position['Z'], 'FromScope'))
                
              

                self.ui.tabWidget_instruments.setEnabled(False)
                self.ui.groupBox_stand.setEnabled(False)
                self.ui.pushButton_set_scanning_parameters.setEnabled(False)
                self.force_scanning_process.connect(self.scanningProcess.run)
                print('Start Scanning')
                self.force_scanning_process.emit()

    
            else:
                self.scanningProcess.is_running=False
                self.ui.tabWidget_instruments.setEnabled(True)
                self.ui.groupBox_scope_control.setEnabled(True)
                self.ui.groupBox_stand.setEnabled(True)
                self.ui.pushButton_set_scanning_parameters.setEnabled(True)
        except:
            print(sys.exc_info())


    def on_pushButton_save_data(self):
        try:
            if self.stages is not None:
                X=self.stages.relative_position['X']
                Y=self.stages.relative_position['Y']
                Z=self.stages.relative_position['Z']
            else:
                    X,Y,Z=[0,0,0]

            Ydata=self.painter.Ydata
            Data=self.painter.Xdata
            for YDataColumn in Ydata:
                if YDataColumn is not None:
                    Data=np.column_stack((Data, YDataColumn))

            FilePrefix=self.ui.lineEdit_saveSpectrumName.text()
            if (self.ui.comboBox_Type_of_OSA.currentText()=='Luna' and 
                    self.ui.comboBox_Luna_mode.currentText() == 'Luna .bin files'):
                        self.OSA.save_binary( f"{self.logger.SpectralBinaryDataFolder}"
                            + f"Sp_{FilePrefix}_X={X}"
                            + f"_Y={Y}"
                            + f"_Z={Z}_.bin")
                        print("Saving Luna as bin")

            else:
                self.logger.save_data(Data,FilePrefix,X,Y,Z,self.painter.TypeOfData)
        except:
                print(sys.exc_info())

    def on_pushButton_getRange(self):
        Range=(self.painter.ax.get_xlim())
        self.ui.lineEdit_StartWavelength.setText(f'{Range[0]}:.1f')
        self.ui.lineEdit_StopWavelength.setText(f'{Range[1]}:.1f')
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
        if self.ui.checkBox_FreezeSpectrum.isChecked() and self.painter.Xdata is not None:
            self.painter.savedY=list(self.painter.Ydata)
            self.painter.savedX=list(self.painter.Xdata)
        else:
            self.painter.savedY=[None]*8

    def on_stateChangeOfApplyFFTBox(self):
        if self.ui.checkBox_ApplyFFTFilter.isChecked():
            self.painter.ApplyFFTFilter=True
            self.painter.FilterLowFreqEdge=float(self.ui.lineEdit_FilterLowFreqEdge.text())
            self.painter.FilterHighFreqEdge=float(self.ui.lineEdit_FilterHighFreqEdge.text())
            self.painter.FFTPointsToCut=int(self.ui.lineEdit_FilterPointsToCut.text())
        else:
            self.painter.ApplyFFTFilter=False

    def on_stateChangeOfIsHighResolution(self):
        if self.OSA is not None:
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
        self.spectral_processor.ProcessedDataFolder=self.path_to_main+'\\ProcessedData\\'
        self.spectral_processor.Source_DirName=self.path_to_main+'\\SpectralData\\'
        self.spectral_processor.run()

    def on_pushButton_ProcessTD(self):
        from Scripts.ProcessAndPlotTD import ProcessAndPlotTD
        self.ProcessTD=ProcessAndPlotTD()
        Thread=self.add_thread([self.ProcessTD])
        self.ProcessTD.run(Averaging=self.ui.checkBox_processing_isAveraging.isChecked(),
            DirName='TimeDomainData',
            axis_to_plot_along=self.ui.comboBox_axis_to_plot_along.currentText(),
            channel_number=self.ui.comboBox_TD_channel_to_plot.currentIndex())
        Thread.quit()

    def plotSampleShape(self,DirName,axis):
        self.spectral_processor.plot_sample_shape()

    def save_parameters_to_file(self):
        '''
        save all parameters and values except paths to file

        Returns
        -------
        None.

        '''
        D={}
        D['MainWindow']=get_widget_values(self)
        D['Analyzer']=self.analyzer.get_parameters()
        D['Spectral_processor']=self.spectral_processor.get_parameters()
        D['Scanning_position_process']=self.scanningProcess.get_parameters()

        #remove all parameters that are absolute paths 
        for k in D:
            l=[key for key in list(D[k].keys()) if ('path' in key)]
            for key in l:
                del D[k][key]
        self.logger.save_parameters(D)
        
        
    def load_parameters_from_file(self):
        Dicts=self.logger.load_parameters()
        if Dicts is not None:
            try:
                set_widget_values(self, Dicts['MainWindow'])
                self.analyzer.set_parameters(Dicts['Analyzer'])
                self.spectral_processor.set_parameters(Dicts['Spectral_processor'])
                self.scanningProcess.set_parameters(Dicts['Scanning_position_process'])
            except KeyError:
                pass

    



    def choose_folder_for_spectral_processor(self):
        self.spectral_processor.source_dir_path = str(
            QFileDialog.getExistingDirectory(self, "Select Directory"))+'\\'
        self.spectral_processor.processedData_dir_path=os.path.dirname(
            os.path.dirname(self.spectral_processor.source_dir_path))+'\\'
        self.ui.label_folder_to_process_files.setText(self.spectral_processor.source_dir_path+'\\')
        
       

    def process_arb_spectral_data_clicked(self):
        Folder=self.spectral_processor.source_dir_path
        try:
            self.spectral_processor.StepSize=int(Folder[Folder.index('Step=')+len('Step='):len(Folder)])
        except ValueError:
            self.spectral_processor.StepSize=0
        self.spectral_processor.run()
            

    def process_arb_TD_data_clicked(self):
        from Scripts.ProcessAndPlotTD import ProcessAndPlotTD
        self.ProcessTD=ProcessAndPlotTD()
        Thread=self.add_thread([self.ProcessTD])
        self.ProcessTD.run(Averaging=self.ui.checkBox_processingArbData_isAveraging.isChecked(),
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
        
    def plot_ERV_from_file(self):
        DataFilePath= str(QFileDialog.getOpenFileName(
            self, "Select Data File",'','*.pkl')).split("\',")[0].split("('")[1]
        self.analyzer.plot_ERV_from_file(DataFilePath)
        
    

    def choose_file_for_analyzer(self):
        DataFilePath= str(QFileDialog.getOpenFileName(self, "Select Data File",'','*.pkl *.pkl3d *.SNAP' )).split("\',")[0].split("('")[1]
        if DataFilePath=='':
            print('file is not chosen or previous choice is preserved')
        self.analyzer.file_path=DataFilePath
        self.ui.label_analyzer_file.setText(DataFilePath)
        self.analyzer.load_data(DataFilePath)
       

    def choose_file_for_analyzer_plotting_parameters(self):
        FilePath= str(QFileDialog.getOpenFileName(
            self, "Select plotting parameters file",'','*.txt')).split("\',")[0].split("('")[1]
        if FilePath=='':
            FilePath=os.getcwd()+'\\plotting_parameters.txt'
        self.analyzer.plotting_parameters_file=FilePath
        self.ui.label_analyzer_plotting_file.setText(FilePath)
        
    def on_pushButton_set_analyzer_parameters(self):
        '''
        open dialog with analyzer parameters
        '''
        d=self.analyzer.get_parameters()
        from Windows.UIs.analyzer_dialogUI import Ui_Dialog
        analyzer_dialog = QDialog()
        ui = Ui_Dialog()
        ui.setupUi(analyzer_dialog)
        set_widget_values(analyzer_dialog,d)
        if analyzer_dialog.exec_() == QDialog.Accepted:
            params=get_widget_values(analyzer_dialog)
            self.analyzer.set_parameters(params)
   
    def on_pushButton_set_spectral_processor_parameters(self):
        '''
        open dialog with  parameters
        '''
        d=self.spectral_processor.get_parameters()
        from Windows.UIs.processing_dialogUI import Ui_Dialog
        dialog = QDialog()
        ui = Ui_Dialog()
        ui.setupUi(dialog)
        set_widget_values(dialog,d)
        if dialog.exec_() == QDialog.Accepted:
            params=get_widget_values(dialog)
            self.spectral_processor.set_parameters(params)
            
    def on_pushButton_set_scanning_parameters(self):
        '''
        open dialog with  parameters
        '''
        d=self.scanningProcess.get_parameters()
        from Windows.UIs.scanning_dialogUI import Ui_Dialog
        dialog = QDialog()
        ui = Ui_Dialog()
        ui.setupUi(dialog)
        set_widget_values(dialog,d)
        
        if dialog.exec_() == QDialog.Accepted:
            params=get_widget_values(dialog)
            self.scanningProcess.set_parameters(params)
            
            final_position=(self.scanningProcess.stop_file_index-self.scanningProcess.current_file_index)*self.scanningProcess.scanning_step+self.stages.relative_position[self.scanningProcess.axis_to_scan]
            self.ui.label_scanning_final_position.setText(str(final_position))
            self.ui.label_scanning_axis.setText(self.scanningProcess.axis_to_scan)

            
    def delete_data_from_folders(self):
        msg=QMessageBox(2, 'Warning', 'Do you want to delete all raw data?')

        msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        if msg.exec_():
            dirs=['\\SpectralData\\','\\SpectralBinData\\']
            for directory in dirs:
                l=os.listdir(self.path_to_main+directory)
                if '.gitignore' in l:l.remove('.gitignore')
                for file in l:
                    os.remove(self.path_to_main+directory+file)
            print('Raw data deleted')

        

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
            del self.powermeter
            print('powermeter is deleted')
        except:
            pass    
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
        del self.spectral_processor
        print('Processing is deleted')
        super(QMainWindow, self).closeEvent(event)
        

def get_widget_values(window)->dict:
    '''
    collect all data from all widgets in a window
    '''
    D={}
    for w in window.findChildren(QLineEdit):
        s=w.text()
        key=w.objectName().split('lineEdit_')[1]
        try:
            f=float(s) if '.' in s else int(s)
        except ValueError:
            f=s
        D[key]=f
    for w in window.findChildren(QCheckBox):
        f=w.isChecked()
        key=w.objectName().split('checkBox_')[1]
        D[key]=f
        
    for w in window.findChildren(QComboBox):
        s=w.currentText()
        key=w.objectName().split('comboBox_')[1]
        D[key]=s
    return D

def set_widget_values(window,d:dict)->None:
     for w in window.findChildren(QLineEdit):
         key=w.objectName().split('lineEdit_')[1]
         try:
             s=d[key]
             w.setText(str(s))
         except KeyError:
             print('error')
             pass
     for w in window.findChildren(QCheckBox):
         key=w.objectName().split('checkBox_')[1]
         try:
             s=d[key]
             w.setChecked(s)
             w.clicked.emit(s)
         except KeyError:
             print('error')
     for w in window.findChildren(QComboBox):
         key=w.objectName().split('comboBox_')[1]
         try:
             s=d[key]
             w.setCurrentText(s)
         except KeyError:
             pass
         

