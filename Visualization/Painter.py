__date__='2022.04.12'

from PyQt5 import QtWidgets

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5 import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import numpy as np
import time
import collections
from scipy.fftpack import rfft, irfft, fftfreq

from Utils.PyQtUtils import pyqtSlotWExceptions
from PyQt5.QtCore import pyqtSignal



class Painter(QtWidgets.QWidget):


    def __init__(self, parent=None):
        super().__init__(parent)

        # a figure instance to plot on
        self.figure = Figure()
        self.ax=self.figure.add_subplot(111)
        # this is the Canvas Widget that displays the `figure`
        # it takes the `figure` instance as a parameter to __init__
        self.canvas = FigureCanvas(self.figure)
        # this is the Navigation widget
        # it takes the Canvas widget and a parent
        self.toolbar = NavigationToolbar(canvas=self.canvas, parent=parent)


        # set the layout
        if parent.layout() is not None:
            parent.layout().addWidget(self.canvas)
        else:
            layout = QtWidgets.QGridLayout(parent)
            layout.addWidget(self.canvas)
        layout.addWidget(self.toolbar)


class MyPainter(Painter):
    ReplotEnded=pyqtSignal()
    powermeter_canvas_updated=pyqtSignal()


    def __init__(self, parent=None):
        super().__init__(parent)
        self.Ydata =[None]*4
        self.Xdata=None
        self.channel_states=None
#        self.range=[1500, 1600]
#        self.ax.set_xbound((self.range[0],self.range[1]))
        self.savedX=None
        self.savedY=[None]*4
        self.ApplyFFTFilter=False
        self.FilterLowFreqEdge=0
        self.FilterHighFreqEdge=0
        self.FFTPointsToCut=20
        self.TypeOfData='FromOSA'
        
    def FFTFilter(self,y_array):
        W=fftfreq(y_array.size)
        f_array = rfft(y_array)
        Indexes=[i for  i,w  in enumerate(W) if all([abs(w)>self.FilterLowFreqEdge,abs(w)<self.FilterHighFreqEdge])]
        f_array[Indexes] = 0
#        f_array[] = 0
        return irfft(f_array)

    def set_color(self, channel_num: int) -> None:
        self.Color='C'+str(channel_num)


#    @pyqtSlotWExceptions("PyQt_PyObject")
    def set_data(self, Xdata: np.ndarray,Ydata:list,channel_numbers:list):
#        if len(channel_numbers)>1:
        self.Ydata =[None]*4
        for jj,num in enumerate(channel_numbers):
            if not self.ApplyFFTFilter:
                self.Ydata[num-1] = Ydata[jj]
            else:
                self.Ydata[num-1] = self.FFTFilter(Ydata[jj])[self.FFTPointsToCut:-self.FFTPointsToCut]
#        else:
#              if not self.ApplyFFTFilter:
#                  self.Ydata[channel_numbers[0]] = Ydata
#              else:
#                  self.Ydata[channel_numbers[0]] = self.FFTFilter(Ydata)[self.FFTPointsToCut:-self.FFTPointsToCut]

        if not self.ApplyFFTFilter:
            self.Xdata=Xdata
        else:
            self.Xdata=Xdata[self.FFTPointsToCut:-self.FFTPointsToCut]
        self.replot()




    @pyqtSlotWExceptions()
    def replot(self):
        self.ax.clear()
        for ii,value1 in enumerate(self.savedY):
            if value1 is not None:
                self.ax.plot(self.savedX, value1, color='black')
        for jj,value in enumerate(self.Ydata):
            if value is not None:
                self.ax.plot(self.Xdata,value, color='C'+str(jj))
        if self.TypeOfData=='FromOSA':
            self.ax.set_xlabel('Wavelength, nm')
            self.ax.set_ylabel('Spectral power density, dBm')
        elif self.TypeOfData=='FromScope':
            self.ax.set_xlabel('Time, s')
            self.ax.set_ylabel('Signal, V')
        self.canvas.draw()

        self.ReplotEnded.emit()
        
       
        
    def create_powermeter_plot(self):
        self.powermeter_plot_N=200
        # if self.powermeter_fig
        
        self.powermeter_fig=plt.figure()
        self.powermeter_ax=self.powermeter_fig.gca()
        self.powermeter_ax.set_xlabel('Time, s')
        self.powermeter_ax.set_ylabel('Power, W')
        temp=np.empty(self.powermeter_plot_N)
        temp[:]=np.nan
        self.powers=collections.deque(temp)
        self.times=collections.deque(np.zeros(self.powermeter_plot_N))
        self.powermeter_canvas = FigureCanvas(self.powermeter_fig)
        self.powermeter_canvas.draw()
        self.time0=time.time()

        
    def update_powermeter_plot(self,power,time):
        self.powermeter_ax.clear()
        # print(power)
        self.powers.popleft()
        self.powers.append(power)
        self.times.popleft()
        self.times.append(time-self.time0)
        self.powermeter_ax.plot(self.times,self.powers)
        self.powermeter_ax.set_xlabel('Time, s')
        self.powermeter_ax.set_ylabel('Power, W')
            # ax1.text(len(ram)-1, ram[-1]+2, "{}%".format(ram[-1]))
        self.powermeter_canvas.draw()
        plt.pause(0.02)
        self.powermeter_canvas_updated.emit()
        
    def delete_powermeter_plot(self):
        plt.close(self.powermeter_fig)
        
        


if __name__=='__main__':
    print(0)


