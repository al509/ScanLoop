# -*- coding: utf-8 -*-
"""
Created on Fri Jul 24 14:47:14 2020

@author: stelt
modified by Ilya

Run as main() to see example process
"""

import pyvisa
import numpy as np
import time
from sys import stdout 

from PyQt5.QtCore import QObject, pyqtSignal     

__version__='2.1'
__date__='2023.04.25'

# class Wave:
#     def __init__(self, datA, xinC):
#         self.data = datA
#         self.xinc = xinC
        

class Scope(QObject):
    received_data = pyqtSignal(np.ndarray,list,list)
    def __init__(self, host, protocol = 'inst0', backend = None, timeout = 5000):
        super().__init__(parent=None)
        if backend:
            self.resource = pyvisa.ResourceManager(backend).open_resource('TCPIP0::'+host+'::'+protocol+'::INSTR')
        else:
            self.resource = pyvisa.ResourceManager().open_resource('TCPIP0::'+host+'::'+protocol+'::INSTR')
        self.resource.timeout = timeout
        
        stdout.write(str(self.query_string('*IDN?')+b'\n'))
        
        self.set_wfm_mode('RAW') #for all data in memory
        self.set_wfm_format('BYTE')
        self.channels_states=[False,False,False,False]
        for ii in [1,2,3,4]:
            self.channels_states[ii-1]=self.get_channel_state(ii)
    """      
    def err_code(self):
        self.resource.write_raw(b':SYSTem:ERRor?')
        resp = self.resource.read_raw()[:-1]
        if b':SYST:ERR ' in resp:
            return int(resp[10:])
        else:
            return int(resp)
    """   
    
    def clear(self):
        """
        use if all is fucked
        """
        self.resource.write_raw(b'*CLS')
        
    """
    def err_corr(self):
        if self.err_code():
            self.clear()
            return 1
        else:
            return 0
    """
    
    def command(self, command):
         #self.err_corr()
         return self.resource.write_raw(bytes(command, encoding = 'utf8'))
     
    def read(self):
        return self.resource.read_raw()
     
    def query_string(self, command):
        #self.err_corr()
        if not command[-1] == '?':
            raise RuntimeError('query with no question mark')
        self.resource.write_raw(bytes(command, encoding = 'utf8'))
        return self.resource.read_raw()[:-1]
        
    def query_wave_fast(self):
        self.resource.write_raw(b":WAVeform:PREamble?")
        preamble = self.resource.read_raw()
        (wav_form, acq_type, wfmpts, avgcnt, x_increment, x_origin,
         x_reference, y_increment, y_origin, y_reference) = preamble.split(b",")
        self.resource.write_raw(b"WAVeform:STARt 1")
        self.resource.write_raw(bytes("WAVeform:STOP {}".format(int(wfmpts)), encoding = 'utf8'))
        origins = np.array(list(map(float,(x_increment, x_origin, y_increment, y_origin))), dtype = 'f')
        self.resource.write_raw(b':WAVeform:DATA?')
        raw = self.resource.read_raw()[11:-1]
        wave = ((np.frombuffer(raw, dtype = np.uint8)).astype(np.int16) - int(y_reference)) * origins[2] + origins[3]
        return wave,origins[0],origins[1]
    
    """
    def set_acquisition_type(self, typ = 'NORMal'):
        #NORMal
        #AVERages
        #PEAK
        #HRESolution
        self.resource.write_raw(bytes(':ACQuire:TYPE {}'.format(typ), encoding = 'utf8'))
    
    def get_acquisition_type(self):
        return self.query_string(':ACQuire:TYPE?')
    
    def set_average_count(self, average_count  = 2):
        #2 to 65536
        self.resource.write_raw(bytes(':ACQuire:AVERages {}'.format(average_count), encoding = 'utf8'))
        
    def get_average_count(self):
        return self.query_string(':ACQuire:AVERages?')
    """
    def set_wfm_source(self, ch_num = 1, source_str = None):
        if source_str:
            self.resource.write_raw(bytes(':WAVeform:SOURce {}'.format(source_str), encoding = 'utf8'))
        else:
            self.resource.write_raw(bytes(':WAVeform:SOURce CHAN{}'.format(ch_num), encoding = 'utf8'))
    def get_wfm_source(self):
        return self.query_string(':WAVeform:SOURce?')       
    
    def set_wfm_mode(self, mode = 'RAW'):
        self.resource.write_raw(bytes(':WAVeform:MODE {}'.format(mode), encoding = 'utf8'))
    
    def get_wfm_mode(self):
        return self.query_string(':WAVeform:MODE?')
    
    def set_wfm_format(self, fmt = 'BYTE'):
        self.resource.write_raw(bytes(':WAVeform:FORMat {}'.format(fmt), encoding = 'utf8'))
    
    def get_wfm_format(self):
        return self.query_string(':WAVeform:FORMat?')
    
    def set_memory_depth(self, depth = 'AUTO'):
        if depth == 'AUTO':
            self.resource.write_raw(bytes(':ACQuire:MDEPth {}'.format(depth), encoding = 'utf8'))
        else:
            depths = [(1000, '1k'),
                      (10000, '10k'),
                      (100000, '100k'),
                      (1000000, '1M'),
                      (10000000, '10M'),
                      (25000000, '25M'),
                      (50000000, '50M'),
                      (100000000, '100M'),
                      (125000000, '125M'),
                      (250000000, '250M'),
                      (500000000, '500M')]
            npd = np.array([1000,
                            10000,
                            100000,
                            1000000,
                            10000000,
                            25000000,
                            50000000,
                            100000000,
                            125000000,
                            250000000,
                            500000000])
            closest = np.argmin(np.abs(npd - depth))
            self.resource.write_raw(bytes(':ACQuire:MDEPth {}'.format(depths[closest][1]), encoding = 'utf8'))
        self.resource.write_raw(b':RUN')
        self.resource.write_raw(b':STOP')
        
    def get_memory_depth(self):
        return self.query_string(':ACQuire:MDEPth?')
    
    def set_channel_on(self, channel = 1):
        self.resource.write_raw(bytes(':CHANnel{}:DISPlay 1'.format(channel), encoding = 'utf8'))
        
    def set_channel_off(self, channel = 1):
        self.resource.write_raw(bytes(':CHANnel{}:DISPlay 0'.format(channel), encoding = 'utf8'))
        
    def get_channel_state(self,channel_number):
        a=self.resource.query(':CHANnel'+str(channel_number)+':DISPlay?')
        return bool(int(a))

    def set_channel_state(self,channel_number,IsOn:bool):
        if IsOn:
            self.resource.write(':CHANnel'+str(channel_number)+':DISPlay ON')
        else:
            self.resource.write(':CHANnel'+str(channel_number)+':DISPlay OFF')
        
    def set_channel_coupling(self, channel = 1, coupling = 'DC'):
        #DC
        #AC
        self.resource.write_raw(bytes(':CHANnel{}:COUPling {}'.format(channel, coupling), encoding = 'utf8'))
        
    def get_channel_coupling(self, channel = 1):
        return self.query_string(':CHANnel{}:COUPling?'.format(channel))
        
    def set_channel_impedance(self, channel = 1, impedance = 'FIFTy'):
        #FIFTy for 50 Ohm
        #OMEG for 1 MOhm
        self.resource.write_raw(bytes(':CHANnel{}:IMPedance {}'.format(channel, impedance), encoding = 'utf8'))
        
    def get_channel_impedance(self, channel = 1):
        return self.query_string(':CHANnel{}:IMPedance?'.format(channel))
    
    """
    def set_trigger_type(self, trigger = 'AUTO'):
        #AUTO
        #NORMal
        #SINGle
        self.resource.write_raw(bytes(':TRIGger:SWEep {}'.format(trigger), encoding = 'utf8'))
        
    def get_trigger_type(self):
        return self.query_string(':TRIGger:SWEep?')
    """
    
    def get_wfm_raw_preamble(self):
        self.resource.write_raw(b":WAVeform:PREamble?")
        return self.resource.read_raw()
 
    def acquire(self, timeout = np.inf, sleep_step = 2):
        """
        Acquire trace using current setup.
        Default timeout is infinite, every ~5 sec a message is written to stdout
        """
        #self.err_corr()
        self.resource.write_raw(b':Single')
        i = 0
        t0 = time.time()
        while time.time() - t0 < timeout:
            if int(self.query_string('*OPC?')):
                stdout.write('Acquisition complete\n')
                break
            else:
                i+=1
                if i % 500 == 0:
                    #if int(self.query_string(':ACQuire:AVERage?')):
                    #    stdout.write('Averaging... \n')
                    #else:
                        stdout.write('Are you sure your trigger setup is correct?\n')
                time.sleep(sleep_step)
        else:
            raise RuntimeError('Acquisition timeout')
        Y=list()
        channel_numbers=list()
        for enum,channel in enumerate(self.channels_states):
            if channel:
#                Test=self.get_y_data(enum+1)
                self.set_wfm_source(enum+1)
                data,x_inc,x_0=self.query_wave_fast()
                Y.append(data)
                channel_numbers.append(enum+1)
                print(enum,len(data),x_inc,x_0)
        X=x_0+x_inc*np.arange(len(data))
        self.received_data.emit(X,Y,channel_numbers)
    
    
    def acquire_and_return(self,ch_num):
        self.acquire(sleep_step=2)
        self.set_wfm_source(ch_num)
        return self.query_wave_fast()
        
    def get_data(self,ch_num):
        self.set_wfm_source(ch_num)
        return self.query_wave_fast()
    
    
                
if __name__ == '__main__':
    import matplotlib.pyplot as plt
    ch = 1
    scope = Scope('192.168.0.47')
    a=scope.acquire()
# #%%
#     """
#     averaging needs to be turned on\off manually
#     """
#     scope.set_wfm_mode('RAW') #for all data in memory
#     print(scope.get_wfm_mode())
#     scope.set_wfm_format('BYTE')
#     print(scope.get_wfm_format())#currently only format supported for downloading
#     #anyway 8 bit only
# #%%
#     scope.set_channel_on(ch)
#     scope.set_channel_coupling(ch, 'DC') # 'DC' ot 'AC'
#     print(scope.get_channel_coupling(ch))
#     scope.set_channel_impedance(ch, 'OMEG') # 'FIFTy' for 50 'OMEG' for 1M
#     print(scope.get_channel_impedance(ch))
#     scope.set_wfm_source(ch)
#     print(scope.get_wfm_source())
#     scope.set_memory_depth(2000000)
#     print(scope.get_memory_depth())
# #%%
#     scope.acquire()
#     wave = scope.query_wave_fast()
#     plt.plot(wave.data)


    