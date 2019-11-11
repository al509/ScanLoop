# -*- coding: utf-8 -*-
"""
Created on Sat Mar 23 21:03:02 2019
You need NI-VISA, PyVISA>1.6 to use this.
Data is transferred using BINARY format
"""


import pyvisa
import numpy as np


from PyQt5.QtCore import QObject, pyqtSignal

class Scope(QObject):
    
    received_data = pyqtSignal(np.ndarray,list,list)
    waiting_time=0.1

    def __init__ (self, host):
        super().__init__(parent=None)
        rm=pyvisa.ResourceManager('@py')
#        self.device=rm.open_resource('TCPIP::'+host+'::hislip0,4880::INSTR')
#        self.device=rm.open_resource('TCPIP0::WINDOWS-E76DLEM::hislip0,4880::INSTR')
        self.device=rm.open_resource('TCPIP0::WINDOWS-E76DLEM::inst0::INSTR')
        self.device.timeout=10000
        self.device.write(":WAV:FORMAT WORD")
        self.device.write(":WAV:BYTEORDER MSBF") # Set the byte order to Big-Endian (default for Infinium oscilloscopes)
        self.device.read_termination = None # '\n' # Since we're transferring binary data we need to remove the newline read termination
        self.device.write(":WAVeform:STReaming ON")
        self.device.chunk_size=1024
#        self.device=rm.open_resource('TCPIP::WINDOWS-E76DLEM.local::hislip0::INSTR')
#        self.device.write(":WAV:FORMAT ASCII")
        self.channels_states=[False,False,False,False]
        for ii in [1,2,3,4]:
            self.channels_states[ii-1]=self.get_channel_state(ii)
            

##        self.device.read_termination = None # Since we're transferring binary data we need to remove the newline read termination
#    
#    def wait_for_armed_1(self):    
#        # Method 1: Determine if armed using :AER? query.
#        # --------------------------------------------------------------------
#        # Define armed criteria.
#        ARMED = 1
#        # Test for armed.
#        ARMED_STATUS = int(self.device.query(":AER?"))
#        # Wait indefinitely until armed.
#        while ARMED_STATUS != ARMED:
#            # Check the status again after small delay.
#            print(1)
#            time.sleep(self.waiting_time) # 100 ms delay to prevent excessive queries.
#            ARMED_STATUS = int(self.device.query(":AER?"))
#        
#        
#    def wait_for_armed_3(self):
#        # Method 3: Determine if armed using :OPER? query.
#        # --------------------------------------------------------------------
#        # Define register bit masks for the Operation Status Register
#        
#        # Test for armed.
#        ARM_BIT = 5
#        # 1 leftshift 5 = 32 (bit 5 in the Operation Status Register)
#        ARM_MASK = 1 << ARM_BIT
#        # Define armed criteria.
#        ARMED = 1 << ARM_BIT # 1 leftshift 5 = 32
#
#        STATUS_REGISTER = int(self.device.query(":OPER?"))
#        ARMED_STATUS = STATUS_REGISTER & ARM_MASK
#        # Wait indefinitely until armed.
#        while ARMED_STATUS != ARMED:
#            # Check the status again after small delay.
#            print(1)
#            time.sleep(self.waiting_time) # 100 ms delay to prevent excessive queries.
#            STATUS_REGISTER = int(self.device.query(":OPER?"))
#            ARMED_STATUS = STATUS_REGISTER & ARM_MASK
#            
#    def wait_for_armed_2(self):
#            # Method 2: Determine if armed by reading the Status Byte.
#            # --------------------------------------------------------------------
#            # Define register bit masks for the Status Byte Register
#            ARM_BIT = 7
#            # 1 leftshift 7 = 128 (bit 7 in the Status Byte Register)
#            ARM_MASK = 1 << ARM_BIT
#            # Define armed criteria.
#            ARMED = 1 << ARM_BIT # 1 leftshift 7 = 128
#            # Test for armed.
#            STATUS_BYTE = int(self.device.read_stb())
#            ARMED_STATUS = STATUS_BYTE & ARM_MASK
#            # Note that you could also do:
#            # ARMED_STATUS = int(KsInfiniiumScope.query("*STB?))
#            # BUT *STB? does not work with the blocking :DIGitize.
#            # Wait indefinitely until armed.
#            while ARMED_STATUS != ARMED:
#                # Check the status again after small delay.
#                time.sleep(self.waiting_time) # 100 ms delay to prevent excessive queries.
#                STATUS_BYTE = int(self.device.read_stb())
#                ARMED_STATUS = STATUS_BYTE & ARM_MASK
#        
#    
#    def readdata(self):
#        self.device.write( ":WAVeform:DATA?" )#; /* Request waveform data */
##/* Find the # character */
#        while cData is not '#':
#        self.device.read_raw()
#/* Find the 0 character */
#do
#{
#ReadByte( &cData, 1L );
#} while ( cData != '0' );
#}
    
    def clear(self):
        self.device.query('*CLS;*OPC?')
    
    def single(self):
        self.clear()
        try:        
            current_time_out=self.device.timeout
            self.device.timeout=40000
            self.device.write(':DIGitize')
            self.device.query('*OPC?')    
            self.device.timeout=current_time_out
        except Exception:
            print("The acquisition timed out, most likely due to no " \
                  "trigger or improper setup causing no trigger. " \
                  "Properly closing the oscilloscope connection and " \
                  "exiting script.\n")

#        self.device.query('*OPC?')
#        self.wait_for_armed_1()
        

    def digitize_channel(self,channel_num:int):
        self.device.write(":DIGitize CHANnel"+str(channel_num))
        self.device.query('*OPC?')
        
    def get_channel_state(self,channel_number):
        a=self.device.query(':CHANnel'+str(channel_number)+':DISPlay?')
        return bool(int(a))
    
    def set_channel_state(self,channel_number,IsOn:bool):
        if IsOn:
            self.device.write(':CHANnel'+str(channel_number)+':DISPlay ON')
        else:
            self.device.write(':CHANnel'+str(channel_number)+':DISPlay OFF')

    
    def set_waiting_for_acquisition_averaging(self,IsSet:bool):
        if IsSet:
            self.device.write(':ACQuire:COMPlete:STATe ON')
        else:
            self.device.write(':ACQuire:COMPlete:STATe OFF')

    def get_waiting_for_acquisition_averaging(self):
        self.device.write(':ACQuire:COMPlete:STATe?')
        return bool(int(self.device.read()))

    def set_averaging_number(self,number:int):
        Command=':ACQuire:AVERage:COUNt '+str(number)
        self.device.write(Command)

    def set_averaging_state(self,Averaging:bool):
        if Averaging:
#            self.device.query(':ACQuire:COMPlete 50')
            self.device.write(':ACQuire:AVERage ON')
        else:
            self.device.write(':ACQuire:AVERage OFF')
        

    def get_averaging_state(self):
        self.device.write(':ACQuire:AVERage?')
        return bool(int(self.device.read()))

    def get_averaging_number(self):
        self.device.write(':ACQuire:AVERage:COUNt?')
        return int(self.device.read())
    
    def get_number_of_points(self):
        a=int(self.device.query(':WAVeform:POINts?'))
#        self.device.query('*OPC?')
        return a
    
    def set_time_range(self,time_range:float):
#        time_range in seconds
        return self.device.query(':TIMebase:RANGe '+format(time_range,'.4E')+';*OPC?')
    
    def get_sampling_rate(self):
#        time_range in seconds
        return float(self.device.query(':ACQuire:SRATe?'))

    
    def get_y_data(self,channel_number:int):
        self.device.query(':WAVeform:SOURce CHANnel'+str(channel_number)+';*OPC?')
        y_inc = float(self.device.query(":WAV:YINC?"))
        y_or = float(self.device.query(":WAV:YOR?"))
        wfm=0
        self.device.query('*OPC?')
        while np.size(wfm)<2:
            try:
                wfm=self.device.query_binary_values(":WAV:DATA?", 'h',container = np.array, is_big_endian = True)
            except pyvisa.errors.VisaIOError:
                print('VisaIOError. Trying to get data from scope again')
        return wfm*y_inc + y_or
        
    
    def get_x_data(self):
        Number=self.get_number_of_points()
        x_inc = float(self.device.query(":WAV:XINC?")) # Get the waveform's X increment
        x_or = float(self.device.query(":WAV:XOR?")) # Get the waveform's X origin
#        self.device.query('*OPC?')
        return np.arange(0,Number)*x_inc+x_or
    
    def acquire(self):
        self.single()
        Y=list()
        channel_numbers=list()
        for enum,channel in enumerate(self.channels_states):
            if channel:
#                Test=self.get_y_data(enum+1)
                Test=self.get_y_data(enum+1)
                Y.append(Test)
                channel_numbers.append(enum+1)
        X=self.get_x_data()
        self.received_data.emit(X,Y,channel_numbers)
        return X,Y,channel_numbers
        
                
        
    
    def close(self):
        self.device.close()

if __name__ == "__main__":
    import matplotlib.pyplot as plt

    HOST = '10.2.60.27'
    scope=Scope(HOST)
    print('Channels that are ON:',scope.channels_states)
    scope.set_time_range(50e-9)
    print(scope.get_number_of_points())
    scope.set_averaging_state(True)
    scope.set_averaging_number(256)
    X,Y,ch=scope.acquire()
    temp=scope.get_sampling_rate()
    plt.plot(X,Y[0])
#    scope.device.write(':Wav:Format WORD')
#    scope.device.write(':Wav:Format ASCII')
#    scope.device.query(':Wav:Form?')
    
#    scope.get_averaging_state()

#    scope.get_averaging_number()
    
    scope.close()
