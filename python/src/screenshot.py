# *-* encoding: utf-8 *-*
## screenshot.py
## (画面キャプチャを行うクラス)

from multiprocessing import Process
from platform import system
import subprocess
from numpy.random import *
import os
import sys
from PIL import Image
from time import sleep

class ScreenCapturer(Process):
    def __init__(self, queue, conf):
        super(ScreenCapturer, self).__init__()
        self.queue = queue
        self.wait_time, self.interval = conf['queue_wait'], conf['interval']
        self.display = conf['display']
        self.style = conf['style']
        os = system()
        if os == 'Windows':
            self.task = self.screenshot_for_windows
        elif os == 'Darwin':
            self.task = self.screenshot_for_darwin
        elif os == 'Linux':
            self.task = self.screenshot_for_linux
        else: 
            syst.stderr.write('Error: This operating system is not supported.')
            exit()
    
    def screenshot_for_windows(self, frame):
        syst.stderr.write('Windows is not supported now.')
        exit()
    
    def screenshot_for_darwin(self):
        return None
    
    def screenshot_for_linux(self):
        tmp_img = './src/tmp/frame{}.{}'.format(randint(10), self.style)
        subprocess.call(['scrot', tmp_img])
        try:
            frame = Image.open(tmp_img)
            os.unlink(tmp_img)
        except:
            frame = self.screenshot_for_linux()
        return frame
    
    def run(self):
        self.queue.put(self.task())
        while True:
            if self.queue.full():
                sleep(self.wait_time)
            else:
                self.queue.put(self.task())
                sleep(self.interval)

