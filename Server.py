import socket
import sqlite3 as sql

from serverComponents.protocols import Start


def main():
    LOCALHOST = ("127.0.0.1", 1864)  # server will get connections on port 2306
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(LOCALHOST)
    db = sql.connect('chat.db')
    try:
        db.cursor().execute('select * from chat').fetchall()
    except sql.OperationalError:
        db.cursor().execute('create table chat('
                            'id INTEGER PRIMARY KEY AUTOINCREMENT,'
                            'sender_username VARCHAR(100) NOT NULL,'
                            'destination_username VARCHAR(100) NOT NULL,'
                            'message_text TEXT NOT NULL)')

    print("Server started")
    print("Waiting for client request..")

    while True:
        server.listen(1)
        ClientSocket, clientAddress = server.accept()
        Start(ClientSocket)


if __name__ == '__main__':
    main()
