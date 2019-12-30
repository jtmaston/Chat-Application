import threading

from PacketHandler import DebugFlag
from clientComponents.Listener import InputQueue
from clientComponents.Listener import listener
from clientComponents.Sender import OutputQueue
from clientComponents.Sender import sender


class ThreadMessage:  # maybe unnecessary
    handled = True
    message = ''


class KeyboardThread(threading.Thread):  # non-blocking input

    def __init__(self, input_cbk=None, name='keyboard-input-thread'):
        self.input_cbk = input_cbk
        super(KeyboardThread, self).__init__(name=name)
        self.start()

    def run(self):
        while True:
            self.input_cbk(input())


KeyboardMessage = ThreadMessage()


def process(inp):  # set the keyboard messages
    global KeyboardMessage
    KeyboardMessage.message = inp
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
    KeyboardThread(process)
    listenThread = ListenerThread(Username, Destination)  # start the listener therad
    listenThread.start()
    sendThread = SenderThread(Username, Destination)  # start the sender thread
    sendThread.start()
    global KeyboardMessage
    while True:
        if not KeyboardMessage.handled:
            OutputQueue.put(KeyboardMessage.message)
            KeyboardMessage.handled = True
        if not InputQueue.empty():
            ReceivedData = InputQueue.get_nowait()
            if ReceivedData:
                print(ReceivedData)


if __name__ == '__main__':
    main()
