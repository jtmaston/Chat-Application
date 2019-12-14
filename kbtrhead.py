import os
import sys
import time
import threading


class ThreadMessage:
    message = ''
    handled = True
thread_message = ThreadMessage()

class KeyboardThread(threading.Thread):

    def __init__(self, input_cbk=None, name='keyboard-input-thread'):
        self.input_cbk = input_cbk
        super(KeyboardThread, self).__init__(name=name)
        self.start()

    def run(self):
        while True:
            self.input_cbk(input())


def process(inp):
    global thread_message
    thread_message.message = inp
    thread_message.handled = False


KeyboardThread(process)
i = 0
print('>', end='')
while True:
    if not thread_message.handled:
        print(f"\rMessage recieved: {thread_message.message}\n>", end='')
        thread_message.handled = True
