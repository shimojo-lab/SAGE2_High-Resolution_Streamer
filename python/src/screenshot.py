# *-* encoding: utf-8 *-*
## screenshot.py
## (画面キャプチャを行うクラス)

from multiprocessing import Process
import subprocess
import numpy as np
import os
import sys
from PIL import Image
from time import sleep

class ScreenCapturer(Process):
    def __init__(self, queue, conf):
        super(ScreenCapturer, self).__init__()
        self.queue, self.task = queue, self.take_screenshot
        self.display = conf['display']
        self.style = conf['style']
    
    def take_screenshot(self):
        num = np.random.randint(10)
        tmp_path = './src/tmp/frame{}.{}'.format(num, self.style)
        cmd = ['env', 'DISPLAY={}'.format(self.display), 'scrot', tmp_path]
        try:
            subprocess.check_call(cmd)
            frame = Image.open(tmp_path)
        except:
            frame = self.take_screenshot()
        try:
            os.unlink(tmp_path)
        except:
            return frame
        return frame
    
    def convert_to_base64(self, frame):
        binary = np.ravel(np.asarray(frame))
        buf = np.fromstring(self.app_id+'|0\x00', dtype=np.uint8)
        data = np.concatenate((buf, binary))
        return data
    
    def run(self):
        while True:
            frame = self.take_screenshot()
            data = self.convert_to_base64(frame)
            if not self.queue.full():
                self.queue.put(data)
    
    def start(self, app_id):
        self.app_id = app_id
        super(ScreenCapturer, self).start()

