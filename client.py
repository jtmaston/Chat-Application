# Import socket module
import json
import socket
import sys
import threading

from PacketHandler import HandshakePacket, BadPacket
from PacketHandler import ClientPacket


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


def Handshake(connection):
    ip_port = connection.getsockname()  # get ip:port data, to be used in json
    HSPacket = HandshakePacket(JsonData=None)  # create a packet with default handhsake settings
    HSPacket.LoadIp(ip_port)  # load the ip of the client
    data = HSPacket.DumpJson()  # dump content to transmittable json type
    connection.send(data)  # greeting message to server, command is hello
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

    # usr = input('Please enter username: ')
    # dest = input('Please enter destination username: ')
    DialoguePacket.username = 'Alexey'  # TODO: unhardcode
    DialoguePacket.destination = 'Danny'
    KeyboardThread(process)
    IsConnected = True
    global KeyboardMessage
    print('>', end='')
    while IsConnected:
        if not KeyboardMessage.handled:
            DialoguePacket.message = KeyboardMessage.message
            DialoguePacket.command = "send"
            DialoguePacket.processed = False
            KeyboardMessage.handled = True
            connection.send(DialoguePacket.DumpJson())
            DialoguePacket.LoadJson(connection.recv(1024))
            if DialoguePacket.command == 'sent' and DialoguePacket.processed:
                print('/rReceived./n>')


def client():
    HOSTNAME = ("127.0.0.1", 8080)  # hostname and port go here
    ClientConnection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # init connection
    DialoguePacket = False
    while not DialoguePacket:
        try:  # try to connect, if you can't, shutdown
            ClientConnection.connect(HOSTNAME)
        except ConnectionRefusedError:
            print("Server may be down! Aborting...")
            sys.exit(1)  # c-style error exit code
        else:
            DialoguePacket = Handshake(ClientConnection)  # go ahead and check if the handshake went all right
            if not DialoguePacket:
                ClientConnection.close()  # if the pipe is broken, reset connection and try again

    Dialogue(ClientConnection, DialoguePacket)

    ClientConnection.close()


if __name__ == '__main__':
    client()
