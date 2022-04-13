# -*- coding: utf-8 -*-
"""
Created on Tue Apr 12 13:40:16 2022

@author: Ilya
"""
__date__='2022.04.12'

import matplotlib.pyplot as plt
import numpy as np
import collections
from PyQt5.QtCore import pyqtSignal,  QObject

class Powermeter_painter(QObject):
    updated=pyqtSignal()
    
    def __init__(self):
        super().__init__()
        
        self.N=1000 
        
        self.fig=None
        self.ax=None
        
        
    def create_plot(self):
        self.fig=plt.figure()
        self.ax=plt.gca()
        plt.xlabel('Time, s')
        plt.ylabel('Power, mW')
        self.powers=collections.deque(np.zeros(self.N))
        plt.tight_layout()
        
    def update_graph(self,power):
        self.ax.cla()
        # print(power)
        self.powers.popleft()
        self.powers.append(power)
        self.ax.plot(self.powers)
        self.ax.set_xlabel('Time, s')
        self.ax.set_ylabel('Power, mW')
            # ax1.text(len(ram)-1, ram[-1]+2, "{}%".format(ram[-1]))
        self.fig.canvas.draw_idle()
        # plt.pause(0.01)
        self.updated.emit()
        
    def delete_plot(self):
        plt.close(self.fig)
        del self.ax
        

if __name__=='__main__':
    print(0)
    
    import os 
    os.chdir('..')
    from Hardware.ThorlabsPM100 import PowerMeter
    p=Powermeter_painter()
    PM=PowerMeter('P0015055')
    p.powermeter=PM
    p.create_plot()
    p.update_graph(PM.get_power())

