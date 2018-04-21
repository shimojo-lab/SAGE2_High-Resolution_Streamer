# *-* encoding: utf-8 *-*
## base64.py
## (Base64エンコードを行うクラス)

from multiprocessing import Process
from queue import Queue
from base64 import b64encode
from time import sleep
from .screenshot import *

CONSOLE = 'SAGE2_Streamer>'

class Base64Encoder(Process):
    def __init__(self, str_queue, conf):
        super(Base64Encoder, self).__init__()
        self.str_queue = str_queue
        self.bin_queue = Queue(maxsize=conf['bin_queue'])
        self.capturer = ScreenCapturer(self.bin_queue, conf)
    
    def fetch_bin_frame(self):
        count = 0
        while self.bin_queue.empty():
             count += 1
             sleep(0.001)
             if count == 10000:
                 print('{} Warning: Screenshot is delayed'.format(CONSOLE))
                 count = 0
        return self.bin_queue.get()
    
    def get_frame_size(self):
        frame = self.fetch_bin_frame()
        return frame.size
    
    def encode(self, frame):
        str_frame = b64encode(frame).decode('utf-8')
        return str_frame
    
    def run(self):
        self.capturer.start()
        while True:
            frame = self.fetch_bin_frame()
            str_frame = self.encode(frame)
            if self.str_queue.full():
                sleep(0.001)
            else:
                self.str_queue.put(str_frame)

