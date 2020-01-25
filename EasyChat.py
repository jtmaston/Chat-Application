import _queue

from kivy.app import App
from kivy.clock import Clock
from kivy.config import Config

from clientComponents import Client
from clientComponents.Listener import InputQueue
from clientComponents.Sender import OutputQueue


class ChatApp(App):
    def __init__(self):
        super(ChatApp, self).__init__()
        Clock.schedule_interval(self.listen_to_queue, 0.5)

    def on_request_close(self, timestamp):
        del timestamp
        self.disconnect()
        return True

    def connect(self):
        username = self.root.ids.username.text
        destination = self.root.ids.destination.text
        try:
            Client.run(username, destination)
        except ConnectionError:
            self.root.current = 'errorScreen'
        else:
            self.root.current = 'chatRoom'

    def send(self):
        OutputQueue.put(self.root.ids.message.text)
        self.on_message("[b][color=2980b9]You:[/color][/b] " + self.root.ids.message.text)
        self.root.ids.message.text = ''

    def on_message(self, msg):
        self.root.ids.chat_logs.text += f'\t {msg} \n'

    def listen_to_queue(self, exec_time):
        del exec_time
        try:
            data = InputQueue.get_nowait()
        except _queue.Empty:
            return 0
        else:
            data = f'{data[1]}: {data[0]}'
            self.on_message(data)

    def disconnect(self):
        OutputQueue.put('halt')
        InputQueue.put('halt')
        self.stop()


Application = ChatApp()
if __name__ == '__main__':
    Config.set('graphics', 'width', '600')
    Config.set('graphics', 'height', '900')
    Application.run()
    OutputQueue.put('halt')
    InputQueue.put('halt')
