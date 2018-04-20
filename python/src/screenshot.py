# *-* encoding: utf-8 *-*
## screenshot.py
## (画面キャプチャを行うクラス)

from threading import Thread
from queue import Queue
import subprocess
from io import BytesIO
from PIL import Image

class ScreenCapturer(Thread):
    def __init__(self, img_queue, conf):
        super(ScreenCapturer, self).__init__()
        self.img_queue = img_queue
        self.display = conf['display']
    
    def take_screenshot(self):
        cmd = ['env', 'DISPLAY={}'.format(self.display), 'import', '-w', 'root', 'bmp:-']
        try:
            binary = subprocess.Popen(cmd, stdout=subprocess.PIPE).communicate()[0]
            img_frame = Image.open(BytesIO(binary))
        except:
            img_frame = self.take_screenshot()
        return img_frame
    
    def run(self):
        while True:
            img_frame = self.take_screenshot()
            if not self.img_queue.full():
                self.img_queue.put(img_frame)

