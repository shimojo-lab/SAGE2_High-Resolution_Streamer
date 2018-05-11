# *-* encoding: utf-8 *-*
## streaming.py
## (ストリーミング処理を行うクラス)

from threading import Lock, active_count
from queue import PriorityQueue
from math import ceil
from .screenshot import *
from .websocket import *
from time import sleep
from asyncio import create_subprocess_shell

MAX_CAPTURERS = 32
MIN_CAPTURERS = 2
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
        self.conf = conf
        self.queue_max_size, self.filetype = conf['queue'], conf['filetype']
        self.title, self.color = conf['title'], conf['color']
        self.width, self.height = conf['width'], conf['height']
        self.enable_chunk, self.chunk_size = conf['chunk'], conf['chunk_size']
        self.queue = PriorityQueue(maxsize=self.queue_max_size)
        self.counter = FrameCounter()
        self.capturers = [ScreenCapturer(self.queue, self.counter, conf) for i in range(MIN_CAPTURERS)]
        self.wsio = WebSocketIO(conf)
    
    def __del__(self):
        print('{} Connection closed'.format(CONSOLE))
        self.wsio.on_close()
    
    def increase_capturer(self):
        if len(self.capturers) < MAX_CAPTURERS:
            capturer = ScreenCapturer(self.queue, self.counter, self.conf)
            capturer.start()
            self.capturers.append(capturer)
    
    def decrease_capturer(self):
        if len(self.capturers) > MIN_CAPTURERS:
            self.capturers[-1].terminate()
            self.capturers.pop()
    
    def optimize_capturers(self):
        current_queue_size = self.queue.qsize()
        self.pre_queue_size = current_queue_size
        queue_diff = current_queue_size - self.pre_queue_size
        if queue_diff<=-1 or self.queue.empty():
            self.increase_capturer()
        elif queue_diff >= 2:
            self.decrease_capturer()
    
    def ws_initialize(self, data):
        for capturer in self.capturers:
            capturer.start()
        self.app_id = data['UID'] + '|0'
        frame = self.queue.get()[1]
        request = {
            'id': self.app_id,
            'title': self.title,
            'color': self.color,
            'width': self.width,
            'height': self.height,
            'src': frame,
            'type': 'image/{}'.format(self.filetype),
            'encoding': 'base64'
        }
        #self.wsio.emit('requestToStartMediaStream', {})
        self.wsio.emit('startNewMediaBlockStream', request)
        
        print('{} Preparing for screenshot...'.format(CONSOLE))
        while not self.queue.full():
            sleep(1)
        print('{} Start streaming'.format(CONSOLE))
    
    def ws_request_next_frame(self, data):
        self.optimize_capturers()
        frame = self.queue.get()[1]
        length = len(frame)
        request = {
            'id': self.app_id,
            'state': {
                'src': None,
                'type': 'image/{}'.format(self.filetype),
                'encoding': 'base64'
            }
        }
        if self.enable_chunk=='True' and length > self.chunk_size:
            chunk_num = ceil(length/self.chunk_size)
            for index in range(chunk_num):
                self.ws_request_next_frame_chunk(frame, request, index, length, chunk_num)
        else:
            request['state']['src'] = frame
            self.wsio.emit('updateMediaBlockStreamFrame', request)
    
    def ws_request_next_frame_chunk(self, frame, request, index, length, chunk_num):
        start, end = self.chunk_size * index, self.chunk_size * (index+1)
        end = end if end<length else length
        request['state']['src'] = frame[start:end]
        request['piece'] = index,
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

