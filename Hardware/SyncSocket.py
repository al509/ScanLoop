from PyQt5.QtCore import QTime, QObject
from PyQt5.QtNetwork import QTcpSocket


class SyncSocket(QTcpSocket):
    def __init__(self,
                 parent: QObject = None,
                 host: str = "127.0.0.1",
                 port: int = 22,
                 short_timeout: int = 50,
                 long_timeout: int = 1000):
        super().__init__(parent=parent)

        self.host = host
        self.port = port

        self.short_timeout = short_timeout
        self.long_timeout = long_timeout

        self.start()

    def restart(self) -> None:
        self.stop()
        self.start()

    def start(self) -> None:
        if self.state() == QTcpSocket.ConnectedState:
            return
        self.connectToHost(self.host, self.port)
        self.waitForConnected(self.long_timeout)

    def stop(self) -> None:
        self.disconnectFromHost()
        if self.state() == QTcpSocket.UnconnectedState:
            return
        self.waitForDisconnected(self.long_timeout)

    def receive(self) -> str:
        time = QTime()
        time.start()

        data = ""
        while time.elapsed() <= self.long_timeout:
            if not self.waitForReadyRead(self.short_timeout):
                break
            line = str(bytes(self.readAll()).decode())

            # if line == "":
            #     break

            data += line

        return data

    def send(self, message: str) -> None:
        self.write(message.encode())
        self.flush()
        self.waitForBytesWritten(self.long_timeout)

    def set_short_timeout(self, timeout):
        self.short_timeout = timeout

    def set_long_timeout(self, timeout):
        self.long_timeout = timeout