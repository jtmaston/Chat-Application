import threading

from PacketHandler import DebugFlag
from clientComponents.Listener import listener
from clientComponents.Sender import sender


class ListenerMessage:  # non-blocking listener message
    message = str()
    handled = False


class ListenerThread(threading.Thread):  # non-blocking listener thread
    def __init__(self, Username, Destination):
        threading.Thread.__init__(self)
        self.Username = Username
        self.Destination = Destination

    def run(self):
        listener(self.Username, self.Destination)


class SenderThread(threading.Thread):  # and a non-blocking sender thread
    def __init__(self, Username, Destination):
        threading.Thread.__init__(self)
        self.Username = Username
        self.Destination = Destination

    def run(self):
        sender(self.Username, self.Destination)


def main():
    if not DebugFlag:  # check the debug flag
        print("Hello! Please enter your username!")  # auth section
        Username = input()
        print("And you are talking to?")
        Destination = input()
    else:
        Username = 'James'
        Destination = 'James'
        print(f"Running in debug mode! Using username {Username} and destination {Destination}")
    sendThread = SenderThread(Username, Destination)  # start the sender thread
    sendThread.start()
    listenThread = ListenerThread(Username, Destination)  # start the listener therad
    listenThread.start()


if __name__ == '__main__':
    main()
