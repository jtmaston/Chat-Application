import socket
import threading

from clientComponents.Listener import listener
from clientComponents.PacketHandler import TesterPacket
from clientComponents.Sender import OutputQueue
from clientComponents.Sender import sender


class ThreadMessage:  # maybe unnecessary
    handled = True
    message = ''


KeyboardMessage = ThreadMessage()


class KeyboardThread(threading.Thread):  # non-blocking input

    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        global KeyboardMessage
        while True:
            KeyboardMessage.message = input('>')
            KeyboardMessage.handled = False


class ListenerMessage:  # non-blocking listener message
    message = str()
    handled = False


class ListenerThread(threading.Thread):  # non-blocking listener thread
    def __init__(self, Username, Destination):
        threading.Thread.__init__(self)
        self.Username = Username
        self.Destination = Destination

    def run(self):
        listener(self.Username)


class SenderThread(threading.Thread):  # and a non-blocking sender thread
    def __init__(self, Username, Destination):
        threading.Thread.__init__(self)
        self.Username = Username
        self.Destination = Destination

    def run(self):
        sender(self.Username, self.Destination)


def send(message):
    OutputQueue.put(message)


def run(Username, Destination):
    Tester = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # init connection
    TestPack = TesterPacket()
    try:  # try to connect, if you can't, shutdown
        Tester.connect(('127.0.0.1', 1864))
        Tester.send(TestPack.DumpJson())
    except ConnectionRefusedError:
        raise ConnectionError
    Tester.close()
    listenThread = ListenerThread(Username, Destination)  # start the listener therad
    listenThread.start()
    sendThread = SenderThread(Username, Destination)  # start the sender thread
    sendThread.start()
    return True
