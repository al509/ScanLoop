# -*- coding: utf-8 -*-
"""

    tested on NI-VISA
by Artem Kirik
"""

import pyvisa
import struct
from sys import stdout
import time




def itla_message(b0 = 0, b1 = 0, b2 = 0, b3 = 0):
    bip8 = (b0 & 0x0f)^b1^b2^b3
    csb0 = ((bip8 & 0xf0) ^ ((bip8 & 0x0f) << 4)) | (b0 & 0x0f)
    return bytes((csb0, b1, b2, b3))

def m_Hz(m):
    return 299792458 / m


nop_err_list =[
        'register not implemented',
        'register not writable',
        'register value range error',
        'Command ignored due to pending operation',
        'Command ignored while module is initializing, warming up, or contains an invalid configuration',
        'Extended address range error',
        'Extended address is read only',
        'Execution general failure',
        'Command ignored while module’s optical output is enabled',
        'Invalid configuration, command ignored',
        'B',
        'C',
        'D',
        'E',
        'Vendor specific error']

class ITLA_Error(Exception):
    pass

class ImplementationError(ITLA_Error):
    def __init__(self):
        self.message = 'register not implemented'
    
class ITLA:
    
    def __init__(self, port, timeout = 2000, backend = None):
        if backend:
            self.resource = pyvisa.ResourceManager(backend).open_resource('ASRL{}::INSTR'.format(port), timeout = timeout)
        else:
            self.resource = pyvisa.ResourceManager().open_resource('ASRL{}::INSTR'.format(port), timeout = timeout)
        
        self.opsl = self.ask_value(0x50, '!h') # dBm * 100 
        self.opsh = self.ask_value(0x51, '!h') # dBm * 100 
        self.lfl1 = self.ask_value(0x52) # THz 
        self.lfl2 = self.ask_value(0x53) # GHz * 10
        self.lfh1 = self.ask_value(0x54) # THz 
        self.lfh2 = self.ask_value(0x55) # GHz * 10
        
        self.pwr_SetP = self.ask_value(0x31, '!h') # dBm * 100 
        self.fcf1 = self.ask_value(0x35) # THz
        self.fcf2 = self.ask_value(0x36) # GHz * 10

        self.enable = self.ask_value(0x32) & 8
        self.freq1 = self.ask_value(0x40) # THz
        self.freq2 = self.ask_value(0x41) # GHz * 10
        self.pwr = self.ask_value(0x42, '!h') # dBm * 100
        self.temp = self.ask_value(0x43, '!h') # dBm * 100 
        
        self.ftfr = self.ask_value(0x4f) # MHz
        self.ftf = self.ask_value(0x62,'!h') #MHz
       
       
    def state(self):
        self.channel = self.ask_value(0x30) # GHz * 10
        self.pwr_SetP = self.ask_value(0x31, '!h') # dBm * 100 
        self.fcf1 = self.ask_value(0x35) # THz
        self.fcf2 = self.ask_value(0x36) # GHz * 10
        self.grid = self.ask_value(0x34) # GHz * 10
        
        self.enable = self.ask_value(0x32) & 8
        self.freq1 = self.ask_value(0x40) # THz
        self.freq2 = self.ask_value(0x41) # GHz * 10
        self.pwr = self.ask_value(0x42, '!h') # dBm * 100
        self.temp = self.ask_value(0x43, '!h') # dBm * 100 
        
        self.ftf = self.ask_value(0x62,'!h') #MHz
        
        return self.__dict__
    
    def talk(self, rw = False, register = 0, data0 = 0, data1 = 0):
        msg = itla_message(int(rw), register, data0, data1)
        self.resource.write_raw(msg)
        rsp = self.resource.read_bytes(4)
        if itla_message(*rsp) != rsp:
            raise ITLA_Error('response checksum error')
            
        if rsp[0] & 8 == 8 :
            raise ITLA_Error('message checksum error')
        
        if rsp[0] & 3 == 1:
            err_code = self.talk()[3] & 0x0f    
            raise ITLA_Error(nop_err_list[err_code-1])
        return rsp
         
    def ask_value(self, register, fmt = '!H'):
        return struct.unpack(fmt ,  self.talk(0, register, 0, 0)[-2:])[0]
     
    def on(self,sleep_inc=1):
        rsp = self.talk(1, 0x32, 0, 8)
        #self.enable = rsp[-1] | 8
        return rsp
    
    def off(self):
        rsp = self.talk(1, 0x32, 0, 0)
        #self.enable = rsp[-1] | 8
        return rsp
    
    def set_power(self, pwr):
        # pwr in dBm*100
        rsp = self.talk(1, 0x31, *struct.pack('!h',pwr))
        #self.pwr_setP = pwr
        return rsp
    
    def set_frequency(self, frequency):
        freq = int(frequency) # Hz
        THz = freq// (10**12)
        freq = freq % (10**12)
        dGHz = freq // (10**8)
        thzResp = self.talk(1, 0x35, *struct.pack('!H',THz))
        self.fcf1 = THz
        dghzResp = self.talk(1, 0x36, *struct.pack('!H',dGHz))
        self.fcf2 = dGHz
        return thzResp, dghzResp
                  
    def set_FTFrequency(self, frequency):
        freq = int(frequency) #Hz 
        MHz = freq // (10**6)
        rsp = self.talk(1, 0x62, *struct.pack('!h', MHz))
        #self.ftf = MHz
        return rsp
        


class PPCL550(ITLA):
    def __init__(self, port, timeout = 2000, backend = None):
        super().__init__(port, timeout, backend)
        self.md = self.ask_value(0x90)
    
    def state(self):
        super().state()
        self.md = self.ask_value(0x90)
        return self.__dict__
        
        
    def mode(self, md):
        if not (self.ask_value(0x32) & 8):
            raise ITLA_Error('can be used only when emitting')
        modes = {
            'dither' : 0,
            'no dither' : 1,
            'whisper' : 2
            }
        return self.talk(1,0x90,0, modes[md])
        
        
           
if __name__ == '__main__':
    kek = PPCL550(12)
    kek.off()
    kek.on()
    kek.mode('no dither')
