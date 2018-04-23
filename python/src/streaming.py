# *-* encoding: utf-8 *-*
## streaming.py
## (ストリーミング処理を行うクラス)

from threading import Lock
from queue import PriorityQueue
from math import ceil
from .screenshot import *
from .websocket import *
from time import sleep

CONSOLE = 'SAGE2_Streamer>'

class FrameCounter(object):
    def __init__(self):
        self.count = 0
        self.lock = Lock()

    def get_frame_num(self):
        with self.lock:
            frame_num = self.count
            self.count += 1
        return frame_num

class SAGE2Streamer:
    def __init__(self, conf):
        self.queue = PriorityQueue(maxsize=conf['queue'])
        self.counter = FrameCounter()
        self.title, self.color = conf['title'], conf['color']
        self.app_id, self.chunk_size = None, conf['chunk_size']
        self.filetype = conf['filetype']
        self.enable_chunk = conf['chunk']
        self.capturers = [ScreenCapturer(self.queue, self.counter, conf) for i in range(conf['capturer'])]
        self.wsio = WebSocketIO(conf)
    
    def __del__(self):
        print('{} Connection closed'.format(CONSOLE))
        self.wsio.close()
    
    def ws_initialize(self, data):
        for capturer in self.capturers:
            capturer.start()
        self.app_id = data['UID'] + '|0'
        width, height = self.capturers[0].get_frame_size()
        frame = self.queue.get()[1]
        request = {
            'id': self.app_id,
            'title': self.title,
            'color': self.color,
            'width': width,
            'height': height,
            'src': frame,
            'type': 'image/{}'.format(self.filetype),
            'encoding': 'base64'
        }
        self.wsio.emit('requestToStartMediaStream', {})
        self.wsio.emit('startNewMediaStream', request)
        
        print('{} Preparing for screenshot...'.format(CONSOLE))
        while not self.queue.full():
            sleep(1)
        print('{} Start streaming'.format(CONSOLE))
    
    def ws_request_next_frame(self, data):
        frame = self.queue.get()[1]
        length = len(frame)
        if self.enable_chunk=='True' and length > self.chunk_size:
            chunk_num = ceil(length/self.chunk_size)
            for i in range(chunk_num):
                start, end = self.chunk_size * i, self.chunk_size * (i+1)
                end = end if end<length else length
                chunk = frame[start:end]
                self.ws_request_next_frame_chunk(i, chunk, chunk_num)
        else:
            request = {
                'id': self.app_id,
                'state': {
                    'src': frame,
                    'type': 'image/{}'.format(self.filetype),
                    'encoding': 'base64'
                }
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

