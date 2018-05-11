# *-* encoding: utf-8 *-*
## screenshot.py
## (画面キャプチャを行うクラス)

from threading import Thread
from subprocess import Popen, PIPE
from base64 import b64encode

class ScreenCapturer(Thread):
    def __init__(self, queue, counter, conf):
        super(ScreenCapturer, self).__init__()
        self.queue, self.counter = queue, counter
        self.cmd = 'ffmpeg -loglevel quiet -f x11grab '
        self.cmd += '-video_size {}x{} '.format(conf['width'], conf['height'])
        self.cmd += '-i :{} -vframes 1 -f image2pipe -'.format(conf['display'])
        self.active = True
    
    def terminate(self):
        self.active = False
    
    def get_frame(self):
        try:
            frame = Popen(self.cmd, shell=True, stdout=PIPE).communicate()[0]
        except:
            frame = self.get_frame()
        #frame = b64encode(frame).decode('utf-8')
        frame_num = self.counter.get_frame_num()
        return (frame_num, frame)
    
    def run(self):
        while self.active:
            frame = self.get_frame()
            self.queue.put(frame)

