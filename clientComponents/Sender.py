# Import socket module
import json
import socket
import sys
import threading

from PacketHandler import DebugFlag
from PacketHandler import HandshakePacket, BadPacket


class ThreadMessage:
    handled = True
    message = ''


class KeyboardThread(threading.Thread):

    def __init__(self, input_cbk=None, name='keyboard-input-thread'):
        self.input_cbk = input_cbk
        super(KeyboardThread, self).__init__(name=name)
        self.start()

    def run(self):
        while True:
            self.input_cbk(input())


KeyboardMessage = ThreadMessage


def process(inp):
    global KeyboardMessage
    KeyboardMessage.message = inp
    KeyboardMessage.handled = False


def Handshake(connection, Username, Destination):
    SenderAddress = connection.getsockname()  # get ip:port data, to be used in json
    HandshakeJson = json.dumps({  # generate the handshake packet
        'senderAddress': SenderAddress,
        'destinationAddress': '',  # gets assigned by server
        'senderUsername': Username,
        'destinationUsername': Destination,
        'command': 'Handshake',
        'processed': False,
        'connectionType': 'out'
    })
    HSPacket = HandshakePacket(JsonData=HandshakeJson)  # create a packet with default handhsake settings
    data = HSPacket.DumpJson()  # dump content to transmittable json type
    connection.send(data)  # send handshake packet to server
    ResponsePacket = HandshakePacket(connection.recv(1024))  # get the reply from server
    HSPacket.command = 'read_back'  # update initial packet command

    ReadBackCorrect = (ResponsePacket == HSPacket)  # compare packages for errors
    if ReadBackCorrect:
        HSPacket.command = 'ok'  # send the all_clear
        data = HSPacket.DumpJson()
        connection.send(data)
    else:
        return lambda x: BadPacket(JsonData=None)  # fail
    HSPacket.LoadJson(connection.recv(1024))  # get the all-clear from server
    if HSPacket.command == 'ready':
        return HSPacket  # handshake ends
    return lambda x: BadPacket(JsonData=None)  # fallback return


def Dialogue(connection, DialoguePacket):
    print(connection.getsockname())
    KeyboardThread(process)
    IsConnected = True
    global KeyboardMessage
    print('>', end='')
    while IsConnected:
        if not KeyboardMessage.handled:
            DialoguePacket.command = "send " + KeyboardMessage.message
            DialoguePacket.processed = False
            KeyboardMessage.handled = True
            connection.send(DialoguePacket.DumpJson())
            DialoguePacket.LoadJson(connection.recv(1024))
            if DialoguePacket.command == 'sent':
                print('\r Sent.')
            print('>', end='')


def sender(Username, Destination):
    ServerAddress = ("127.0.0.1", 8080)  # Hostname and port go here
    ClientConnection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # init connection
    try:  # try to connect, if you can't, shutdown
        ClientConnection.connect(ServerAddress)
    except ConnectionRefusedError:
        print("Server may be down! Aborting...")
        sys.exit(1)  # exiting with error code
    DialoguePacket = Handshake(ClientConnection, Username, Destination)
    while DialoguePacket.command == 'Bad':
        ListenerPacket = Handshake(ClientConnection, Username, Destination)  # go ahead and check if the handshake
        # went all right
        if ListenerPacket.command == 'Bad':
            ClientConnection.close()  # if the pipe is broken, reset connection and try again
    Dialogue(connection=ClientConnection, DialoguePacket=DialoguePacket)

    ClientConnection.close()


if __name__ == '__main__':
    sender('alexey', 'danny')
