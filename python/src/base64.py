# *-* encoding: utf-8 *-*
## base64.py
## (Base64エンコードを行うクラス)

from multiprocessing import Process
from queue import PriorityQueue
from threading import Lock
from base64 import b64encode
from time import sleep
from .screenshot import *

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

class Base64Encoder(Process):
    def __init__(self, str_queue, conf):
        super(Base64Encoder, self).__init__()
        self.str_queue = str_queue
        self.bin_queue = PriorityQueue(maxsize=conf['bin_queue'])
        self.counter = FrameCounter()
        self.capturers = [ScreenCapturer(self.bin_queue, self.counter, conf) for i in range(conf['capturer'])]
    
    def fetch_bin_frame(self):
        bin_frame = self.bin_queue.get()[1]
        return bin_frame
    
    def get_frame_size(self):
        frame = self.fetch_bin_frame()
        return frame.size
    
    def encode(self, frame):
        str_frame = b64encode(frame).decode('utf-8')
        return str_frame
    
    def run(self):
        for capturer in self.capturers:
            capturer.start()
        while True:
            bin_frame = self.fetch_bin_frame()
            str_frame = self.encode(bin_frame)
            self.str_queue.put(str_frame)

