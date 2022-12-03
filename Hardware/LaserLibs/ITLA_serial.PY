import serial
import time
import struct
import os
import os.path
import time
import sys
import threading

ITLA_NOERROR=0x00
ITLA_EXERROR=0x01
ITLA_AEERROR=0x02
ITLA_CPERROR=0x03
ITLA_NRERROR=0x04
ITLA_CSERROR=0x05
ITLA_ERROR_SERPORT=0x01
ITLA_ERROR_SERBAUD=0x02

REG_Nop=0x00
REG_Mfgr=0x02
REG_Model=0x03
REG_Serial=0x04
REG_Release=0x06
REG_Gencfg=0x08
REG_AeaEar=0x0B
REG_Iocap=0x0D
REG_Ear=0x10
REG_Dlconfig=0x14
REG_Dlstatus=0x15
REG_Channel=0x30
REG_Power=0x31
REG_Resena=0x32
REG_Grid=0x34
REG_Fcf1=0x35
REG_Fcf2=0x36
REG_Lf1=0x40
REG_Lf2=0x41    # Read only
REG_Oop=0x42    # Read only
REG_Opsl=0x50
REG_Opsh=0x51
REG_Lfl1=0x52
REG_Lfl2=0x53
REG_Lfh1=0x54
REG_Lfh2=0x55
REG_Currents=0x57
REG_Temps=0x58
REG_Ftf=0x62
REG_Mode=0x90
REG_PW=0xE0
REG_Csweepsena=0xE5
REG_Csweepamp=0xE4
REG_Cscanamp=0xE4
REG_Cscanon=0xE5
REG_Csweepon=0xE5
REG_Csweepoffset=0xE6
REG_Cscanoffset=0xE6
REG_Cscansled=0xF0
REG_Cscanf1=0xF1
REG_Cscanf2=0xF2
REG_CjumpTHz=0xEA
REG_CjumpGHz=0xEB
REG_CjumpSled=0xEC
REG_Cjumpon=0xED
REG_Cjumpoffset=0xE6

READ=0
WRITE=1
latestregister=0
tempport=0
raybin=0
queue=[]
maxrowticket=0

_error=ITLA_NOERROR
seriallock=0


def stripString(input):
    outp=''
    input=str(input)
    teller=0
    while teller<len(input) and ord(input[teller])>47:
        outp=outp+input[teller]
        teller=teller+1
    return(outp)

def ITLALastError():
    return(_error)

def SerialLock():
    global seriallock
    return seriallock

def SerialLockSet():
    global seriallock
    global queue
    seriallock=1
    
def SerialLockUnSet():
    global seriallock
    global queue
    seriallock=0
    queue.pop(0)
    
def checksum(byte0,byte1,byte2,byte3):
    bip8=(byte0&0x0f)^byte1^byte2^byte3
    bip4=((bip8&0xf0)>>4)^(bip8&0x0f)
    return bip4
    
def Send_command(sercon,byte0,byte1,byte2,byte3):
    sercon.write(byte0.to_bytes(1, byteorder = "big"))
    sercon.write(byte1.to_bytes(1, byteorder = "big"))
    sercon.write(byte2.to_bytes(1, byteorder = "big"))
    sercon.write(byte3.to_bytes(1, byteorder = "big"))

def Receive_response(sercon):
    global _error,queue
    reftime= time.perf_counter()
    while sercon.inWaiting()<4:
        if  time.perf_counter()>reftime+0.25:
            _error=ITLA_NRERROR
            return(0xFF,0xFF,0xFF,0xFF)
        time.sleep(0.0001)
    try:
        byte0=ord(sercon.read(1))
        byte1=ord(sercon.read(1))
        byte2=ord(sercon.read(1))
        byte3=ord(sercon.read(1))
    except:
        print ('problem with serial communication. queue[0] =',queue)
        byte0=0xFF
        byte1=0xFF
        byte2=0xFF
        byte3=0xFF
    if checksum(byte0,byte1,byte2,byte3)==byte0>>4:
        _error=byte0&0x03
        return(byte0,byte1,byte2,byte3)
    else:
        _error=ITLA_CSERROR
        return(byte0,byte1,byte2,byte3)       

def Receive_simple_response(sercon):
    global _error,CoBrite
    reftime= time.perf_counter()
    while sercon.inWaiting()<4:
        if  time.perf_counter()>reftime+0.25:
            _error=ITLA_NRERROR
            return(0xFF,0xFF,0xFF,0xFF)
        time.sleep(0.0001)
    byte0=ord(sercon.read(1))
    byte1=ord(sercon.read(1))
    byte2=ord(sercon.read(1))
    byte3=ord(sercon.read(1)) 

def ITLAConnect(port,baudrate=9600):
    global CoBrite
    reftime= time.perf_counter()
    connected=False
    try:
        conn = serial.Serial(port,baudrate , timeout=1)
    except serial.SerialException:
        return(ITLA_ERROR_SERPORT)
    baudrate2=4800
    while baudrate2<115200:
        ITLA(conn,REG_Nop,0,0)
        if ITLALastError() != ITLA_NOERROR:
            #go to next baudrate
            if baudrate2==4800:baudrate2=9600
            elif baudrate2==9600: baudrate2=19200
            elif baudrate2==19200: baudrate2=38400
            elif baudrate2==38400:baudrate2=57600
            elif baudrate2==57600:baudrate2=115200
            conn.close()
            conn = serial.Serial(port,baudrate2 , timeout=1)            
        else:
            return(conn)
    conn.close()
    return(ITLA_ERROR_SERBAUD)

def ITLA(sercon: serial.Serial,register,data,rw):
    global latestregister
    lock=threading.Lock()
    lock.acquire()
    global queue
    global maxrowticket
    rowticket=maxrowticket+1
    maxrowticket=maxrowticket+1
    queue.append(rowticket)
    lock.release()
    while queue[0]!=rowticket:
        rowticket=rowticket
    if rw==0:
        byte2=int(data/256)
        byte3=int(data-byte2*256)
        latestregister=register
        Send_command(sercon,int(checksum(0,register,byte2,byte3))*16,register,byte2,byte3)
        test=Receive_response(sercon)
        b0=test[0]
        b1=test[1]
        b2=test[2]
        b3=test[3]
        if (b0&0x03)==0x02:
            test=AEA(sercon,b2*256+b3)
            lock.acquire()
            queue.pop(0)
            lock.release()
            return test
        lock.acquire()
        queue.pop(0)
        lock.release()
        return b2*256+b3
    else:
        byte2=int(data/256)
        byte3=int(data-byte2*256)
        Send_command(sercon,int(checksum(1,register,byte2,byte3))*16+1,register,byte2,byte3)
        test=Receive_response(sercon)
        lock.acquire()
        queue.pop(0)
        lock.release()
        return(test[2]*256+test[3])

def ITLA_send_only(sercon,register,data,rw):
    global latestregister
    global queue
    global maxrowticket
    rowticket=maxrowticket+1
    maxrowticket=maxrowticket+1
    queue.append(rowticket)
    while queue[0]!=rowticket:
        time.sleep(.1)
    SerialLockSet()
    if rw==0:
        latestregister=register
        Send_command(sercon,int(checksum(0,register,0,0))*16,register,0,0)
        Receive_simple_response(sercon)
        SerialLockUnSet()
    else:
        byte2=int(data/256)
        byte3=int(data-byte2*256)
        Send_command(sercon,int(checksum(1,register,byte2,byte3))*16+1,register,byte2,byte3)
        Receive_simple_response(sercon)
        SerialLockUnSet()
         
def AEA(sercon,bytes):
    outp=''
    while bytes>0:
        Send_command(sercon,int(checksum(0,REG_AeaEar,0,0))*16,REG_AeaEar,0,0)
        test=Receive_response(sercon)
        outp=outp+chr(test[2])
        outp=outp+chr(test[3])
        bytes=bytes-2
    return outp



def ITLAFWUpgradeStart(sercon,raydata,salvage=0):
    global tempport,raybin
    #set the baudrate to maximum and reconfigure the serial connection
    if salvage==0:
        ref=stripString(ITLA(sercon,REG_Serial,0,0))
        if len(ref)<5:
            print ('problems with communication before start FW upgrade')
            return(sercon,'problems with communication before start FW upgrade')
        ITLA(sercon,REG_Resena,0,1)
    ITLA(sercon,REG_Iocap,64,1) #bits 4-7 are 0x04 for 115200 baudrate
    #validate communication with the laser
    tempport=sercon.portstr
    sercon.close()
    sercon = serial.Serial(tempport, 115200, timeout=1)
    if stripString(ITLA(sercon,REG_Serial,0,0))!=ref:
        return(sercon,'After change baudrate: serial discrepancy found. Aborting. '+str(stripString(ITLA(sercon,REG_Serial,0,0)))+' '+str( params.serial))
    #load the ray file
    raybin=raydata
    if (len(raybin)&0x01):raybin.append('\x00')
    ITLA(sercon,REG_Dlconfig,2,1)  #first do abort to make sure everything is ok
    #print ITLALastError()
    if ITLALastError()!=ITLA_NOERROR:
        return( sercon,'After dlconfig abort: error found. Aborting. ' + str(ITLALastError()))
    #initiate the transfer; INIT_WRITE=0x0001; TYPE=0x1000; RUNV=0x0000
    #temp=ITLA(sercon,REG_Dlconfig,0x0001 ^ 0x1000 ^ 0x0000,1)
    #check temp for the correct feedback
    ITLA(sercon,REG_Dlconfig,3*16*256+1,1) # initwrite=1; type =3 in bits 12:15
    #print ITLALastError()
    if ITLALastError()!=ITLA_NOERROR:
        return(sercon,'After dlconfig init_write: error found. Aborting. '+str(ITLALastError() ))
    return(sercon,'')

def ITLAFWUpgradeWrite(sercon,count):
    global tempport,raybin
    #start writing bits
    teller=0
    while teller<count:
        ITLA_send_only(sercon,REG_Ear,struct.unpack('>H',raybin[teller:teller+2])[0],1)
        teller=teller+2
    raybin=raybin[count:]
    #write done. clean up
    return('')

def ITLAFWUpgradeComplete(sercon):
    global tempport,raybin
    time.sleep(0.5)
    sercon.flushInput()
    sercon.flushOutput()
    ITLA(sercon,REG_Dlconfig,4,1) # done (bit 2)
    if ITLALastError()!=ITLA_NOERROR:
        return(sercon,'After dlconfig done: error found. Aborting. '+str(ITLALastError()))
    #init check
    ITLA(sercon,REG_Dlconfig,16,1) #init check bit 4
    if ITLALastError()==ITLA_CPERROR:
        while (ITLA(sercon,REG_Nop,0,0)&0xff00)>0:
            time.sleep(0.5)
    elif ITLALastError()!=ITLA_NOERROR:
        return(sercon,'After dlconfig done: error found. Aborting. '+str(ITLALastError() ))
    #check for valid=1
    temp=ITLA(sercon,REG_Dlstatus,0,0)
    if (temp&0x01==0x00):
        return(sercon,'Dlstatus not good. Aborting. ')           
    #write concluding dlconfig
    ITLA(sercon,REG_Dlconfig,3*256+32, 1) #init run (bit 5) + runv (bit 8:11) =3
    if ITLALastError()!=ITLA_NOERROR:
        return(sercon, 'After dlconfig init run and runv: error found. Aborting. '+str(ITLALastError()))
    time.sleep(1)
    #set the baudrate to 9600 and reconfigure the serial connection
    ITLA(sercon,REG_Iocap,0,1) #bits 4-7 are 0x0 for 9600 baudrate
    sercon.close()
    #validate communication with the laser
    sercon = serial.Serial(tempport, 9600, timeout=1)
    ref=stripString(ITLA(sercon,REG_Serial,0,0))
    if len(ref)<5:
        return( sercon,'After change back to 9600 baudrate: serial discrepancy found. Aborting. '+str(stripString(ITLA(sercon,REG_Serial,0,0)))+' '+str( params.serial))
    return(sercon,'')

def ITLASplitDual(input,rank):
    teller=rank*2
    return(ord(input[teller])*256+ord(input[teller+1]))


             