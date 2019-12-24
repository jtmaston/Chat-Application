# Import socket module
import json
import socket
import sys
import threading

from PacketHandler import HandshakePacket
from PacketHandler import ClientPacket
from PacketHandler import BadPacket
from PacketHandler import DebugFlag


def Handshake(connection, Username, Destination):
    SenderAddress = connection.getsockname()  # get ip:port data, to be used in json
    HandshakeJson = json.dumps({  # generate the handshake packet
        'senderAddress': SenderAddress,
        'destinationAddress': '',  # gets assigned by server
        'senderUsername': Username,
        'destinationUsername': 'LISTENER',
        'command': 'Handshake',
        'processed': False
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


def listener():
    if not DebugFlag:
        print("Hello! Please enter your username!")
        Username = input()
        print("And you are talking to?")
        Destination = input()
    else:
        Username = 'Danny'
        Destination = 'Alexey'
        print(f"Running in debug mode! Using username {Username} and destination {Destination}")
    ServerAddress = ("127.0.0.1", 8080)  # hostname and port go here
    ClientConnection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # init connection
    try:  # try to connect, if you can't, shutdown
        ClientConnection.connect(ServerAddress)
    except ConnectionRefusedError:
        print("Server may be down! Aborting...")
        sys.exit(1)  # exiting with error code
    ListenerPacket = Handshake(ClientConnection, Username, Destination)
    while ListenerPacket.command == 'Bad':
        ListenerPacket = Handshake(ClientConnection, Username, Destination)  # go ahead and check if the handshake
        # went all right
        if ListenerPacket.command == 'Bad':
            ClientConnection.close()  # if the pipe is broken, reset connection and try again

    print("Listening...")
    while True:
        data = ClientConnection.recv(1024)
        ListenerPacket.LoadJson(data)
        if not ListenerPacket.processed:
            print(f"Message received from: {ListenerPacket.senderUsername}: {ListenerPacket.command[5:]}")
            ListenerPacket.processed = True


if __name__ == '__main__':
    listener()
