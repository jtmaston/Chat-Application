import socket
import time
import threading

from PacketHandler import HandshakePacket
from PacketHandler import ClientPacket
from PacketHandler import PacketFormatValidator

routes = dict([])  # routes dict, see below

"""REMEMBER: routes now holds dictionary with structure {username: {'ip_in': sender ip, 'ip_out': listener ip}}"""


def Handshake(connection):
    HSPacket = HandshakePacket(connection.recv(1024))  # load json from recvd packet
    if not (PacketFormatValidator(HSPacket) and HSPacket.command == 'Handshake'):
        HSPacket.command = 'Bad'
        connection.send(HSPacket.DumpJson())
        print("Broken connection! Sending abort message...")
        return False
    else:
        HSPacket.command = 'read_back'
        connection.send(HSPacket.DumpJson())
        HSPacket.LoadJson(connection.recv(1024))
        if HSPacket.command == 'ok':
            print(f"Handshake established with {connection.getpeername()}")
            HSPacket.command = 'ready'
            connection.send(HSPacket.DumpJson())
            return HSPacket
        else:
            return False


class CommunicationThread(threading.Thread):
    def __init__(self, Username):
        threading.Thread.__init__(self)
        self.username = Username
        pass

    def run(self):
        global routes
        usrList = dict(routes[self.username])
        inputConnection = usrList['ip_in']
        outputConnection = usrList['ip_out']
        print("INPUT: ", inputConnection)
        print("OUTPUT: ", outputConnection)


class routeTesterThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        pass

    def run(self):
        while True:
            global routes
            time.sleep(1)
            print(routes)


def main():
    LOCALHOST = "127.0.0.1"
    PORT = 8080
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((LOCALHOST, PORT))
    print("Server started")
    print("Waiting for client request..")
    routeTesterThread().start()
    while True:
        server.listen(1)
        ClientSocket, clientAddress = server.accept()
        user = Handshake(ClientSocket)  # handshake part
        if user:
            if user.connectionType == 'out':
                try:
                    routes[user.senderUsername].append(('ip_in', ClientSocket))
                except KeyError:
                    routes[user.senderUsername] = [('ip_in', ClientSocket)]
            if user.connectionType == 'in':
                try:
                    routes[user.senderUsername].append(('ip_out', ClientSocket))
                except KeyError:
                    routes[user.senderUsername] = [('ip_out', ClientSocket)]
        CommThread = CommunicationThread(user.senderUsername)
        try:
            a = dict(routes[user.senderUsername])['ip_in']
            a = dict(routes[user.senderUsername])['ip_out']
        except KeyError:
            continue
        else:
            CommThread.start()



if __name__ == '__main__':
    main()
