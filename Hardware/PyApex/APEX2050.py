#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#                                       IMPORTS
# ------------------------------------------------------------------------------

try:
    from serial import EIGHTBITS, PARITY_NONE, STOPBITS_ONE
except:
    pass

# ------------------------------------------------------------------------------
#                                  UNIVERSAL CONSTANTS
# ------------------------------------------------------------------------------

VACCUM_LIGHT_SPEED = 299792458
Celerity = VACCUM_LIGHT_SPEED


# ------------------------------------------------------------------------------
#                                   AP1000 CONSTANTS
# ------------------------------------------------------------------------------

#                       CONSTANTS FOR AP1000 MODULES REFERENCE
# ------------------------------------------------------------------------------
AP1000_PWM = 3314
AP1000_PWM_NAME = "Optical Power Meter"
AP1000_TLS_CBAND = 3350
AP1000_TLS_CBAND_NAME = "C Band Tunable Laser Source"
AP1000_TLS_LBAND = 3352
AP1000_TLS_LBAND_NAME = "L Band Tunable Laser Source"
AP1000_OSW = 3344
AP1000_OSW_NAME = "Optical Switch"
AP1000_ATT = 3364
AP1000_ATT_NAME = "Optical Attenuator"
AP1000_EFA = 3370
AP1000_EFA_NAME = "Erbium Doped Fiber Amplifier"
AP1000_FIL = 3380
AP1000_FIL_NAME = "Optical Filter"
AP1000_DFB_CBAND = 3390
AP1000_DFB_CBAND_NAME = "C Band DFB Laser Source"
AP1000_DFB_LBAND = 3392
AP1000_DFB_LBAND_NAME = "L Band DFB Laser Source"
AP1000_DFB_OBAND = 3395
AP1000_DFB_OBAND_NAME = "O Band DFB Laser Source"
AP1000_POL = 3510
AP1000_POL_NAME = "Polarimeter"

Modules = {\
    AP1000_TLS_CBAND : AP1000_TLS_CBAND_NAME, \
    AP1000_TLS_LBAND : AP1000_TLS_LBAND_NAME, \
    AP1000_PWM : AP1000_PWM_NAME, \
    AP1000_ATT : AP1000_ATT_NAME, \
    AP1000_EFA : AP1000_EFA_NAME, \
    AP1000_OSW : AP1000_OSW_NAME,\
    AP1000_FIL : AP1000_FIL_NAME,\
    AP1000_DFB_CBAND : AP1000_DFB_CBAND_NAME, \
    AP1000_DFB_LBAND : AP1000_DFB_LBAND_NAME, \
    AP1000_DFB_OBAND : AP1000_DFB_OBAND_NAME, \
    AP1000_POL : AP1000_POL_NAME, \
}

#                           SLOTS NUMBER MIN AND MAX
# ------------------------------------------------------------------------------
AP1000_SLOT_MIN = 0
AP1000_SLOT_MAX = 92

#                            POWER METER CONSTANTS
# ------------------------------------------------------------------------------
# POWER METER TYPE
AP1000_PWM_CHTYPE = {"1" : "Standard", "3" : "High Power"}
# MIN AND MAX WAVELENGTH
AP1000_PWM_WLMIN = 800
AP1000_PWM_WLMAX = 1700
# MIN AND MAX AVERAGE TIME
AP1000_PWM_AVGMIN = 15
AP1000_PWM_AVGMAX = 10000

#                            ATTENUATOR CONSTANTS
# ------------------------------------------------------------------------------
# NUMBER OF CHANNELS
AP1000_ATT_CHNUMBER = 2
# MIN AND MAX ATTENUATION
AP1000_ATT_ATTMIN = 0
AP1000_ATT_ATTMAX = 35
# MIN AND MAX WAVELENGTH
AP1000_ATT_WLMIN = 1300
AP1000_ATT_WLMAX = 1700

#                           TUNABLE LASER CONSTANTS
# ------------------------------------------------------------------------------
# [3350 : C-BAND TYPE, 3351 : NOT USED, 3352 : L-BAND TYPE]
# MIN AND MAX POWER
AP1000_TLS_POWMIN = [-30, None, -30]
AP1000_TLS_POWMAX = [13, None, 13]
# MIN AND MAX WAVELENGTH
AP1000_TLS_WLMIN = [1526, None, 1567]
AP1000_TLS_WLMAX = [1567, None, 1608]
# MIN AND MAX FREQUENCY
AP1000_TLS_FRMIN = [VACCUM_LIGHT_SPEED / AP1000_TLS_WLMIN[0], None, VACCUM_LIGHT_SPEED / AP1000_TLS_WLMIN[2]]
AP1000_TLS_FRMAX = [VACCUM_LIGHT_SPEED / AP1000_TLS_WLMAX[0], None, VACCUM_LIGHT_SPEED / AP1000_TLS_WLMAX[2]]
# FOR CALIBRATION ONLY
# MIN AND MAX TEMPERATURE BINARY VALUES
AP1000_TLS_TMIN = 0
AP1000_TLS_TMAX = 65535
# MIN AND MAX SOA CURRENT BINARY VALUES
AP1000_TLS_SOAMIN = 0
AP1000_TLS_SOAMAX = 65535

#                         ERBIUM AMPLIFIER CONSTANTS
# ------------------------------------------------------------------------------
# [3370-A : BOOSTER, 3370-B : IN-LINE, 3370-C : PRE-AMPLI]
# MAX PUMP LASER CURRENT (mA)
AP1000_EFA_IPMAX = [1000, 1000, 600]

#                               FILTER CONSTANTS
# ------------------------------------------------------------------------------
# MIN AND MAX WAVELENGTH
AP1000_FIL_WLMIN = 1525.0
AP1000_FIL_WLMAX = 1635.0
# MIN AND MAX FREQUENCY
AP1000_FIL_FRMIN = VACCUM_LIGHT_SPEED / AP1000_FIL_WLMAX
AP1000_FIL_FRMAX = VACCUM_LIGHT_SPEED / AP1000_FIL_WLMIN
# MIN AND MAX SWEEP SPEED
AP1000_FIL_SPEEDMIN = 1.0
AP1000_FIL_SPEEDMAX = 10.0

#                           DFB LASER CONSTANTS
# ------------------------------------------------------------------------------
# [3390 : C-BAND TYPE, 3391 : NOT USED, 3392 : L-BAND TYPE, 3393 : NOT USED, 3394 : NOT USED, 3395 : 0-BAND TYPE]
# MIN AND MAX POWER
AP1000_DFB_POWMIN = [-30, None, -30, None, None, -30]
AP1000_DFB_POWMAX = [13, None, 13, None, None, 13]
# MIN AND MAX WAVELENGTH
AP1000_DFB_WLMIN = [1530, None, 1565, None, None, 1290]
AP1000_DFB_WLMAX = [1565, None, 1610, None, None, 1330]
# MIN AND MAX FREQUENCY
AP1000_DFB_FRMIN = [VACCUM_LIGHT_SPEED / AP1000_DFB_WLMIN[0], None, VACCUM_LIGHT_SPEED / AP1000_DFB_WLMIN[2], \
                    None, None, VACCUM_LIGHT_SPEED / AP1000_DFB_WLMIN[5]]
AP1000_DFB_FRMAX = [VACCUM_LIGHT_SPEED / AP1000_DFB_WLMAX[0], None, VACCUM_LIGHT_SPEED / AP1000_DFB_WLMAX[2], \
                    None, None, VACCUM_LIGHT_SPEED / AP1000_DFB_WLMAX[5]]
# FOR CALIBRATION ONLY
# MIN AND MAX TEMPERATURE BINARY VALUES
AP1000_DFB_TMIN = 0
AP1000_DFB_TMAX = 65535

#                           POLARIMETER CONSTANTS
# ------------------------------------------------------------------------------

# MIN AND MAX ACQUISITION TIME IN MS
AP1000_POL_ACQMIN = 10.0
AP1000_POL_ACQMAX = 1000.0
# MIN AND MAX WAVELENGTH IN NM
AP1000_POL_WLMIN = 800
AP1000_POL_WLMAX = 1700

# ------------------------------------------------------------------------------
#                                   AP2XXX CONSTANTS
# ------------------------------------------------------------------------------

# MIN AND MAX WAVELENGTH
AP2XXX_WLMIN = 1200
AP2XXX_WLMAX = 1700
# MIN AND MAX WAVELENGTH SPAN
AP2XXX_MINSPAN = 0.01
AP2XXX_MAXSPAN = 100
# MIN AND MAX CENTER WAVELENGTH
AP2XXX_MAXCENTER = AP2XXX_WLMAX - AP2XXX_MINSPAN / 2
AP2XXX_MINCENTER = AP2XXX_WLMIN + AP2XXX_MINSPAN / 2
# MIN AND MAX Y RESOLUTION
AP2XXX_MINYRES = 0.001
AP2XXX_MAXYRES = 100
# MIN AND MAX POINTS NUMBER
AP2XXX_MINNPTS = 2
AP2XXX_MAXNPTS = 1000000

# ------------------------------------------------------------------------------
#                                   AB3510 CONSTANTS
# ------------------------------------------------------------------------------

# VID AND PID
AB3510_VID = 0x5553
AB3510_PID = 0x80a0
# VENDOR REQUESTS
AB3510_VR_RESET_ALL = 0xB0
AB3510_VR_SET_EEPROM_PARAMETERS = 0xB1
AB3510_VR_GET_EEPROM_PARAMETERS = 0xB2
AB3510_VR_SIMULATION_MODE = 0xB4
AB3510_VR_GET_SAMPLE = 0xB5
AB3510_VR_START_ACQ = 0xB6
AB3510_VR_STOP_ACQ = 0xB7
AB3510_VR_SET_FREQ = 0xB9
AB3510_VR_GET_FREQ = 0xBA
AB3510_VR_GET_TEMPERATURE = 0xBB
AB3510_VR_BULK_TEST = 0xBC
AB3510_VR_RESET_FIFO = 0xBF
AB3510_VR_WRITE_EEPROM = 0xC1
AB3510_VR_READ_EEPROM = 0xC2
# OTHER CONSTANTS
AB3510_PTS_NB = 100

# ------------------------------------------------------------------------------
#                                   AB3380 CONSTANTS
# ------------------------------------------------------------------------------

# VID AND PID
AB3380_VID = 0x5553
AB3380_PID = 0x8070
# VENDOR REQUESTS
AB3380_VR_RESET_ALL = 0xB0
AB3380_VR_SET_EEPROM_PARAMETERS = 0xB1
AB3380_VR_GET_EEPROM_PARAMETERS = 0xB2
AB3380_VR_SET_VOLTAGE1 = 0xB3
AB3380_VR_SET_VOLTAGE2 = 0xB9
AB3380_VR_TURN_ON = 0xB4
AB3380_VR_SET_SWITCH1 = 0xB5
AB3380_VR_SET_SWITCH2 = 0xB7
AB3380_VR_MAX_VOLTAGE1 = 0xC5
AB3380_VR_MAX_VOLTAGE2 = 0xC6
# OTHER CONSTANTS
AB3380_PTS_NB = 84

# ------------------------------------------------------------------------------
#                               ETUVE CONSTANTS
# ------------------------------------------------------------------------------

try:
    ETUVE_BAUDRATE = 9600
    ETUVE_NBITS = EIGHTBITS
    ETUVE_PARITY = PARITY_NONE
    ETUVE_STOPBIT = STOPBITS_ONE
    ETUVE_FLOWCONTROL = False
except:
    pass


# ------------------------------------------------------------------------------
#                                   ERROR CODE CONSTANTS
# ------------------------------------------------------------------------------

APXXXX_ERROR_COMMUNICATION = -1
APXXXX_ERROR_BADCOMMAND = -2
APXXXX_ERROR_ARGUMENT_TYPE = -11
APXXXX_ERROR_ARGUMENT_VALUE = -12
APXXXX_ERROR_BAD_FILENAME = -13
APXXXX_ERROR_VARIABLE_NOT_DEFINED = -301
AP1000_ERROR_SLOT_NOT_DEFINED = -151
AP1000_ERROR_SLOT_NOT_GOOD_TYPE = -152
AP1000_ERROR_SLOT_TYPE_NOT_DEFINED = -153

ABXXXX_NO_EQUIPMENT_FOUND = -310
ABXXXX_ERROR_BAD_HANDLE = -311
ABXXXX_EP0_WRITE_ERROR = -331
ABXXXX_EP0_READ_ERROR = -332
ABXXXX_EP1_WRITE_ERROR = -333
ABXXXX_EP1_READ_ERROR = -334
ABXXXX_EP2_WRITE_ERROR = -335
ABXXXX_EP2_READ_ERROR = -336
ABXXXX_EP3_WRITE_ERROR = -337
ABXXXX_EP3_READ_ERROR = -338
ABXXXX_EP4_WRITE_ERROR = -339
ABXXXX_EP4_READ_ERROR = -340
ABXXXX_EP5_WRITE_ERROR = -341
ABXXXX_EP5_READ_ERROR = -342
ABXXXX_EP6_WRITE_ERROR = -343
ABXXXX_EP6_READ_ERROR = -344

ETUVE_ERROR_COMMUNICATION = -1
ETUVE_ERROR_BADCOMMAND = -2
ETUVE_ERROR_ARGUMENT_TYPE = -11
ETUVE_ERROR_ARGUMENT_VALUE = -12


# ------------------------------------------------------------------------------
#                                   SIMULATION CONSTANTS
# ------------------------------------------------------------------------------

SimuAP1000_ID = "APEX-TECHNOLOGIES/AP1000-8/00001/1.0\n"
SimuAP1000_SlotID = "APEX-TECHNOLOGIES/3314/13-3314-A-13-000502/1.0\n"
SimuAP1000_SlotUsed = "1\n"

SimuPWM_SlotID = "APEX-TECHNOLOGIES/3314/13-3314-A-13-000502/1.0\n"
SimuPWM_AvgTime = "1000\n"
SimuPWM_Wavelength = "1550.000\n"
SimuPWM_Power_dBm = "2.45\n"
SimuPWM_Power_mW = "1.85\n"

SimuATT_SlotID = "APEX-TECHNOLOGIES/3364/12-3364-A-2-000504/0.0\n"
SimuATT_Attenuation = "10\n"
SimuATT_Wavelength = "1528\n"

SimuTLS_SlotID = "APEX-TECHNOLOGIES/3350/10-3350-A-000503/0.0\n"
SimuTLS_Power = "5\n"
SimuTLS_Wavelength = "1553.310\n"

SimuEFA_SlotID = "APEX-TECHNOLOGIES/3370/09-3370-A-000500/0.0\n"
SimuEFA_InVoltage = "512\n"
SimuEFA_OutVoltage = "624\n"
SimuEFA_InPower = "-10\n"
SimuEFA_OutPower = "15\n"

SimuOSW_SlotID = "APEX-TECHNOLOGIES/3344/10-3344-A-1x4-000501/1.0\n"

SimuDFB_SlotID = "APEX-TECHNOLOGIES/3390/10-3390-A-000525/0.0\n"

SimuAP2XXX_ID = "APEX Technologies/2050-A/09-2050-A-000000/9.14\n"
SimuAP2XXX_StartWavelength = "1526.000\n"
SimuAP2XXX_StopWavelength = "1566.000\n"
SimuAP2XXX_Span = "20\n"
SimuAP2XXX_Center = "1551.234\n"
SimuAP2XXX_XResolution = "0.100\n"
SimuAP2XXX_YResolution = "2.000\n"
SimuAP2XXX_NPoints = "10000\n"

SIMU_AB3510_VID = 0x5553
SIMU_AB3510_PID = 0x3510
SIMU_AB3510_TEMPERATURE = 23.6

SIMU_AB3380_VID = 0x5553
SIMU_AB3380_PID = 0x8070
