# *-* encoding: utf-8 *-*
## screenshot.py
## (画面キャプチャを行うクラス)

from threading import Thread
from queue import Queue
import subprocess
from time import sleep

class ScreenCapturer(Thread):
    def __init__(self, bin_queue, conf):
        super(ScreenCapturer, self).__init__()
        self.bin_queue = bin_queue
        self.display, self.window = conf['display'], conf['window']
        self.depth, self.quality = conf['depth'], conf['quality']
        self.filetype = conf['filetype']
    
    def take_screenshot(self):
        cmd = [
            'import',
            '-display', ':{}'.format(self.display),
            '-w', str(self.window),
            '-depth', str(self.depth),
            '-quality', str(self.quality),
            '{}:-'.format(self.filetype)
        ]
        try:
            bin_frame = subprocess.Popen(cmd, stdout=subprocess.PIPE).communicate()[0]
        except:
            bin_frame = self.take_screenshot()
        return bin_frame
    
    def run(self):
        while True:
            bin_frame = self.take_screenshot()
            if self.bin_queue.full():
                sleep(0.001)
            else:
                self.bin_queue.put(bin_frame)

