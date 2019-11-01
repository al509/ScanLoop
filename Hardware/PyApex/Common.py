
def Send(Connexion, Command):
    from Hardware.PyApex.Constantes import APXXXX_ERROR_ARGUMENT_TYPE, APXXXX_ERROR_BADCOMMAND
    from Hardware.PyApex.Errors import ApexError
    from sys import exit
    from socket import timeout

    if not isinstance(Command, str):
        Connexion.close()
        raise ApexError(APXXXX_ERROR_ARGUMENT_TYPE, "Command")
    try:
        Connexion.send(Command.encode('utf-8'))
    except timeout:
        Connexion.close()
        raise ApexError(APXXXX_ERROR_BADCOMMAND, Command)


def Receive(Connexion, ByteNumber=1024):
    from Hardware.PyApex.Constantes import APXXXX_ERROR_ARGUMENT_TYPE, APXXXX_ERROR_COMMUNICATION
    from Hardware.PyApex.Errors import ApexError
    from sys import exit
    from socket import timeout

    if not isinstance(ByteNumber, int):
        Connexion.close()
        raise ApexError(APXXXX_ERROR_ARGUMENT_TYPE, "ByteNumber")
    try:
        data = Connexion.recv(ByteNumber)
    except timeout:
        Connexion.close()
        raise ApexError(APXXXX_ERROR_COMMUNICATION, Connexion.getsockname()[0])
    else:
        return data.decode('utf-8')


def ReceiveUntilChar(Connexion, EndCharacter = "\n"):
    from Hardware.PyApex.Constantes import APXXXX_ERROR_ARGUMENT_TYPE, APXXXX_ERROR_COMMUNICATION
    from Hardware.PyApex.Errors import ApexError
    from sys import exit
    from socket import timeout

    if not isinstance(EndCharacter, str):
        Connexion.close()
        raise ApexError(APXXXX_ERROR_ARGUMENT_TYPE, "EndCharacter")
    try:
        data_total = ""
        while True:
            data = (Connexion.recv(1024)).decode('utf-8')
            if data.find(EndCharacter) >= 0:
                data_total += data[:data.find(EndCharacter)] + EndCharacter
                break
            else:
                data_total += data
    except timeout:
        Connexion.close()
        raise ApexError(APXXXX_ERROR_COMMUNICATION, Connexion.getsockname()[0])
    else:
        return data_total
