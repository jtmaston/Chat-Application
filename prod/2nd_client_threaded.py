# Import socket module
import json
import socket
import sys


def Handshake(connection):
    ip_port = connection.getsockname()  # get ip:port data, to be used in json
    HandshakeTest = {  # json template, TODO: un-hardcode it!
        'command': 'hello',
        'host': ip_port[0],
        'port': ip_port[1],
        'username': 'David',
        'message': '',
        'destination': 'Alexey'
    }
    data = json.dumps(HandshakeTest)  # convert HT to json, for processing
    connection.send(data.encode('UTF-8'))  # greeting message to server, command is hello
    data = json.loads(connection.recv(1024))  # get server's response
    ReadBackCorrect = True  # check to see if readback is ok
    for i in HandshakeTest:
        if i != 'command':  # command changes so don't check it
            if HandshakeTest[i] != data[i]:
                ReadBackCorrect = False
    if ReadBackCorrect:  # send the all-clear if data is correctly transmitted
        data['command'] = 'ok'
        connection.send(json.dumps(data).encode('UTF-8'))  # send the all-clear
        return True
    else:
        data['command'] = 'not ok'
        connection.send(json.dumps(data).encode('UTF-8'))  # send the not all-clear
        return False


def client():
    HOSTNAME = ("127.0.0.1", 8080)  # hostname and port go here

    client_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # init connection

    connected = False
    while not connected:
        try:                # try to connect, if you can't, shutdown
            client_conn.connect(HOSTNAME)
        except ConnectionRefusedError:
            print("Server may be down! Aborting...")
            sys.exit(1)     # c-style error exit code
        else:
            connected = Handshake(client_conn)  # go ahead and check if the handshake went all right
            if not connected:
                client_conn.close()     # if the pipe is broken, reset connection and try again
    client_conn.close()

if __name__ == '__main__':
    client()
