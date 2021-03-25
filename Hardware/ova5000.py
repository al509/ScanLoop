'''The module describing the OVA5000 device'''
import socket
import time
import numpy as np

RESPONSE_TIMEOUT = 2 # seconds

BUFSIZE = 4096 # bytes


class Luna:
    '''The class for controlling the OVA5000'''
    class ResponseError(Exception):
        '''Exception that is thrown when where are response from a command or no
           response from query'''
    class ScanError(Exception):
        '''Exception that is thrown whrn there is a scan error'''


    def __init__(self, host='localhost', port=1):
        '''Setup a remote connection for OVA5000'''
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(RESPONSE_TIMEOUT)
        self.sock.connect((host, port))

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
        self.send_command(cmd)
        return None

    ########## Methods for integrate into scanloop ##########
    def acqire_data(self, x_mode, y_mode):
        '''Scan data and return it tuple of two numpy arrays'''
        self.send_auto("SCAN")
        while self.send_auto("SYST:RDY?")[0] != '1':
            pass
        if self.send_auto("SYST:ERR?")[0] != '0':
            raise self.ScanError(self.send_auto("SYST:ERRD?"))
        x_raw = self.send_auto("FETC:XAXI? " + str(x_mode))
        y_raw = self.send_auto("FETC:MEAS? " + str(y_mode))
        x_final = x_raw[:-2].split('\r')
        y_final = y_raw[:-2].split('\r')
        return np.array(x_final, np.float64), np.array(y_final, np.float64)

    def set_range(self, start_wavelength, end_wavelength):
        '''Set the wavelength range'''
        center = (start_wavelength + end_wavelength)/2
        rng =  (end_wavelength - start_wavelength)
        self.send_auto("CONF:CWL "+ str(center))
        self.send_auto("CONF:RANG " + str(rng))
        
    #############################################

    def __del__(self):
        '''Close the TCP connection'''
        self.sock.send("*QUIT".encode())
        time.sleep(RESPONSE_TIMEOUT)
        self.sock.close()
   
def main():
    print("Welcome to Luna OVA5000 Shell! Here you can enter any remote commads from Luna's manual.")
    
   
if __name__ == '__main__':
    main()