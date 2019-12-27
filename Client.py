import socket
import sys
import threading

from PacketHandler import DebugFlag
from clientComponents.Listener import listener
from clientComponents.Sender import sender


class ListenerMessage:
    message = str()
    handled = False


class ListenerThread(threading.Thread):
    def __init__(self, Username, Destination):
        threading.Thread.__init__(self)
        self.Username = Username
        self.Destination = Destination

    def run(self):
        listener(self.Username, self.Destination)


class SenderThread(threading.Thread):
    def __init__(self, Username, Destination):
        threading.Thread.__init__(self)
        self.Username = Username
        self.Destination = Destination

    def run(self):
        sender(self.Username, self.Destination)


def main():
    if not DebugFlag:
        print("Hello! Please enter your username!")
        Username = input()
        print("And you are talking to?")
        Destination = input()
    else:
        Username = 'James'
        Destination = 'Danny'
        print(f"Running in debug mode! Using username {Username} and destination {Destination}")
    sendThread = SenderThread(Username, Destination)
    sendThread.start()
    listenThread = ListenerThread(Username, Destination)
    listenThread.start()


if __name__ == '__main__':
    main()
