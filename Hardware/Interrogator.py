from PyQt5.QtCore import QObject, QThread, pyqtSignal

import numpy as np
import os
if __name__ is "__main__":
    os.chdir('..')
from Hardware.SyncSocket import SyncSocket
from Utils.PyQtUtils import pyqtSlotWExceptions
from Common.Consts import Consts

import itertools


def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = itertools.tee(iterable)
    next(b, None)
    return a, b


class Interrogator(QObject):
    received_wavelengths = pyqtSignal(object)
    received_spectra = pyqtSignal(object,object)
    received_spectrum = pyqtSignal(np.ndarray,list,list)
    renew_config = pyqtSignal(object)
    connected = pyqtSignal(int)

    def __init__(self,
                 parent: QObject,
                 host: str,
                 command_port: int,
                 data_port: int,
                 short_timeout: int,
                 long_timeout: int,
                 config: dict):
        super().__init__(parent=parent)

        self.command_socket = SyncSocket(
            parent=self,
            host=host,
            port=command_port,
            short_timeout=short_timeout,
            long_timeout=long_timeout)
        self.data_socket = SyncSocket(
            parent=self,
            host=host,
            port=data_port,
            short_timeout=short_timeout,
            long_timeout=long_timeout)

        self.initial_config = config

        self.wavelengths = dict()
        self.config = config
        self.threshold = None
        self.channel_num = 0
        self.spectra = None
        self.initialwavelengtharray=np.linspace(1500,1600,20001)
        self.wavelengtharray=self.initialwavelengtharray
        self.range=[1500,1600]
        self.rangeIndexes=[0,20001]
        self.FFTwavelengtharray=self.wavelengtharray
        self.acquire_spectra()



    @pyqtSlotWExceptions()
    def check_connection(self):
        # Restart socket
        self.command_socket.restart()

        self.command_socket.send(":STAT?\r\n")
        answer = self.command_socket.receive().strip()

        try:
            self.connected.emit(int(answer[-1]))
        except ValueError or IndexError:
            self.connected.emit(0)



    def Acquire(self, message: str) -> str:
        # print("Message is : {0}".format(message))

        self.command_socket.restart()

        self.command_socket.send(message)
        answer = self.command_socket.receive()
        # print("Answer is : {0}".format(answer))

        return answer

    def set_ranges(self, channel_num: int, ranges: dict):
        # Send acqu-request and receive the answer
        rngs = []
        for fbg_num in ranges:
            rngs += [ranges[fbg_num]["min"]]
            rngs += [ranges[fbg_num]["max"]]

        message = ":ACQU:CONF:RANG:WAVE:{0}:{1}:{2}\r\n".format(
            channel_num,
            len(ranges),
            ",".join([str(rng) for rng in rngs]))

        answer = self.Acquire(message)

        if answer != ":ACK\r\n":
            raise ValueError("Error! Ranges are not valid.\n"
                             "channel_num:\n\t"
                             "{0}\n"
                             "ranges:\n\t"
                             "{1}".format(channel_num, ",".join([str(rng) for rng in rngs])))

    def set_config(self, config: dict) -> None:
        self.config = config

        message = ":ACQU:CONF:RANG:ENAB\r\n"
        answer = self.Acquire(message)
        if answer != ":ACK\r\n":
            raise ValueError("Error! Ranges enabling was not successful. Check connection with the Interrogator")

        message = ":ACQU:CONF:RANG:DELE:A\r\n"
        answer = self.Acquire(message)
        if answer != ":ACK\r\n":
            raise ValueError("Error! Ranges clearing was not successful.")

        for channel_num in config:
            ranges = config[channel_num]["ranges"]
            if ranges:
                self.set_ranges(int(channel_num), config[channel_num]["ranges"])
                self.set_cwl_formula(int(channel_num), ranges)

            threshold = config[channel_num]["threshold"]
            self.set_threshold(int(channel_num), threshold)

        self.renew_config.emit(self.config)

    def set_cwl_formula(self, channel_num: int, config: dict) -> None:
        cwl_formula = []
        for fbg_num in config:
            cwl_formula += ["[{0};{1}]".format(config[fbg_num]["cwl"], config[fbg_num]["formula"])]

        message = ":ACQU:CONF:RANG:FORM:{0}:{1}:{2}\r\n".format(channel_num, len(cwl_formula), ",".join(cwl_formula))
        answer = self.Acquire(message)

        if answer != ":ACK\r\n":
            raise ValueError("Error! CWLs and formulae setting was not successful.\n"
                             "channel_num:\n\t"
                             "{0}\n"
                             "config:\n\t"
                             "{1}".format(channel_num, config))

    def set_threshold(self, channel_num: int, threshold: int) -> None:
        if not (
                Consts.Interrogator.MIN_THRESHOLD <=
                threshold <=
                Consts.Interrogator.MAX_THRESHOLD):
            return

        message = ":ACQU:CONF:THRE:CHAN:{0}:{1}\r\n".format(channel_num, threshold)
        answer = self.Acquire(message)

        if answer != ":ACK\r\n":
            raise ValueError("Error! Threshold is not valid.\n"
                             "channel_num:\n\t"
                             "{0}\n"
                             "threshold:\n\t"
                             "{1}".format(channel_num, threshold))

    @pyqtSlotWExceptions()
    def Acquire_wavelengths(self):
        """
        Sends acquisition command for all the FBGs with current configuration and receives the data.
        If the data was successful received emits 'received_wavelengths' signal.
        :return: None
        """

        message = ":ACQU:WAVE:CHAN:A?\r\n"
        answer = self.Acquire(message)

        # Parse answer in numpy array
        self.wavelengths = []
        channels = answer.rstrip().split(":")[2:]
        for i in range(len(channels)):
            if channels[i] == "":
                self.wavelengths += [None]
            else:
                self.wavelengths += [np.array(channels[i].split(","), dtype=np.float32)]

        self.received_wavelengths.emit(self.wavelengths)
        # self.update_config()

    def update_config(self):
        config = self.config
        for channel_num, channel in config.items():
            wavelengths = self.wavelengths[int(channel_num)]
            if wavelengths is None:
                continue
            # wavelengths = sorted(wavelengths)

            ranges = [value for (key, value) in sorted(channel["ranges"].items())]
            # Set up the first and the last borders
            if wavelengths[0] > 0:
                ranges[0]["min"] = wavelengths[0] - Consts.Interrogator.RANGE_WIDTH
            # if wavelengths[-1] > 0:
            ranges[-1]["max"] = wavelengths[-1] + Consts.Interrogator.RANGE_WIDTH
            for wavelength_curr, wavelength_next, fbg_range_curr, fbg_range_next in \
                    zip(*pairwise(wavelengths), *pairwise(ranges)):
                # Check if peaks lean near
                # if abs(wavelength_curr - fbg_range_curr["cwl"]) > Consts.Interrogator.RANGE_MAX_SHIFT and \
                #    abs(wavelength_next - fbg_range_next["cwl"]) > Consts.Interrogator.RANGE_MAX_SHIFT:
                #     continue
                #
                # if wavelength_curr < 0 or wavelength_next < 0:
                #     continue

                # Set up central wavelengths equal to the new peak wavelengths
                fbg_range_curr["cwl"] = wavelength_curr
                fbg_range_next["cwl"] = wavelength_next

                # Try to set up max ranges
                fbg_range_curr["max"] = wavelength_curr + Consts.Interrogator.RANGE_WIDTH
                fbg_range_next["min"] = wavelength_next - Consts.Interrogator.RANGE_WIDTH

                # If ranges overlap, set new border as middle between central wavelengths
                if fbg_range_curr["max"] - fbg_range_next["min"] >= 0:
                    border = (wavelength_next + wavelength_curr) / 2
                    fbg_range_curr["max"] = border - Consts.Interrogator.RANGE_ACCURACY
                    fbg_range_next["min"] = border + Consts.Interrogator.RANGE_ACCURACY

        self.set_config(config)

    def acquire_spectra(self):
        """
        Sends acquisition command for all the channels and receives the data.
        If the data was successful received emits 'received_spectra' signal.
        :return: None
        """
        self.command_socket.set_long_timeout(Consts.Interrogator.MAX_LONG_TIMEOUT)
        self.command_socket.set_short_timeout(Consts.Interrogator.MAX_SHORT_TIMEOUT)

        message = ":ACQU:OSAT:CHAN:A?\r\n"
        answer = self.Acquire(message)

        self.command_socket.set_long_timeout(Consts.Interrogator.LONG_TIMEOUT)
        self.command_socket.set_short_timeout(Consts.Interrogator.SHORT_TIMEOUT)

        # Check the data validity
#        if len(answer) != Consts.Interrogator.DATA_LEN_ALL:
#            raise ValueError("Error! Received data is not valid.\n"
#                             "length:\n\t"
#                             "{0}\n"
#                             "data:\n\t"
#                             "{1}".format(len(answer), answer))

        # Parse answer in numpy array
        channels = answer.rstrip().split(":")[2:-1]

#        self.spectra = ([np.array(channel.split(",")[self.rangeIndexes[0]:self.rangeIndexes[1]], dtype=np.float32) for channel in channels])
        self.spectra = np.array([np.array(channel.split(",")[::-1], dtype=np.float32) for channel in channels])
        self.spectra =[array[self.rangeIndexes[0]:self.rangeIndexes[1]] for array in self.spectra]
        self.received_spectra.emit(self.spectra, self.wavelengtharray)

    @pyqtSlotWExceptions("int")
    def acquire_spectrum(self):
        """
        Sends acquisition command for the single channel and receives the data.
        If the data was successful received emits 'received' signal.
        :param channel_num: int -- channel to Acquire, range [0, 7]
        :return: None
        """
        # Send acqu-request and receive the answer

        message = ":ACQU:OSAT:CHAN:{0}?\r\n".format(self.channel_num)
        answer = self.Acquire(message)

        # Check the data validity
#        if len(answer) != Consts.Interrogator.DATA_LEN_SINGLE:
#            raise ValueError("Error! Received data is not valid.\n"
#                             "length:\n\t"
#                             "{0}\n"
#                             "data:\n\t"
#                             "{1}".format(len(answer), answer))

        # Parse answer in numpy array
        self.spectra[self.channel_num]= np.array(answer[len(":ACK:"):].rstrip().split(","), dtype=np.float32)[self.rangeIndexes[0]:self.rangeIndexes[1]]
        self.received_spectrum.emit(self.wavelengtharray,list([self.spectra[self.channel_num]]),[0])


    def set_span(self,start_wavelength=None,stop_wavelength=None):
        if start_wavelength is None:start_wavelength=self.range[0]
        if stop_wavelength is None:stop_wavelength=self.range[1]
        IndexMin=np.argmin(abs(self.initialwavelengtharray-start_wavelength))
        IndexMax=np.argmin(abs(self.initialwavelengtharray-stop_wavelength))
        self.rangeIndexes=[IndexMin,IndexMax]
        self.range=[start_wavelength,stop_wavelength]
        self.wavelengtharray=self.initialwavelengtharray[self.rangeIndexes[0]:self.rangeIndexes[1]]

    def set_channel_num(self, channel_num: int) -> None:
        self.channel_num = channel_num

if __name__ == "__main__":
    from Hardware.Config import Config
    import matplotlib.pyplot as plt

    interrogator = Interrogator(
        parent=None,
        host="10.6.1.10",
        command_port=3500,
        data_port=3365,
        short_timeout=1000,
        long_timeout=2000
    )
    thread = QThread()
    interrogator.moveToThread(thread)
    thread.start()
    #
    #
    # # Test Acquire_wavelengths method
    # interrogator.Acquire_wavelengths()
    # print(interrogator.wavelengths)
    #
    # # Test Acquire_spectra method
    # interrogator.Acquire_spectra()
    # wls = np.linspace(1500, 1600, len(interrogator.spectra[0]))
    #
    # for channel_num in interrogator.spectra:
    #     plt.plot(wls, interrogator.spectra[channel_num])
    # plt.show()
    #
    # # Test set_ranges method
    # interrogator.set_ranges(0, {"0": {"min": 1555.12, "max": 1560.13}})
    #
    # # Test set_threshold method
    # interrogator.set_threshold(0, 30)
    #
    # # Test set_config method
    # cfg = Config("config.json")
    # interrogator.set_config(cfg.config["channels"])

    # Test config for MCF-v1
    cfg = Config("config.json")
    interrogator.set_config(cfg.config["channels"])

    interrogator.Acquire_spectra()
    interrogator.Acquire_wavelengths()

    wls = np.linspace(1500, 1600, len(interrogator.spectra[0]))

    for channel_num in [2, 3, 4, 7]:
        print(interrogator.wavelengths[channel_num])

        plt.plot(wls, interrogator.spectra[channel_num])
        if interrogator.wavelengths[channel_num] is not None:
            plt.vlines(interrogator.wavelengths[channel_num], ymin=-60, ymax=0)
        plt.show()
