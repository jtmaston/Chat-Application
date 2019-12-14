import socket
import threading


class ClientThread(threading.Thread):
    def __init__(self, Address, ClientSocket):
        threading.Thread.__init__(self)
        self.sock = ClientSocket
        self.addr = Address
        print("New connection added: ", Address)

    def run(self):
        print("Connection from : ", self.addr)
        # self.csocket.send(bytes("Hi, This is from Server..",'utf-8'))
        msg = ''
        while True:
            data = self.sock.recv(2048)
            msg = data.decode()
            if msg == 'bye':
                break
            print("from client", msg)
            self.sock.send(bytes(msg, 'UTF-8'))
        print("Client at ", self.addr, " disconnected...")


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
