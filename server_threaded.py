import socket
import threading
import json
from dev.PacketHandler import PacketFormatValidator
from dev.PacketHandler import PotatoPackage
from dev.PacketHandler import PacketSchema
routes = {}  # routes dict, format user: (ip,port)


def Handshake(connection):

    data = PotatoPackage(connection.recv(1024))  # load json from recvd packet
    print(isinstance(data, PacketSchema))
    if not (PacketFormatValidator(data) and data.command == 'hello'):
        connection.send(b"Malformed input!")
        print("Broken connection! Sending abort message...")
        return False
    else:
        data.command = 'read_back'
        connection.send(data.DumpJson())
        data.LoadJson(connection.recv(1024))
        if data.command == 'ok':
            print(f"Handshake established with {data.hostname}: {data.port}")
            return data
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
