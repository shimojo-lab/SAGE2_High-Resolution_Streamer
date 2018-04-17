# *-* encoding: utf-8 *-*
## streaming.py
## (ストリーミング処理を行うクラス)

from multiprocessing import Queue
import sys
import numpy as np
from .screenshot import *
from .websocket import *

WS_CONSOLE = 'WebSocketIO>'

class SAGE2Streamer:
    def __init__(self, conf):
        self.title = conf['title']
        self.color = conf['color']
        self.colorspace = conf['colorspace']
        self.queue = Queue(maxsize=conf['queue'])
        self.wait_time = conf['dequeue_wait']
        self.capturer = ScreenCapturer(self.queue, conf)
        self.wsio = WebSocketIO(conf)
        self.capturer.start()
    
    def get_screenshot(self):
        while self.queue.empty():
            #print('{} Warning: Could not get screenshots.'.format(WS_CONSOLE))
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
    
    def ws_request_next_frame(self, data):
        frame = self.get_screenshot()
        pixels = np.ravel(np.asarray(frame))
        buf = np.fromstring(self.app_id+'|0\x00', dtype=np.uint8)
        data = np.concatenate((buf, pixels))
        self.wsio.emit('updateMediaBlockStreamFrame', data)
    
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
        while self.queue.full() != False:
            sleep(1)
        frame = self.get_screenshot()
        self.width, self.height = frame.size
        self.wsio.open(self.on_open)

