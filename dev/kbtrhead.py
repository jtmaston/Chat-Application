import os
import sys
import threading


class KeyboardThread(threading.Thread):

    def __init__(self, input_cbk=None, name='keyboard-input-thread'):
        self.input_cbk = input_cbk
        super(KeyboardThread, self).__init__(name=name)
        self.start()

    def run(self):
        while True:
            self.input_cbk(input())


def process(inp):
    print(inp)


KeyboardThread(process)
i = 0
while True:
    os.sleep(1)
    i += 1
    print(i)
