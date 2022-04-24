# -*- coding: utf-8 -*-

from platform import system
from enum import Enum

SYSTEM_NAME = system()


class Consts:
    """Class with default constant values for particular hardware used in the lab"""

    class APEX:
        HOST = "10.2.60.25"

    class Yokogawa:
        HOST = "10.2.60.60"

    class Interrogator:
        HOST = "192.168.19.111"
        COMMAND_PORT = 3500
        DATA_PORT = 3365
        SHORT_TIMEOUT = 1000
        MAX_SHORT_TIMEOUT = 5000
        MAX_LONG_TIMEOUT = 10000
        LONG_TIMEOUT = 2000

        CHANNEL_NUMBER = 8

        DATA_LEN_SINGLE = 160014
        DATA_LEN_ALL = 1280071

        MIN_THRESHOLD = 0
        MAX_THRESHOLD = 60

        RANGE_WIDTH = 4
        RANGE_ACCURACY = 1e-3  # nm
        RANGE_MAX_SHIFT = 20  # nm

        MIN_WL = 1500
        MAX_WL = 1600


    class Scope:
        HOST = '10.2.60.27'
        
    class Powermeter:
        SERIAL_NUMBER='P0015055'

    class LUNA:
        PORT=1
