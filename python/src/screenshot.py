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
        self.wait_time = conf['queue_wait']
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
        num = randint(10)
        tmp_path = './src/tmp/frame{}.{}'.format(num, self.style)
        cmd = ['env', 'DISPLAY={}'.format(self.display), 'scrot', tmp_path]
        try:
            subprocess.check_call(cmd)
            frame = Image.open(tmp_path)
        except:
            frame = self.screenshot_for_linux()
        os.unlink(tmp_path)
        return frame
    
    def run(self):
        self.queue.put(self.task())
        while True:
            if self.queue.full():
                sleep(self.wait_time)
            else:
                self.queue.put(self.task())

