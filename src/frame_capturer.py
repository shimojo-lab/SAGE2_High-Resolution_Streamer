# *-* coding: utf-8 *-*

from threading import Thread
from subprocess import Popen, PIPE
import numpy as np
from .logger import Logger

## A class for capturing raw frames from the virtual framebuffer
class FrameCapturer(Thread):
    def __init__(self, raw_frame_queue, loglevel, display_num, width, height, depth, fps):
        super(FrameCapturer, self).__init__()
        
        self.raw_frame_queue = raw_frame_queue   # the queue for raw frames
        self.width, self.height = width, height  # the width and height of a raw frame
        self.frame_size = width * height * 3     # the data size of a raw frame
        self.rec_fps = fps                       # the frame rate applied for ffmpeg
        self.frame_num = 0                       # the frame number
        self.active = True                       # the flag for running this class
        self.prev_frame = ''.encode()            # the raw frame captured in the previous time
        
        self.pipe = self.init_recording(loglevel, display_num, depth)
    
    # start recording with ffmpeg
    def init_recording(self, loglevel, display_num, depth):
        record_cmd = [
            'ffmpeg', '-loglevel', loglevel, '-f', 'x11grab',
            '-vcodec', 'rawvideo', '-an', '-s', '%dx%d' % (self.width, self.height),
            '-i', ':%d+0,0' % display_num, '-r', str(self.rec_fps),
            '-f', 'image2pipe', '-vcodec', 'rawvideo', '-pix_fmt', 'bgr%d' % depth, '-'
        ]
        
        try:
            pipe = Popen(record_cmd, stdout=PIPE)
        except:
            Logger.print_err('Could not start capturing frame')
            exit(1)
        return pipe
    
    # capture a raw frame from the virtual framebuffer
    def get_frame(self):
        while True:
            frame = self.pipe.stdout.read(self.frame_size)
            if frame != self.prev_frame:
                self.prev_frame = frame
                try:
                    raw_frame = np.fromstring(frame, dtype=np.uint8).reshape(self.height, self.width, 3)
                except:
                    Logger.print_err('Could not get new frame')
                    exit(1)
                return raw_frame
    
    # terminate capturing
    def terminate(self):
        self.active = False
    
    # repeat capturing raw frames
    def run(self):
        while self.active:
            raw_frame = self.get_frame()
            frame_num = self.frame_num
            self.frame_num += 1
            self.raw_frame_queue.put((frame_num, raw_frame))

