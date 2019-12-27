import json
import socket
import sys

from PacketHandler import BadPacket, ClientPacket
from PacketHandler import HandshakePacket


def Handshake(connection, Username, Destination):
    SenderAddress = connection.getsockname()  # get ip:port data, to be used in json
    HandshakeJson = json.dumps({  # generate the handshake packet
        'senderAddress': SenderAddress,
        'destinationAddress': '',  # gets assigned by server
        'senderUsername': Username,
        'destinationUsername': 'LISTENER',
        'command': 'Handshake',
        'processed': False,
        'connectionType': 'in'
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
        HSPacket.processed = True
        return HSPacket  # handshake ends
    return lambda x: BadPacket(JsonData=None)  # fallback return


def listener(Username, Destination):
    ServerAddress = ("127.0.0.1", 8080)  # Hostname and port go here
    ClientConnection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # init connection
    try:  # try to connect, if you can't, shutdown
        ClientConnection.connect(ServerAddress)
    except ConnectionRefusedError:
        print("Server may be down! Aborting...")
        sys.exit(1)  # exiting with error code
    ListenerPacket = Handshake(connection=ClientConnection, Username=Username, Destination=Destination)
    while ListenerPacket.command == 'Bad':
        ListenerPacket = Handshake(connection=ClientConnection, Username=Username,
                                   Destination=Destination)  # go ahead and check if the handshake
        # went all right
        if ListenerPacket.command == 'Bad':
            ClientConnection.close()  # if the pipe is broken, reset connection and try again
    chatPacket = ClientPacket(None)  # create a blank packet
    while True:
        chatPacket.LoadJson(ClientConnection.recv(1024))  # get messages from the server
        print(f"\r{chatPacket.senderUsername}: {chatPacket.command[5:]}\n>", end='')  # if you got a message, print it