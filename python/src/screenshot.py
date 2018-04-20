# *-* encoding: utf-8 *-*
## screenshot.py
## (画面キャプチャを行うクラス)

from threading import Thread
from queue import Queue
from subprocess import check_call
from PIL import Image
from numpy import random
from os import unlink

class ScreenCapturer(Thread):
    def __init__(self, img_queue, conf):
        super(ScreenCapturer, self).__init__()
        self.img_queue = img_queue
        self.display, self.filetype = conf['display'], conf['filetype']
    
    def take_screenshot(self):
        tmp_path = './src/.tmp/frame{}.{}'.format(random.randint(10), self.filetype)
        cmd = ['env', 'DISPLAY={}'.format(self.display), 'scrot', tmp_path]
        try:
            check_call(cmd)
            img_frame = Image.open(tmp_path)
            unlink(tmp_path)
        except:
            img_frame = self.take_screenshot()
        return img_frame
    
    def run(self):
        while True:
            img_frame = self.take_screenshot()
            if not self.img_queue.full():
                self.img_queue.put(img_frame)

