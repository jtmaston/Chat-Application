import json
import socket
import sys
from multiprocessing import Queue

from PacketHandler import HandshakePacket, BadPacket

OutputQueue = Queue()


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
        return lambda x: BadPacket()  # fail
    HSPacket.LoadJson(connection.recv(1024))  # get the all-clear from server
    if HSPacket.command == 'ready':
        return HSPacket  # handshake ends
    return lambda x: BadPacket()  # fallback return


def Send(connection, DialoguePacket):  # sender function
    IsConnected = True
    while IsConnected:
        KeyboardMessage = OutputQueue.get()
        DialoguePacket.command = "send " + KeyboardMessage
        DialoguePacket.processed = False
        connection.send(DialoguePacket.DumpJson())


def sender(Username, Destination):
    ServerAddress = ("127.0.0.1", 1864)  # Hostname and port go here
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
    Send(connection=ClientConnection, DialoguePacket=DialoguePacket)

    ClientConnection.close()
