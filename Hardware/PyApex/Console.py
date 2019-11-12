from Hardware.PyApex import AP2XXX
import threading
from time import sleep

Equipments = []

def __Menu():
    
    ValidChoice = False
    
    while not ValidChoice:
        print("========== MENU ==========")
        print()
        print("1. Connect to an AP2XXX")
        print("2. Connect to an AP1000")
        print("3. Communicate with an equipment")
        print("4. Close a connection")
        print("0. Quit the program")
        print()
        
        Choice = input("Enter your choice: ")
        try:
            Choice = int(Choice)
            ValidChoice = True
        except:
            print("Invalid choice\n")
            print()
            pass
    
    return Choice


def __ConnectAP2XXX():

    global Equipments
    IP = input("Enter IP Address of the AP2XXX: ")
    
    Equipment = AP2XXX(str(IP))
    if Equipment.IsConnected():
        EquipmentData = {}
        EquipmentData['equipment'] = Equipment
        EquipmentData['ip'] = IP
        EquipmentData['type'] = Equipment.GetType()
        Equipment.SetTimeOut(0.5)
        Equipments.append(EquipmentData)


def __ConnectAP1000():

    global Equipments
    IP = input("Enter IP Address of the AP1000: ")
    
    Equipment = AP1000(str(IP))
    if Equipment.IsConnected():
        EquipmentData = {}
        EquipmentData['equipment'] = Equipment
        EquipmentData['ip'] = IP
        EquipmentData['type'] = "AP1000"
        Equipment.SetTimeOut(0.5)
        Equipments.append(EquipmentData)


def __CloseConnection(Number = 0):
    
    global Equipments
    if Number >= 0 and Number < len(Equipments):
        try:
            Equipments[Number]['equipment'].Close()
            Equipments.remove(Number)
        except:
            pass


def __SelectEquipment(Action):
    
    global Equipments
    N = 1
    
    for e in Equipments:
        print(str(N) + ". " + e['type'] + " on " + e['ip'])
        N += 1
    print()
    Number = input("Choose the equipment to " + str(Action) + ": ")
    print()
    try:
        Number = int(Number) - 1
    except:
        Number = 0
    
    return Number


def __Run(equipment):
    
    print("To display help, press 'help' at prompt")
    print("To exit the software, press 'quit' at prompt")
    print()

    RecThread = __ReceiveThread(equipment['equipment'].Connexion, 0.2, 1024)
    RecThread.start()

    cmd = input(equipment['type'] + "@" + equipment['ip'] + "> ")
    try:
        cmd = str(cmd)
    except:
        cmd = ""

    while cmd.lower() != 'quit':
    
        if cmd.lower() == 'help':
            DisplayHelp()
        else:
            if cmd[-1] != '\n':
                cmd += '\n'
            equipment['equipment'].Connexion.send(cmd.encode('utf-8'))

        sleep(0.2)
        cmd = input(equipment['type'] + "@" + equipment['ip'] + "> ")

    RecThread.stop()
    RecThread.join()


class __ReceiveThread(threading.Thread):
    
    def __init__(self, Connexion, SleepTime, BytesNb = 1024):
        threading.Thread.__init__(self)
        self.Connexion = Connexion
        self.SleepTime = SleepTime
        self.BytesNb = BytesNb
        self.Running = True
      
    def run(self):
        while self.Running:        
            RecvString = self.ReceiveData()
            if RecvString != "":
                print(RecvString)
            sleep(self.SleepTime)
    
    def ReceiveData(self):
        try:
            finish = False
            RecvString = ""
            while not finish:
                rstr = self.Connexion.recv(self.BytesNb)
                if chr(rstr[len(rstr) - 1]) == '\n':
                    finish = True
                RecvString += rstr.decode('utf-8')
        except:
            pass

        return RecvString

    def stop(self):
        self.Running = False

    def IsRunning(self):
        return self.Running


def __DisplayHelp():
    
    print()
    print("--------------------------------------------------------------------------")
    print("This is a terminal for communicating asynchronously with APEX equipments")
    print("Press 'quit' to exit from the terminal and return to the main menu")
    print("Press 'help' to display this help")
    print("Any other command will be send to the connected equipment") 
    print("If no '\n' is present at the end of the command, it is automatically added")
    print("--------------------------------------------------------------------------")
    print()


def Terminal():
    '''
    Terminal is a small program to communicate with AP2XXX and AP1000 equipments.
    It acts as a standard terminal. Send data and read answers.
    '''

    Loop = True
    while Loop:

        Choice = __Menu()
    
        if Choice == 1:
            __ConnectAP2XXX()
        
        elif Choice == 2:
            __ConnectAP1000()

        elif Choice == 3:
            Index = __SelectEquipment("Communicate with")
            __Run(Equipments[Index])
        
        elif Choice == 4:
            Index = __SelectEquipment("Close")
            __CloseConnection(Index)
        
        elif Choice == 0:
            Loop = False


