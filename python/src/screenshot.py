# *-* encoding: utf-8 *-*
## screenshot.py
## (画面キャプチャを行うクラス)

from threading import Thread
from subprocess import Popen, PIPE
from io import BytesIO
from PIL import Image
from base64 import b64encode

class ScreenCapturer(Thread):
    def __init__(self, queue, counter, conf):
        super(ScreenCapturer, self).__init__()
        self.queue, self.counter = queue, counter
        self.cmd = [
            'import',
            '-display', ':{}'.format(conf['display']),
            '-w', str(conf['window']),
            '-depth', str(conf['depth']),
            '-quality', str(conf['quality']),
            '{}:-'.format(conf['filetype']) 
        ]
    
    def get_frame_size(self):
        try:
            frame = Popen(self.cmd, stdout=PIPE).communicate()[0]
            buf = BytesIO(frame)
            width, height = Image.open(buf).size
        except:
            width, height = self.get_frame_size()
        return width, height
    
    def take_screenshot(self):
        try:
            frame = Popen(self.cmd, stdout=PIPE).communicate()[0]
        except:
            frame = self.take_screenshot()
        frame = b64encode(frame).decode('utf-8')
        frame_num = self.counter.get_frame_num
        return (frame_num, frame)
    
    def run(self):
        while True:
            frame = self.take_screenshot()
            self.queue.put(frame)

