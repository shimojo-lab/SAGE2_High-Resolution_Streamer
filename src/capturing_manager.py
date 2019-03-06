# *-* encoding: utf-8 *-*

from queue import PriorityQueue
from time import sleep
from .logger import Logger
from .frame_capturer import FrameCapturer
from .frame_compressor import FrameCompressor

WAIT_TIME = 1

## a class for managing frame capturing
class CapturingManager:
    def __init__(self, display_num, width, height, depth, loglevel, fps, comp_thre_num, raw_queue_size, comp_queue_size, quality):
        self.display = display   # the display number used by the vnc server
        self.next_frame_num = 0  # the number for the next compressed frame
        self.raw_frame_queue = PriorityQueue(raw_queue_size)    # the queue for raw frames
        self.comp_frame_queue = PriorityQueue(comp_queue_size)  # the queue for compressed frames
        
        self.capturer = FrameCapturer(raw_frame_queue=self.raw_frame_queue,
                                      loglevel=loglevel,
                                      display=self.display,
                                      width=width,
                                      height=height,
                                      depth=depth,
                                      fps=fps
                        )
        
        self.compressors = []
        for i in range(comp_thre_num):
            compressor = FrameCompressor(raw_frame_queue=self.raw_frame_queue,
                                         comp_frame_queue=self.comp_frame_queue,
                                         quality=quality
                                        )
            self.compressors.append(compressor)
    
    # start capturing frames
    def init(self):
        self.capturer.start()
        for compressor in self.compressors:
            compressor.start()
        Logger.print_ok('Captured from Display :%d' % self.display)
    
    # terminate all the threads
    def terminate_all(self):
        self.capturer.terminate()
        self.raw_frame_queue.get()
        self.capturer.join()
        
        for compressor in self.compressors:
            compressor.terminate()
        
        for i in range(self.comp_queue.qsize()):
            self.comp_frame_queue.get()
        
        for compressor in self.compressors:
            compressor.join()
    
    # get the next compressed frame
    def get_next_frame(self):
        while True:
            frame_num, frame = self.comp_frame_queue.get()
            if frame_num == self.next_frame_num:
                self.next_frame_num += 1
                return (frame_num, frame)
            elif frame == None:
                self.next_frame_num += 1
            else:
                self.comp_frame_queue.put((frame_num, frame))

