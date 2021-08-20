'''The module describing the OVA5000 device'''
import socket
import time
from PyQt5.QtCore import QObject,pyqtSignal
import numpy as np

RESPONSE_TIMEOUT = 2 # seconds

BUFSIZE = 4096 # bytes


class Luna(QObject):
    '''The class for controlling the OVA5000'''
    class ResponseError(Exception):
        '''Exception that is thrown when where are response from a command or no
           response from query'''
    class ScanError(Exception):
        '''Exception that is thrown whrn there is a scan error'''
    received_spectrum = pyqtSignal(np.ndarray,list,list)

    def __init__(self, host='localhost', port=1):
        QObject.__init__(self)
        '''Setup a remote connection for OVA5000'''
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(RESPONSE_TIMEOUT)
        self.sock.connect((host, port))
        self._Span = 2.55
        self._Center = 1550
        self._StartWavelength=self._Center-self._Span/2
        self._StopWavelength=self._Center+self._Span/2


    def recvall(self):
        '''Recieve all symbols from server'''
        arr = self.sock.recv(BUFSIZE)
        while arr[-1] != 0:
            arr +=self.sock.recv(BUFSIZE)
        return arr.decode()

    def send_command(self, cmd):
        '''Send a command whish does not require response'''
        self.sock.send(str(cmd).encode())
        try:
            err = self.recvall()
        except socket.timeout:
            return
        raise self.ResponseError(f"Response: {err}\nConsidered as error: " +
                            "command should not have any response. If you expected " +
                            "a response from this command, please use send_query(cmd) method.")

    def send_query(self, cmd):
        '''Send a command which requres response'''
        self.sock.send(str(cmd).encode())
        try:
            return self.recvall()
        except socket.timeout as q_timeout:
            raise self.ResponseError("The command has no response.\nConsidered as error: " +
                            "query should have a response. If you didn't expect " +
                            "a response, please use send_command(cmd) method.") from q_timeout

    def send_auto(self, cmd):
        '''Send any kind of command'''
        if "?" in cmd:
            return self.send_query(cmd)
        try:
            self.send_command(cmd)
        except Exception as e:
            print(e)
        return None

    ########## Methods for integrate into scanloop ##########
    def acquire_spectrum(self, x_mode=0, y_mode=0):
        ''' 
        Scan data and return it tuple of two numpy arrays;
        y_mode=0 for insertion losses
        '''
        self.send_auto("SCAN")
        while self.send_auto("SYST:RDY?")[0] != '1':
            pass
        if self.send_auto("SYST:ERR?")[0] != '0':
            raise self.ScanError(self.send_auto("SYST:ERRD?"))
        x_raw = self.send_auto("FETC:XAXI? " + str(x_mode))
        y_raw = self.send_auto("FETC:MEAS? " + str(y_mode))
        x_final = np.array(x_raw[:-2].split('\r'),np.float64)
        y_final = np.array(y_raw[:-2].split('\r'),np.float64)
        self.received_spectrum.emit(x_final,list([y_final]),[0])
        return x_final, y_final

    def change_range(self, start_wavelength=None, stop_wavelength=None):
        '''Set the wavelength range'''
        if start_wavelength is None:
            start_wavelength=self._StartWavelength
        if stop_wavelength is None:
            stop_wavelength=self._StopWavelength
        self._Center = (start_wavelength + stop_wavelength)/2
        self._Span =  (stop_wavelength - start_wavelength)
        self._StartWavelength=start_wavelength
        self._StopWavelength=stop_wavelength
        self.send_auto("CONF:CWL "+ str(self._Center))
        self.send_auto("CONF:RANG " + str(self._Span))
        
    def save_binary(self, file_name):
        '''**Usage:** Save the currnt Jones matrix data in Matrix A as binary 
        data in the *filename.bin* specified. 
        
        An error flag will be set if no data is available to save. The cause of
        error can be determined by using the SYST:ERR? query.
        
        **Response:**   None.
        **Note**:  The file type ".bin" must be specified. This command always
        saves the data from Matrix A.
        
        **Example:**    save_binary("C:\SavedFiles\JM.bin") saves the data from
        matrix A into the file "JM.bin"
        '''
        self.send_auto(f'SYST:SAVJ "{file_name}"')
        
        
    #############################################

    def __del__(self):
        '''Close the TCP connection'''
        self.sock.send("*QUIT".encode())
        time.sleep(RESPONSE_TIMEOUT)
        self.sock.close()