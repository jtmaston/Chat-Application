import socket
import threading
import time

from clientComponents.PacketHandler import ClientPacket
from clientComponents.PacketHandler import HandshakePacket
from clientComponents.PacketHandler import PacketFormatValidator

routes = dict([])  # routes dict, see below

"""REMEMBER: routes now holds dictionary with structure {username: {'ip_in': sender ip, 'ip_out': listener ip}}"""


def Handshake(connection):  # this is how the communication begins
    HSPacket = HandshakePacket(connection.recv(1024))  # load json from recvd packet
    if not (PacketFormatValidator(HSPacket) and HSPacket.command == 'Handshake'):  # if somehow the chat is
        # corrupted, send it back
        HSPacket.command = 'Bad'
        connection.send(HSPacket.DumpJson())
        print("Broken connection! Sending abort message...")
        return False
    else:
        if HSPacket.command == 'test':
            return False
        HSPacket.command = 'read_back'  # integrity check, basically see if anything gets kaput on the way
        connection.send(HSPacket.DumpJson())
        HSPacket.LoadJson(connection.recv(1024))
        if HSPacket.command == 'ok':
            print(f"Handshake established with {connection.getpeername()}")  # handshake ok, start it
            HSPacket.command = 'ready'
            connection.send(HSPacket.DumpJson())
            return HSPacket
        else:
            return False


class CommunicationThread(threading.Thread):  # this is the comms thread
    def __init__(self, Username):
        threading.Thread.__init__(self)
        self.username = Username
        pass

    def run(self):
        global routes
        inputConnection = dict(routes[self.username])['ip_in']  # get the connection on which to listen
        chatPacket = ClientPacket()  # create a blank packet
        while True:
            chatPacket.LoadJson(inputConnection.recv(1024))  # getting the message from client
            outputConnection = dict(routes[chatPacket.destinationUsername])['ip_out']  # find which socket the
            # message should be sent to
            outputConnection.send(chatPacket.DumpJson())  # and send it


class routeTesterThread(threading.Thread):  # debug, will remove later
    def __init__(self):
        threading.Thread.__init__(self)
        pass

    def run(self):
        while True:
            global routes
            time.sleep(1)
            print(routes)


def main():
    LOCALHOST = ("127.0.0.1", 1864)  # server will get connections on port 2306
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(LOCALHOST)
    print("Server started")
    print("Waiting for client request..")
    # routeTesterThread().start()
    while True:
        server.listen(1)
        ClientSocket, clientAddress = server.accept()
        user = Handshake(ClientSocket)  # handshake part
        if user:  # this part separates the listener and sender sockets
            if user.connectionType == 'out':  # the socket on which the server sends data
                try:
                    routes[user.senderUsername].append(('ip_in', ClientSocket))
                except KeyError:
                    routes[user.senderUsername] = [('ip_in', ClientSocket)]
            if user.connectionType == 'in':  # the socket on which the server recieves data
                try:
                    routes[user.senderUsername].append(('ip_out', ClientSocket))
                except KeyError:
                    routes[user.senderUsername] = [('ip_out', ClientSocket)]
            CommThread = CommunicationThread(user.senderUsername)
            try:  # this is a check to see if both ip_in and ip_out are assigned, communication doesn't start until
                # both are
                if dict(routes[user.senderUsername])['ip_in'] and dict(routes[user.senderUsername])['ip_out']:
                    pass
            except KeyError:
                continue
            else:
                CommThread.start()  # start the commnuication thread


if __name__ == '__main__':
    main()
