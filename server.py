import socket
import threading
import json
from cerberus import Validator

PacketSchema = {
    'command': {'type': 'string'},
    'host': {'type': 'string'},
    'port': {'type': 'integer'},
    'username': {'type': 'string'},
    'message': {'type': 'string'},
    'destination': {'type': 'string'},
    'processed': {'type': 'boolean'}
}

routes = {}  # routes dict, format user: (ip,port)


class ClientData:
    hostname = '0.0.0.0'
    port = 8000
    username = 'default'
    message = 'placeholder'
    command = 'default'
    destination = 'someone else'
    processed = False

    def load(self, json_data):
        self.hostname = json_data['host']
        self.port = json_data['port']
        self.username = json_data['username']
        self.message = json_data['message']
        self.command = json_data['command']
        self.destination = json_data['destination']
        self.processed = json_data['processed']

    def __str__(self):
        return self.hostname + '\n' + str(self.port) + '\n' + self.username


def Handshake(connection):
    v = Validator()
    data = json.loads(connection.recv(1024))
    if not (v.validate(data, PacketSchema) and data['command'] == 'hello'):
        connection.send(b"Malformed input!")
        return False
    else:
        data['command'] = 'read_back'
        connection.send(json.dumps(data).encode('UTF-8'))
        data = json.loads(connection.recv(1024))
        if data['command'] == 'ok':
            print(f"Handshake established with {data['host']}: {data['port']}")
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
            routes[user['username']] = (user['host'], user['port'])


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
        clientsock, clientAddress = server.accept()
        newthread = ClientThread(clientAddress, clientsock)
        newthread.start()
        print(routes)


if __name__ == '__main__':
    main()
