import socket
import threading
import json
from PacketHandler import PacketFormatValidator
from PacketHandler import PotatoPackage
from PacketHandler import PacketSchema
routes = {}  # routes dict, format user: (ip,port)


def Handshake(connection):

    HSPacket = PotatoPackage(connection.recv(1024))  # load json from recvd packet
    if not (PacketFormatValidator(HSPacket) and HSPacket.command == 'hello'):
        connection.send(b"Malformed input!")
        print("Broken connection! Sending abort message...")
        return False
    else:
        HSPacket.command = 'read_back'
        connection.send(HSPacket.DumpJson())
        HSPacket.LoadJson(connection.recv(1024))
        if HSPacket.command == 'ok':
            print(f"Handshake established with {HSPacket.hostname}: {HSPacket.port}")
            HSPacket.command = 'ready'
            connection.send(HSPacket.DumpJson())
            return HSPacket
        else:
            return False


class ClientThread(threading.Thread):
    def __init__(self, Address, ClientSocket):
        threading.Thread.__init__(self)
        self.socket = ClientSocket
        self.address = Address

    def run(self):
        user = Handshake(self.socket)
        if user:
            routes[user.username] = (user.hostname, user.port)


def main():
    LOCALHOST = "127.0.0.1"
    PORT = 8080
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((LOCALHOST, PORT))
    print("Server started")
    print("Waiting for client request..")
    while True:
        server.listen(1)
        ClientSocket, clientAddress = server.accept()
        NewThread = ClientThread(clientAddress, ClientSocket)
        NewThread.start()
        # print(routes)


if __name__ == '__main__':
    main()
