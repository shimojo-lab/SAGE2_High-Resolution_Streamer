# *-* encoding: utf-8 *-*
## streaming.py
## (ストリーミング処理を行うクラス)

from multiprocessing import Queue as mp_queue
from io import BytesIO
from PIL import Image
from math import ceil
from .base64 import *
from .websocket import *
from time import sleep

CONSOLE = 'SAGE2_Streamer>'

class SAGE2Streamer:
    def __init__(self, conf):
        self.str_queue = mp_queue(maxsize=conf['str_queue'])
        self.counter = FrameCounter()
        self.title, self.color = conf['title'], conf['color']
        self.app_id, self.chunk_size = None, conf['chunk_size']
        self.filetype, self.width, self.height = conf['filetype'], conf['width'], conf['height']
        self.encoder = Base64Encoder(self.str_queue, conf)
        self.wsio = WebSocketIO(conf)
    
    def __del__(self):
        print('{} Connection closed'.format(CONSOLE))
        self.wsio.close()
        self.encoder.terminate()
        self.encoder.join()
    
    def fetch_str_frame(self):
        str_frame = self.str_queue.get()
        return str_frame
    
    def ws_initialize(self, data):
        self.encoder.start()
        self.app_id = data['UID'] + '|0'
        str_frame = self.fetch_str_frame()
        request = {
            'id': self.app_id,
            'title': self.title,
            'color': self.color,
            'width': self.width,
            'height': self.height,
            'src': str_frame,
            'type': 'image/{}'.format(self.filetype),
            'encoding': 'base64'
        }
        self.wsio.emit('requestToStartMediaStream', {})
        self.wsio.emit('startNewMediaStream', request)
        
        print('{} Preparing for screenshot...'.format(CONSOLE))
        while not self.str_queue.full():
            sleep(1)
        print('{} Start streaming'.format(CONSOLE))
    
    def ws_request_next_frame(self, data):
        str_frame = self.fetch_str_frame()
        length = len(str_frame)
        if length > self.chunk_size:
            chunk_num = ceil(length/self.chunk_size)
            for i in range(chunk_num):
                start, end = self.chunk_size * i, self.chunk_size * (i+1)
                end = end if end<length else length
                chunk = str_frame[start:end]
                self.ws_request_next_frame_chunk(i, chunk, chunk_num)
        else:
            request = {
                'id': self.app_id,
                'state': {
                    'src': str_frame,
                    'type': 'image/{}'.format(self.filetype),
                    'encoding': 'base64'
                },
            }
            self.wsio.emit('updateMediaStreamFrame', request)
    
    def ws_request_next_frame_chunk(self, index, chunk, chunk_num):
        request = {
            'id': self.app_id,
            'state': {
                'src': chunk,
                'type': 'image/{}'.format(self.filetype),
                'encoding': 'base64'
            },
            'piece': index,
            'total': chunk_num
        }
        self.wsio.emit('updateMediaStreamChunk', request)
    
    def on_open(self):
        self.wsio.on('initialize', self.ws_initialize)
        self.wsio.on('requestNextFrame', self.ws_request_next_frame)
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
        self.wsio.open(self.on_open)

