import socket
from _thread import *
import threading
import json
from datetime import datetime
from cerberus import Validator

ThreadLock = threading.Lock()


class ClientData:
    hostname = '0.0.0.0'
    port = 8000
    username = 'default'
    message = 'placeholder'
    command = 'default'
    destination = 'someone else'

    def load(self, json_data):
        self.hostname = json_data['host']
        self.port = json_data['port']
        self.username = json_data['usr']
        self.message = json_data['message']
        self.command = json_data['command']
        self.destination = json_data['destination']

    def __str__(self):
        return self.hostname + '\n' + str(self.port) + '\n' + self.username


def greeting(host, port, username):
    json_data = {
        'command': 'ReadBack',
        'host': host,
        'port': port,
        'usr': username
    }
    return json.dumps(json_data)  # returns a string


def Handshake(connection):
    client = ClientData()
    HandshakeSchema = {
        'command': {'type': 'string'},
        'host': {'type': 'string'},
        'port': {'type': 'int'},
        'username': {'type': 'string'},
        'message': {'type': 'string'},
        'destination': {'type': 'string'}
    }
    v = Validator()

    data = json.loads(connection.recv(1024))
    if not (v.validate(data, HandshakeSchema) and data['command'] == 'hello'):
        connection.send(b"Malformed input!")
        return False
    else:
        client.load(data)
        return client


def ClientThread(connection):
    IsConnected = True
    ConnectionExitedOk = None
    # HandShake
    # if Handshake(connection):
    #     IsConnected = True
    # else:
    #     ConnectionExitedOk = False
    #     ThreadLock.release()
    #data = json.loads(connection.recv(1024))
    data = connection.recv(1024)
    print(data)
    # while IsConnected:
    #     data = json.loads(connection.recv(1024))
    #     data = connection.recv(1024)
    #     print(data)
    #     if data['command'] == 'end':
    #         IsConnected = False
    #         ConnectionExitedOk = True
    #         ThreadLock.release()


def Main():
    host = ""

    # reverse a port on your computer
    # in our case it is 12345 but it
    # can be anything
    port = 12345
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host, port))
    print("socket binded to port", port)

    # put the socket into listening mode
    s.listen(5)
    print("socket is listening")

    # a forever loop until client wants to exit
    while True:
        # establish connection with client
        c, addr = s.accept()

        # lock acquired by client
        ThreadLock.acquire()
        print('Connected to :', addr[0], ':', addr[1])

        # Start a new thread and return its identifier
        start_new_thread(ClientThread, (c,))
    s.close()


if __name__ == '__main__':
    Main()
