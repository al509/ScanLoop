import serial
import json
import numpy as np
from datetime import datetime
from time import perf_counter, sleep
from PyQt5.QtCore import QObject, pyqtSignal    

__version__ = '1'
__date__ = '27.09.2023'


#%%
'''
Вспомогательные функции чтения и записи посылок по serial
'''
def FloatToChars(number):
    result = ['', '', '', '']
    bAnd = np.uint8(128)
    kk = np.array([1, 1, 1, 1], dtype=np.uint8)
    int_part = int(np.abs(number))
    frac_part = np.abs(number) - int_part
    kk[0] = int(int_part/256)
    kk[1] = int_part%256
    frac_part *= 10000
    kk[2] = int(frac_part/256)
    kk[3] = frac_part%256
    if number < 0:
        kk[0] = (np.uint8(kk[0]) | bAnd)
    for i in range(4):
        result[i] = np.uint8(kk[i])
    return result


def CharsToFloat(chars):
    tmpData = '80'
    bAnd = int(tmpData, 16)
    flagZShu = np.uint8(bAnd) & np.uint8(chars[0])
    flag = (flagZShu != 0)
    D0 = 256*np.int16(chars[0] - bAnd*(flag)) + np.int16(chars[1])
    D1 = 256*np.int16(chars[2]) + np.int16(chars[3])
    a = np.float64(D0)
    b = np.float64(D1)
    rData = (a + b*0.0001)*((-1)**(flag))
    return rData


def OpeningPort(COMPort, baudrate):
    ser = serial.Serial()  # Создание порта
    ser.baudrate = baudrate  # Настройка частоты порта
    ser.port = COMPort  # Указание COMPort
    ser.timeout=1
    ser.open()  # Открытие порта
    return ser


def SendPackage(serial, SendData, package, length):
    if SendData:
        chars = FloatToChars(SendData)
        for char in chars:
            package.append(char)
    tmpdata1 = np.uint8(0)
    for i in range(0, int(length, 16)-1):
        tmpdata1 = tmpdata1 ^ package[i]    
    package.append(tmpdata1)
    serial.write(package)


def ReadPackage(serial, length):
    data = serial.read(length)
    return data


def Logging(time='1.1.1 11:11', event='Nothing', counter=1):
    print(f'{counter}) {time} - {event}')
    
    
def PrintingDataFromStage(data, whole_info=True, volts=False, move=False, *args):
    if whole_info:
        print(f'Total bytes = {len(data)}')
        for i in range(0, len(data)):
            print(f'{i+1} byte: {hex(data[i])}')
    if volts:
        print(f'Volts on stage: {args}')
    if move:
        print(f'Moves on stage: {args}')
#%%
'''
Создание класса PiezoStage, методы - основные команды для управления подвижкой
'''
class PiezoStage(QObject):
    
    is_connected = 0
    def __init__(self, COMPort, baudrate):
        super().__init__()
        self.serial = OpeningPort(COMPort=COMPort, baudrate=baudrate)
        self.event_counter = 1
        _, self.rel_position = self.A06_ReadDataMove()
        self.abs_position = 0
        try:
            with open('PiezoStageStartPosition.json', 'r', encoding='utf-8') as file:
                tmp = json.load(file)
                self.abs_position = tmp["X"]
        except Exception as e:
            print(e)
            self.abs_position = 0
        Logging(datetime.now().strftime('%d.%m.%Y %H:%M:%S'), 'Piezo stage is connected to COM5', self.event_counter)
    
    
    def __del__(self):
        print(f'Destructor')
        self.serial.close()
        self.event_counter += 1
        Logging(datetime.now().strftime('%d.%m.%Y %H:%M:%S'), 'Piezo stage is disconnected', self.event_counter)
    
    
    def A00_SendVolt(self, volt_to_set):
        Send1, Send2, Send3, Send4, Send5, Send6 = '0xAA', '0x01', '0x0B', '0x00', '0x00', '0x00'
        # Создание посылки(?); aa - Start Byte (B0), 01 - Address (B1), 0b - Package length (B2)
        # 00 - Instruction code 1 (B3), 00 - Instruction code 2 (B4), 00 - The number of channel ('0' - 1ch, '1' - 2chs, '2' - 3chs)
        package_hex = [Send1, Send2, Send3, Send4, Send5, Send6]
        package_dec = list(map(lambda x: int(x, 16), package_hex))
        SendPackage(self.serial, volt_to_set, package_dec, Send3)
        
    
    def A01_SendMove(self, coord_to_move):
        # print(f'into the function {coord_to_move}', end = ' ')
        Send1, Send2, Send3, Send4, Send5, Send6 = '0xAA', '0x01', '0x0B', '0x01', '0x00', '0x00'
        # Создание посылки(?); aa - Start Byte (B0), 01 - Address (B1), 0b - Package length (B2)
        # 00 - Instruction code 1 (B3), 00 - Instruction code 2 (B4), 00 - The number of channel ('0' - 1ch, '1' - 2chs, '2' - 3chs)
        package_hex = [Send1, Send2, Send3, Send4, Send5, Send6]
        package_dec = list(map(lambda x: int(x, 16), package_hex))
        # print(f'Num: {coord_to_move}; Num after char transform: {CharsToFloat(FloatToChars(coord_to_move))}')
        SendPackage(self.serial, coord_to_move, package_dec, Send3)
        
    
    def A04_ClearMultChannel(self):
        Send1, Send2, Send3, Send4, Send5 = '0xAA', '0x01', '0x06', '0x04', '0x00'
        package_hex = [Send1, Send2, Send3, Send4, Send5]
        package_dec = list(map(lambda x: int(x, 16), package_hex))
        SendPackage(self.serial, None, package_dec, Send3)
    
    
    def A05_ReadDataVolt(self):
        Send1, Send2, Send3, Send4, Send5, Send6 = '0xAA', '0x01', '0x07', '0x05', '0x00', '0x00'
        package_hex = [Send1, Send2, Send3, Send4, Send5, Send6]
        package_dec = list(map(lambda x: int(x, 16), package_hex))
        SendPackage(self.serial, None, package_dec, Send3)
        sleep(1)
        whole_data = ReadPackage(self.serial, 11)
        stage_volt = CharsToFloat(whole_data[6:10])
        sleep(1)
        return whole_data, stage_volt
    
    
    def A06_ReadDataMove(self):
        Send1, Send2, Send3, Send4, Send5, Send6 = '0xAA', '0x01', '0x07', '0x06', '0x00', '0x00'
        package_hex = [ Send1, Send2, Send3, Send4, Send5, Send6]
        package_dec = list(map(lambda x: int(x, 16), package_hex))
        SendPackage(self.serial, None, package_dec, Send3)
        sleep(0.1)
        whole_data = ReadPackage(self.serial, 11)
        stage_move = CharsToFloat(whole_data[6:10])
        sleep(0.1)
        return whole_data, stage_move
    
    
    def A18_SetChannelOpenOrClose(self, setOpen=False):
        Send1, Send2, Send3, Send4, Send5, Send6 = '0xAA', '0x01', '0x08', '0x12', '0x00', '0x00'
        if setOpen:
            Send7 = '0x4f'
        else:
            Send7 = '0x43'
        package_hex = [Send1, Send2, Send3, Send4, Send5, Send6, Send7]
        package_dec = list(map(lambda x: int(x, 16), package_hex))
        SendPackage(self.serial, None, package_dec, Send3)
    
    
    def A19_ReadChannelOpenOrClose(self):
        Send1, Send2, Send3, Send4, Send5, Send6 = '0xAA', '0x01', '0x07', '0x13', '0x00', '0x00'
        package_hex = [Send1, Send2, Send3, Send4, Send5, Send6]
        package_dec = list(map(lambda x: int(x, 16), package_hex))
        SendPackage(self.serial, None, package_dec, Send3)
        sleep(0.1)
        dat_from_stage = ReadPackage(self.serial, 8)
        sleep(0.1)
        return dat_from_stage
    
    
    def A26_SetChannelHMove(self, HMove_to_set):
        Send1, Send2, Send3, Send4, Send5, Send6 = '0xAA', '0x01', '0x0B', '0x1A', '0x00', '0x00'
        package_hex = [Send1, Send2, Send3, Send4, Send5, Send6]
        package_dec = list(map(lambda x: int(x, 16), package_hex))
        SendPackage(self.serial, HMove_to_set, package_dec, Send3)
        
        
    def A27_ReadChannelHMove(self):
        Send1, Send2, Send3, Send4, Send5, Send6 = '0xAA', '0x01', '0x07', '0x1B', '0x00', '0x00'
        package_hex = [Send1, Send2, Send3, Send4, Send5, Send6]
        package_dec = list(map(lambda x: int(x, 16), package_hex))
        SendPackage(self.serial, None, package_dec, Send3)
        sleep(0.1)
        dat_from_stage = ReadPackage(self.serial, 11)
        sleep(0.1)
        return dat_from_stage
    
    
    def A30_SetChannelLVolt(self, LVolt_to_set=0):
        Send1, Send2, Send3, Send4, Send5, Send6 = '0xAA', '0x01', '0x0B', '0x1E', '0x00', '0x00'
        package_hex = [Send1, Send2, Send3, Send4, Send5, Send6]
        package_dec = list(map(lambda x: int(x, 16), package_hex))
        SendPackage(self.serial, LVolt_to_set, package_dec, Send3)
        
        
    def A31_ReadChannelLVolt(self):
        Send1, Send2, Send3, Send4, Send5, Send6 = '0xAA', '0x01', '0x07', '0x1F', '0x00', '0x00'
        package_hex = [Send1, Send2, Send3, Send4, Send5, Send6]
        package_dec = list(map(lambda x: int(x, 16), package_hex))
        SendPackage(self.serial, None, package_dec, Send3)
        sleep(0.1)
        dat_from_stage = ReadPackage(self.serial, 11)
        sleep(0.1)
        return dat_from_stage
    
    
    def A32_SetChannelHVolt(self, HVolt_to_set=120.000):
        Send1, Send2, Send3, Send4, Send5, Send6 = '0xAA', '0x01', '0x0B', '0x20', '0x00', '0x00'
        package_hex = [Send1, Send2, Send3, Send4, Send5, Send6]
        package_dec = list(map(lambda x: int(x, 16), package_hex))
        SendPackage(self.serial, HVolt_to_set, package_dec, Send3)
    
    
    def A33_ReadChannelHVolt(self):
        Send1, Send2, Send3, Send4, Send5, Send6 = '0xAA', '0x01', '0x07', '0x21', '0x00', '0x00'
        package_hex = [Send1, Send2, Send3, Send4, Send5, Send6]
        package_dec = list(map(lambda x: int(x, 16), package_hex))
        SendPackage(self.serial, None, package_dec, Send3)
        sleep(0.1)
        dat_from_stage = ReadPackage(self.serial, 11)
        sleep(0.1)
        return dat_from_stage
    
    
    def A34_SetChannelLMove(self, LMove_to_set=0):
        Send1, Send2, Send3, Send4, Send5, Send6 = '0xAA', '0x01', '0x0B', '0x22', '0x00', '0x00'
        package_hex = [Send1, Send2, Send3, Send4, Send5, Send6]
        package_dec = list(map(lambda x: int(x, 16), package_hex))
        SendPackage(self.serial, LMove_to_set, package_dec, Send3)
    
    
    def A35_ReadChannelLMove(self):
        Send1, Send2, Send3, Send4, Send5, Send6 = '0xAA', '0x01', '0x07', '0x23', '0x00', '0x00'
        package_hex = [Send1, Send2, Send3, Send4, Send5, Send6]
        package_dec = list(map(lambda x: int(x, 16), package_hex))
        SendPackage(self.serial, None, package_dec, Send3)
        sleep(0.1)
        dat_from_stage = ReadPackage(self.serial, 11)
        sleep(0.1)
        return dat_from_stage
        

        
#%%
'''
Отладка программы
'''
if __name__ == '__main__':
    COMPort = 'COM5'
    baudrate = 9600
    stage = PiezoStage(COMPort, baudrate)
    # del stage