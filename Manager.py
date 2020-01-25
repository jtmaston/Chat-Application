import _queue
import threading
from multiprocessing import Queue, Process

from serverComponents.protocols import init, serverQueue

commandQueue = Queue()


class KeyboardThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        while True:
            data = input('>')
            commandQueue.put(data)


if __name__ == '__main__':
    KeyboardThread().start()

    while True:
        try:
            command = commandQueue.get_nowait()
        except _queue.Empty:
            continue
        try:
            serverMessage = serverQueue.get_nowait()
            print(serverMessage)
        except _queue.Empty:
            pass
        else:
            print(serverMessage)

        if command == 'start':
            try:
                server.is_alive()
            except (ValueError, NameError):
                print('\rStarting', end='\n>')
                server = Process(target=init)
                server.start()
            else:
                if server.is_alive():
                    print('\rServer already running!', end='\n>')
                else:
                    print('\rStarting', end='\n>')
                    server = Process(target=init)
                    server.start()
        elif command == 'stop':
            try:
                server.terminate()
                server.join()
                server.close()
            except (ValueError, NameError):
                print('\rServer not online!', end='\n>')
        elif command == 'status':
            try:
                if server.is_alive():
                    print('\rServer running', end='\n>')
                else:
                    print('\rServer halted!', end='\n>')
            except (ValueError, NameError):
                print('\rServer halted!', end='\n>')
        elif command == 'help':
            print('\rhelp - displays help\n'
                  'start - starts the server\n'
                  'stop - stops the server\n'
                  'status - displays server status', end='\n>')
        else:
            print(f"\r{command} is not a recognized command, type 'help' for a list of available commands", end='\n>')
