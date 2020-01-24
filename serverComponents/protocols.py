import json
import threading

from clientComponents.PacketHandler import ClientPacket, PacketFormatValidator, HandshakePacket

routes = dict([])


def Handshake(connection):  # this is how the communication begins
    HSPacket = HandshakePacket(connection.recv(1024))  # load json from recvd packet
    if not (PacketFormatValidator(HSPacket) and HSPacket.command == 'Handshake'):
        # corrupted, send it back
        HSPacket.command = 'Bad'
        connection.send(HSPacket.DumpJson())
        # print("Broken connection! Sending abort message...")
        return False
    else:
        if HSPacket.command == 'test':
            return False
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


class CommunicationThread(threading.Thread):  # this is the comms thread
    def __init__(self, Username):
        threading.Thread.__init__(self)
        self.username = Username

    def run(self):
        global routes
        inputConnection = dict(routes[self.username])['ip_in']
        chatPacket = ClientPacket()
        while True:
            try:
                chatPacket.LoadJson(inputConnection.recv(1024))  # getting the message from client
            except (ConnectionResetError, json.decoder.JSONDecodeError):
                print(f"closed connection to {inputConnection.getpeername()}")
                exit(0)
            try:
                outputConnection = dict(routes[chatPacket.destinationUsername])[
                    'ip_out']  # find which socket the message should be sent to
            except KeyError:
                print(f'An attempt was made to contact user {chatPacket.destinationUsername}, who is offline')
            else:
                outputConnection.send(chatPacket.DumpJson())  # and send it


def Start(ClientSocket):
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
            return False
        else:
            CommThread.start()  # start the commnuication thread
