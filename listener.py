# Import socket module
import json
import socket
import sys
import threading

from PacketHandler import HandshakePacket
from PacketHandler import ClientPacket
from PacketHandler import BadPacket


def Handshake(connection):
    # usr = input('Please enter username: ')
    usr = 'Danny'  # TODO: unhardocde
    ip_port = connection.getsockname()  # get ip:port data, to be used in json
    HSPacket = HandshakePacket(JsonData=None)  # create a packet with default handhsake settings
    HSPacket.LoadIp(ip_port)  # load the ip of the client
    HSPacket.username = usr
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
        return HSPacket
    return lambda x: BadPacket(JsonData=None)  # fallback return


def listener():
    HOSTNAME = ("127.0.0.1", 8080)  # hostname and port go here
    ClientConnection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # init connection
    try:  # try to connect, if you can't, shutdown
        ClientConnection.connect(HOSTNAME)
    except ConnectionRefusedError:
        print("Server may be down! Aborting...")
        sys.exit(1)  # c-style error exit code
    ListenerPacket = Handshake(ClientConnection)
    while ListenerPacket.command == 'BAD':
        ListenerPacket = Handshake(ClientConnection)  # go ahead and check if the handshake went all right
        if ListenerPacket.command == 'BAD':
            ClientConnection.close()  # if the pipe is broken, reset connection and try again
    print("Listening...")
    ListenerPacket.LoadJson(ClientConnection.recv(1024))
    if not ListenerPacket.processed:
        print(f"Message received from: {ListenerPacket.username}: {ListenerPacket.message}")
        ListenerPacket.processed = True
        ClientConnection.send(ListenerPacket.DumpJson())


if __name__ == '__main__':
    listener()
