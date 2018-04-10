# *-* encoding: utf-8 *-*
## streaming.py
## (ストリーミング処理を行うクラス)

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
        self.capturer = ScreenCapturer()
        self.wsio = WebSocketIO(conf)
        return
    
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
        return
    
    def ws_request_next_frame(self, data):
        img = self.capturer.capture()
        pixels = np.ravel(np.asarray(img))
        data_num = len(self.colorspace) * self.width * self.height
        if pixels.size != data_num:
            print('{} Error: Image size is wrong. (Colorspace may be wrong)'.format(WS_CONSOLE))
            self.ws_request_next_frame(data)
        buf = np.fromstring(self.app_id+'|0\x00', dtype=np.uint8)
        data = np.concatenate((buf, pixels))
        self.wsio.emit('updateMediaBlockStreamFrame', data)
        return
    
    def ws_stop_screen_capture(self, data):
        print('{} Connection closed.'.format(WS_CONSOLE))
        self.wsio.close()
        return
    
    def on_open(self):
        self.wsio.on('initialize', self.ws_initialize)
        self.wsio.on('requestNextFrame', self.ws_request_next_frame)
        self.wsio.on('stopMediaCapture', self.ws_stop_screen_capture)
        request = {
            'clientType': 'test',
            'requests': {
                'config': False,
                'version': False,
                'time': False,
                'console': False
            }
        }
        self.wsio.emit('addClient', request)
        return
    
    def start(self):
        img = self.capturer.capture()
        self.width, self.height = img.size
        self.wsio.open(self.on_open)
        return

