# *-* encoding: utf-8 *-*
## streaming.py
## (ストリーミング処理を行うクラス)

from multiprocessing import Queue
from math import ceil
from .screenshot import *
from .websocket import *

CONSOLE = 'SAGE2_Streamer>'

class SAGE2Streamer:
    def __init__(self, conf):
        self.queue, self.queue_wait = Queue(maxsize=conf['queue']), conf['queue_wait']
        self.title, self.color = conf['title'], conf['color']
        self.app_id, self.chunk_size = None, conf['chunk_size']
        self.capturer, self.wsio = ScreenCapturer(self.queue, conf), WebSocketIO(conf)
        self.width, self.height = self.capturer.take_screenshot().size
    
    def fetch_frame(self):
        while self.queue.empty():
            print('{} Warning: Queue is empty (Screenshot is too slow)'.format(CONSOLE))
            sleep(self.queue_wait)
        frame_str = self.queue.get()
        return frame_str
    
    def send_next_frame_chunk(self, index, chunk, chunk_num):
        request = {
            'id': self.app_id + '|0',
            'state': {
                'src': chunk.decode('utf-8'),
                'type': 'image/jpeg',
                'encoding': 'base64'
            },
            'piece': index,
            'total': chunk_num
        }
        self.wsio.emit('updateMediaStreamChunk', request)
    
    def ws_initialize(self, data):
        self.app_id = data['UID']
        self.capturer.start()
        frame_str = self.fetch_frame()
        request = {
            'id': self.app_id + '|0',
            'title': self.title,
            'color': self.color,
            'width': self.width,
            'height': self.height,
            'src': frame_str.decode('utf-8'),
            'type': 'image/jpeg',
            'encoding': 'base64'
        }
        self.wsio.emit('requestToStartMediaStream', {})
        self.wsio.emit('startNewMediaStream', request)
        
        print('{} Preparing for screenshot...'.format(CONSOLE))
        while not self.queue.full():
            sleep(1)
        print('{} Start streaming'.format(CONSOLE))
    
    def ws_request_next_frame(self, data):
        frame_str = self.fetch_frame()
        length = len(frame_str)
        if length > self.chunk_size:
            chunk_num = ceil(length/self.chunk_size)
            for i in range(chunk_num):
                start, end = self.chunk_size * i, self.chunk_size * (i+1)
                end = end if end<length else length
                chunk = frame_str[start:end]
                self.send_next_frame_chunk(i, chunk, chunk_num)
        else:
            request = {
                'id': self.app_id + '|0',
                'state': {
                    'src': frame_str.decode('utf-8'),
                    'type': 'image/jpeg',
                    'encoding': 'base64',
                    'pointersOverApp': []
                },
            }
            self.wsio.emit('updateMediaStreamFrame', request)
    
    def ws_stop_screen_capture(self, data):
        print('{} Connection closed'.format(WS_CONSOLE))
        self.wsio.close()
        self.capturer.terminate()
        self.capturer.join()
    
    def on_open(self):
        self.wsio.on('initialize', self.ws_initialize)
        self.wsio.on('requestNextFrame', self.ws_request_next_frame)
        self.wsio.on('stopMediaStream', self.ws_stop_screen_capture)
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

