# *-* encoding: utf-8 *-*
## streaming.py
## (ストリーミング処理を行うクラス)

from multiprocessing import Queue
from .screenshot import *
from .websocket import *

CONSOLE = 'SAGE2_Streamer>'

class SAGE2Streamer:
    def __init__(self, conf):
        self.title = conf['title']
        self.color = conf['color']
        self.colorspace = conf['colorspace']
        self.queue = Queue(maxsize=conf['queue'])
        self.wait_time = conf['queue_wait']
        self.capturer = ScreenCapturer(self.queue, conf)
        self.wsio = WebSocketIO(conf)
    
    def fetch_frame(self):
        while self.queue.empty():
            print('{} Warning: Queue is empty (Screenshot is too slow)'.format(CONSOLE))
            sleep(self.wait_time)
        frame = self.queue.get()
        return frame
   
    def ws_initialize(self, data):
        self.app_id = data['UID']
        request = {
            'id': self.app_id + '|0',
            'width': self.width,
            'height': self.height,
            'title': self.title,
            'color': self.color,
            'colorspace': self.colorspace
        }
        self.wsio.emit('startNewMediaBlockStream', request)
        self.capturer.start(self.app_id)
        print('{} Preparing for screenshot...'.format(CONSOLE))
        while not self.queue.full():
            sleep(1)
        print('{} Start streaming'.format(CONSOLE))
    
    def ws_request_next_frame(self, data):
        frame = self.fetch_frame()
        self.wsio.emit('updateMediaBlockStreamFrame', frame)
    
    def ws_stop_screen_capture(self, data):
        print('{} Connection closed.'.format(WS_CONSOLE))
        self.wsio.close()
        self.capturer.terminate()
        self.capturer.join()
    
    def on_open(self):
        self.wsio.on('initialize', self.ws_initialize)
        self.wsio.on('requestNextFrame', self.ws_request_next_frame)
        self.wsio.on('stopMediaCapture', self.ws_stop_screen_capture)
        request = {
            'clientType': self.title,
            'requests': {
                'config': False,
                'version': False,
                'time': False,
                'console': False
            }
        }
        self.wsio.emit('addClient', request)
    
    def start(self):
        print('{} Preparing for WebSocket...'.format(CONSOLE))
        frame = self.capturer.take_screenshot()
        self.width, self.height = frame.size
        self.wsio.open(self.on_open)

