from PyQt5.QtCore import QObject,  pyqtSignal
import sys
import os
import numpy as np



OldPath=os.getcwd()
#    if (os.path.dirname(sys.argv[0])+'/Hardware') not in sys.path:
#        sys.path.append(os.path.dirname(sys.argv[0])+'/Hardware')
if __name__ != "__main__":
#    os.chdir(os.path.dirname(sys.argv[0])+'/Hardware')
    os.chdir(os.path.dirname(__file__))
if sys.version_info >= (3,0):
    import urllib.parse
try:
    from pyximc import *
except ImportError as err:
    print ("Can't import pyximc module. The most probable reason is that you haven't copied pyximc.py to the working directory. See developers' documentation for details.")
    exit()
except OSError as err:
    print ("Can't load libximc library. Please add all shared libraries to the appropriate places (next to pyximc.py on Windows). It is decribed in detailes in developers' documentation.")
    exit()
#def command_move(device_id, Position, uPosition)
# variable 'lib' points to a loaded library
# note that ximc uses stdcall on win

print("Library loaded")
os.chdir(OldPath)


class Stages(QObject):
    connected = pyqtSignal()
    stopped = pyqtSignal()
#    StepSize={'X':10,'Y':10,'Z':10}
    Stage_key={'X':None,'Y':None,'Z':None}
    position={'X':0,'Y':0,'Z':0}

    def __init__(self):
        super().__init__()
        self.lib=lib
        self.IsConnected=0
        sbuf = create_string_buffer(64)
        self.lib.ximc_version(sbuf)
        print("Library version: " + sbuf.raw.decode())

        # This is device search and enumeration with probing. It gives more information about devices.
        devenum = self.lib.enumerate_devices(EnumerateFlags.ENUMERATE_PROBE, None)
        print("Device enum handle: " + repr(devenum))
        print("Device enum handle type: " + repr(type(devenum)))

        dev_count = self.lib.get_device_count(devenum)
        print("Device count: " + repr(dev_count))
        self.IsConnected=dev_count

        controller_name = controller_name_t()
        for dev_ind in range(0, dev_count):
            enum_name = self.lib.get_device_name(devenum, dev_ind)
            result = self.lib.get_enumerate_device_controller_name(devenum, dev_ind, byref(controller_name))
            if result == Result.Ok:
                print("Enumerated device #{} name (port name): ".format(dev_ind) + repr(enum_name) + ". Friendly name: " + repr(controller_name.ControllerName) + ".")

        open_name = None
        if len(sys.argv) > 1:
            open_name = sys.argv[1]
        elif dev_count > 0:
            open_name = self.lib.get_device_name(devenum, 0)
            open_name_1 = self.lib.get_device_name(devenum, 1)
            open_name_2 = self.lib.get_device_name(devenum, 2)
        elif sys.version_info >= (3,0):
            # use URI for virtual device when there is new urllib python3 API
            tempdir = tempfile.gettempdir() + "/testdevice.bin"
            if os.altsep:
                tempdir = tempdir.replace(os.sep, os.altsep)

            tempdir1 = tempfile.gettempdir() + "/testdevice1.bin"
            if os.altsep:
                tempdir1 = tempdir1.replace(os.sep, os.altsep)

            tempdir2 = tempfile.gettempdir() + "/testdevice2.bin"
            if os.altsep:
                tempdir2 = tempdir2.replace(os.sep, os.altsep)
            # urlparse build wrong path if scheme is not file
            uri = urllib.parse.urlunparse(urllib.parse.ParseResult(scheme="file", \
                    netloc=None, path=tempdir, params=None, query=None, fragment=None))
            open_name = re.sub(r'^file', 'xi-emu', uri).encode()

            uri1 = urllib.parse.urlunparse(urllib.parse.ParseResult(scheme="file", \
                    netloc=None, path=tempdir1, params=None, query=None, fragment=None))
            open_name_1 = re.sub(r'^file', 'xi-emu', uri1).encode()

            uri2 = urllib.parse.urlunparse(urllib.parse.ParseResult(scheme="file", \
                    netloc=None, path=tempdir2, params=None, query=None, fragment=None))
            open_name_2 = re.sub(r'^file', 'xi-emu', uri2).encode()

        if not open_name:
            exit(1)
        if not open_name_1:
            exit(1)
        if not open_name_2:
            exit(1)

        if type(open_name) is str:
            open_name = open_name.encode()
        if type(open_name_1) is str:
            open_name_1 = open_name_1.encode()
        if type(open_name_2) is str:
            open_name_2 = open_name_2.encode()

        print("\nOpen device " + repr(open_name))
        self.Stage_key['X'] = self.lib.open_device(open_name)
#        print("Device id: " + repr(Stage_X))

        print("\nOpen device " + repr(open_name_1))
        self.Stage_key['Z'] = self.lib.open_device(open_name_1)
#        print("Device id_1: " + repr(Stage_Z))


        print("\nOpen device " + repr(open_name_2))
        self.Stage_key['Y'] = self.lib.open_device(open_name_2)
#        print("Device id_2: " + repr(Stage_Y))
        self.position['X']=self.get_position(self.Stage_key['X'])
        self.position['Y']=self.get_position(self.Stage_key['Y'])
        self.position['Z']=self.get_position(self.Stage_key['Z'])

    def get_info(self, device_id):
        print("\nGet device info")
        x_device_information = device_information_t()
        result = self.lib.get_device_information(device_id, byref(x_device_information))
        print("Result: " + repr(result))
        if result == Result.Ok:
            print("Device information:")
            print(" Manufacturer: " +
                    repr(string_at(x_device_information.Manufacturer).decode()))
            print(" ManufacturerId: " +
                    repr(string_at(x_device_information.ManufacturerId).decode()))
            print(" ProductDescription: " +
                    repr(string_at(x_device_information.ProductDescription).decode()))
            print(" Major: " + repr(x_device_information.Major))
            print(" Minor: " + repr(x_device_information.Minor))
            print(" Release: " + repr(x_device_information.Release))

    def get_status(self, device_id):
        print("\nGet status")
        x_status = status_t()
        result = self.lib.get_status(device_id, byref(x_status))
        print("Result: " + repr(result))
        if result == Result.Ok:
            print("Status.Ipwr: " + repr(x_status.Ipwr))
            print("Status.Upwr: " + repr(x_status.Upwr))
            print("Status.Iusb: " + repr(x_status.Iusb))
            print("Status.Flags: " + repr(hex(x_status.Flags)))

    def get_position(self, device_id):
        x_pos = get_position_t()
        result = self.lib.get_position(device_id, byref(x_pos))
        return x_pos.Position

    def move_left(self, device_id):
        print("\nMoving left")
        result = self.lib.command_left(device_id)
        print("Result: " + repr(result))

    def move_right(self, device_id):
        print("\nMoving left")
        result = self.lib.command_right(device_id)
        print("Result: " + repr(result))

    def shiftOnArbitrary(self, key:str, distance:int):
        device_id=self.Stage_key[key]
        result = self.lib.command_movr(device_id, distance, 0)
#        if (result>-1):
        lib.command_wait_for_stop(device_id, 11)
        self.position[key]=self.get_position(device_id)
        self.stopped.emit()

#    def shift(self, key:str,Sign_key):
#        device_id=self.Stage_key[key]
#        distance=int(np.sign(Sign_key)*self.StepSize[key])
#        print(distance)
#        result = self.lib.command_movr(device_id, distance, 0)
#        if (result>-1):
#            self.Position[key]+=distance
#        print("Result: Shifted - " + str(bool(result+1)))
#        self.stopped.emit()

    def wait_for_stop(self, device_id, interval):
        print("\nWaiting for stop")
        result = self.lib.command_wait_for_stop(device_id, interval)
        print("Result: " + repr(result+1))

    def get_serial(self, device_id):
        print("\nReading serial")
        x_serial = c_uint()
        result = self.lib.get_serial_number(device_id, byref(x_serial))
        if result == Result.Ok:
            print("Serial: " + repr(x_serial.value))

    def __del__(self):
        self.lib.close_device(byref(cast(self.Stage_key['X'], POINTER(c_int))))
        self.lib.close_device(byref(cast(self.Stage_key['Y'], POINTER(c_int))))
        self.lib.close_device(byref(cast(self.Stage_key['Z'], POINTER(c_int))))


if __name__ == "__main__":
    stages=Stages()
    d=5
    stages.shiftOnArbitrary('X',d)

    del stages

#################################### CLOSE CONNECTION #######################################



#plt.grid(True)
#plt.plot(Data[1], Data[0])
#plt.xlabel("Wavelength (nm)")
#plt.ylabel("Power (dBm)")
#plt.show()
