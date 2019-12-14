# Import socket module
import json
import socket
import sys
from kbtrhead import KeyboardThread

def Handshake(connection):
    ip_port = connection.getsockname()  # get ip:port data, to be used in json
    HandshakeTest = {  # json template, TODO: un-hardcode it!
        'command': 'hello',
        'host': ip_port[0],
        'port': ip_port[1],
        'username': 'Alexey',
        'message': '',
        'destination': 'David'
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
        return data
    else:
        data['command'] = 'not ok'
        connection.send(json.dumps(data).encode('UTF-8'))  # send the not all-clear
        return False


def Dialogue(connection):
    pass


def client():
    HOSTNAME = ("127.0.0.1", 8080)  # hostname and port go here

    client_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # init connection

    packet = False
    while not packet:
        try:                # try to connect, if you can't, shutdown
            client_conn.connect(HOSTNAME)
        except ConnectionRefusedError:
            print("Server may be down! Aborting...")
            sys.exit(1)     # c-style error exit code
        else:
            packet = Handshake(client_conn)  # go ahead and check if the handshake went all right
            if not packet:
                client_conn.close()     # if the pipe is broken, reset connection and try again

    # while True:
    #     message = input('>')
    #     packet['message'] = message
    #     packet['command'] = 'send'
    #     client_conn.send(json.dumps(packet).encode('UTF-8'))
    #     packet = json.loads(client_conn.recv(1024))
    #     print(packet['message'])
    client_conn.close()



if __name__ == '__main__':
    client()