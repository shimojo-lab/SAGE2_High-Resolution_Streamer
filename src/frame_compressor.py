# *-* coding: utf-8 *-*

from threading import Thread
import cv2
from base64 import b64encode
from .logger import Logger

# A class for frame compression
class FrameCompressor(Thread):
    def __init__(self, raw_frame_queue, comp_frame_queue, quality):
        super(FrameCompressor, self).__init__()
        
        self.raw_frame_queue = raw_frame_queue    # the queue for raw frames
        self.comp_frame_queue = comp_frame_queue  # the queue for compressed frames
        self.active = True                        # the flag for repeating compression
        self.param = [int(cv2.IMWRITE_JPEG_QUALITY), quality]  # the paramater for JPEG compression
    
    # compress a raw frame with JPEG
    def compress_frame(self, raw_frame):
        result, jpg_frame = cv2.imencode('.jpg', raw_frame, self.param)
        str_frame = b64encode(jpg_frame).decode('utf-8') if result else None
        return str_frame
    
    # terminate JPEG compression
    def terminate(self):
        self.active = False
    
    # repeat JPEG compression
    def run(self):
        while self.active:
            frame_num, raw_frame = self.raw_frame_queue.get()
            comp_frame = self.compress_frame(raw_frame)
            self.comp_frame_queue.put((frame_num, comp_frame))

