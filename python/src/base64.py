# *-* encoding: utf-8 *-*
## base64.py
## (Base64エンコードを行うクラス)

from multiprocessing import Process
from queue import Queue
from io import BytesIO
from base64 import b64encode
from .screenshot import *
from time import sleep

CONSOLE = 'SAGE2_Streamer>'

class Base64Encoder(Process):
    def __init__(self, str_queue, conf):
        super(Base64Encoder, self).__init__()
        self.str_queue = str_queue
        self.img_queue = Queue(maxsize=conf['img_queue'])
        self.capturer = ScreenCapturer(self.img_queue, conf)
    
    def fetch_img_frame(self):
         while self.img_queue.empty():
             print('{} Warning: Screenshot is too slow'.format(CONSOLE))
         return self.img_queue.get()
    
    def encode(self, frame):
         buf = BytesIO()
         try:
             frame.save(buf, format='JPEG')
             str_frame = b64encode(buf.getvalue())
         except:
             str_frame = self.encode(frame)
         return str_frame
    
    def run(self):
        self.capturer.start()
        while True:
            frame = self.fetch_img_frame()
            str_frame = self.encode(frame)
            if not self.str_queue.full():
                self.str_queue.put(str_frame)

