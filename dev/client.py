# Import socket module
import json
import socket


def Handshake(connection):
    ip_port = connection.getsockname()
    HandshakeTest = {
        'command': 'hello',
        'host': ip_port[0],
        'port': ip_port[1],
        'username': 'Alexey',
        'message': 'Henlo',
        'destination': 'David'
    }
    data = json.dumps(HandshakeTest)
    connection.send(data.encode('UTF-8'))

def client():
    host = '127.0.0.1'
    port = 12345
    connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connection.connect((host, port))
    Handshake(connection)
    connection.close()


if __name__ == '__main__':
    client()
