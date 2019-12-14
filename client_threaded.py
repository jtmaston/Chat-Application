# Import socket module
import json
import socket
import sys
from PacketHandler import HandshakePacket


def Handshake(connection):
    ip_port = connection.getsockname()  # get ip:port data, to be used in json
    HSPacket = HandshakePacket(JsonData=False)  # create a packet with default handhsake settings
    HSPacket.LoadIp(ip_port)                # load the ip of the client
    data = HSPacket.DumpJson()              # dump content to transmittable json type
    connection.send(data)  # greeting message to server, command is hello
    ResponsePacket = HandshakePacket(connection.recv(1024)) # get the reply from server
    HSPacket.command = 'read_back'  # update initial packet command

    ReadBackCorrect = (ResponsePacket == HSPacket)  # compare packages for errors
    if ReadBackCorrect:
        HSPacket.command = 'ok' # send the all_clear
        data = HSPacket.DumpJson()
        connection.send(data)
    else:
        return False        # fail
    HSPacket.LoadJson(connection.recv(1024))    # get the all-clear from server
    if HSPacket.command == 'ready':
        return True     # handshake ends
    return False        # fallback return


def Dialogue(connection):
    pass


def client():
    HOSTNAME = ("127.0.0.1", 8080)  # hostname and port go here
    client_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # init connection
    DialoguePacket = False
    while not DialoguePacket:
        try:  # try to connect, if you can't, shutdown
            client_conn.connect(HOSTNAME)
        except ConnectionRefusedError:
            print("Server may be down! Aborting...")
            sys.exit(1)  # c-style error exit code
        else:
            DialoguePacket = Handshake(client_conn)  # go ahead and check if the handshake went all right
            if not DialoguePacket:
                client_conn.close()  # if the pipe is broken, reset connection and try again
    client_conn.close()


if __name__ == '__main__':
    client()
