# -*- coding: utf-8 -*-
"""
https://github.com/PI-PhysikInstrumente/PIPython
need:
PIPython
PyUSB
PySerial
PySocket

"""

__version__=0.1
__date__='24.04.2022'

CONTROLLERNAME = 'C-663.12'  # 
# CONTROLLERNAME = 'C-885'  # 
serial_numbers={'X':'0017550037','Y':'0017550079','Z':'0017550081'}

import time
from PyQt5.QtCore import QObject,  pyqtSignal
try:
    from pipython import GCSDevice
    from pipython import pitools
except ModuleNotFoundError as e:
    print(e)    
    print('Consider installing pipython using pip')

class PIStages(QObject):
    connected = pyqtSignal()
    stopped = pyqtSignal()
#    StepSize={'X':10,'Y':10,'Z':10}
    Stage_key={'X':None,'Y':None,'Z':None}
    abs_position={'X':0,'Y':0,'Z':0}
    relative_position={'X':0,'Y':0,'Z':0}
    zero_position={'X':0,'Y':0,'Z':0}
    
    def __init__(self):
        super().__init__()
        try:
            
            for k in self.Stage_key:
                pidevice = GCSDevice(CONTROLLERNAME)
                pidevice.ConnectUSB(serialnum=serial_numbers[k])
                self.Stage_key[k]=pidevice
            self.isConnected=1
        except:
            print('Error: not connected to '+str(CONTROLLERNAME))
            
        self.update_relative_positions()

    
    
    def set_zero_positions(self,l):
        self.zero_position['X']=l[0]
        self.zero_position['Y']=l[1]
        self.zero_position['Z']=l[2]
        self.update_relative_positions()
        
    def update_abs_positions(self):
        for k in self.abs_position:
            self.abs_position[k]=self.get_position(k)
    
    def update_relative_positions(self):
        self.update_abs_positions()
        for k in self.relative_position:
            self.relative_position[k]=round(self.abs_position[k]-self.zero_position[k],1)

        
    def get_position(self, key):
        '''
        returns
        position in microns
        '''
        return round(self.Stage_key[key].qPOS('1')['1']*1e3,2)
            
    
    def shiftOnArbitrary(self, key:str, distance:float):
        '''
        distance in microns!
        '''
        self.Stage_key[key].MVR('1',distance*1e-3)
        while not all(list(self.Stage_key[key].qONT('1').values())):
            # print(self.Stage_key[key].qONT('1').values())
            time.sleep(0.05)
        # pitools.waitontarget(self.Stage_key[key], '1')

        self.update_relative_positions()
        self.stopped.emit()
 



if __name__ == "__main__":
    stages=PIStages()
    a=stages.get_position('Z')
    print(a)
    
    #%%
    d=-50
    stages.shiftOnArbitrary('Z', d)
    b=stages.get_position('Z')
    print(b)

