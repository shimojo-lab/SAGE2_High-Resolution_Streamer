# *-* encoding: utf-8 *-*
## screenshot.py
## (画面キャプチャを行うクラス)

from multiprocessing import Process, Queue
from subprocess import check_call
from PIL import Image
import numpy as np
from os import unlink
from io import BytesIO
from base64 import b64encode
from time import sleep

class ScreenCapturer(Process):
    def __init__(self, queue, conf):
        super(ScreenCapturer, self).__init__()
        self.queue = queue
        self.display, self.style = conf['display'], conf['style']
    
    def take_screenshot(self):
        num = np.random.randint(10)
        tmp_path = './src/tmp/frame{}.{}'.format(num, self.style)
        cmd = ['env', 'DISPLAY={}'.format(self.display), 'scrot', tmp_path]
        try:
            check_call(cmd)
            frame = Image.open(tmp_path)
        except:
            frame = self.take_screenshot()
        try:
            os.unlink(tmp_path)
        except:
            return frame
        return frame
   
    def convert_to_base64(self, frame):
        buf = BytesIO()
        frame.save(buf, format='JPEG')
        frame_str = b64encode(buf.getvalue())
        return frame_str
    
    def run(self):
        while True:
            frame = self.take_screenshot()
            frame_str = self.convert_to_base64(frame)
            if not self.queue.full():
                self.queue.put(frame_str)
'''
class Base64Converter(Process):
    def __init__(self, queue):
        super(ScreenCapturer, self).__init__()
        self.queue = Queue(max_size=8)
    
    def fetch_frame(self):
         frame = self.queue.get()
         return frame
    
    def convert(self, frame):
         buf = BytesIO()
         frame.save(buf, format='JPEG')
         frame_str = b64encode(buf.getvalue())
         return frame_str
    
    def run(self):
        while True:
            if not self.queue.full():
                frame = self.fetch_frame()
                frame_str = self.convert(frame)
                self.queue.put(frame_str)
'''

