# *-* coding: utf-8 *-*

from time import time
import sys
from base64 import b64decode
from .logger import Logger

## A class for frame streaming
class FrameStreamer():
    def __init__(self, ws_io, capturing_mgr, width, height):
        self.ws_io = ws_io                       # the Websocket I/O handler
        self.capturing_mgr = capturing_mgr       # the frame capturing manager
        self.app_id = None                       # the application ID
        self.title = 'SAGE2_Streamer'            # the application name
        self.color = '#cccc00'                   # the window color on the sage UI
        self.width, self.height = width, height  # the width and height of frames
        self.fps_interval = 1                    # the interval of printing the frame rate
        self.pre_send_time = time()              # the time in which the previous frame was sended
    
    # measure the frame rate
    def measure_fps(self):
        post_send_time = time()
        fps = 1.0 / (post_send_time-self.pre_send_time)
        self.pre_send_time = post_send_time
        return round(fps, 2)
    
    # notify the sage2 server of starting streaming
    def notify_start(self, data):
        self.app_id = data['UID'] + '|0' 
        self.ws_io.emit('requestToStartMediaStream', {})
        
        frame = self.capturing_mgr.get_next_frame()[1]
        self.ws_io.emit('startNewMediaStream', {
            'id': self.app_id,
            'title': self.title,
            'color': self.color,
            'width': self.width,
            'height': self.height,
            'src': frame,
            'type': 'image/jpg',
            'encoding': 'base64',
        })
        
        self.fps = self.measure_fps()
        Logger.print_notice('Started desktop streaming')
    
    # send a next compressed frame
    def send_next_frame(self, data):
        frame_num, frame = self.capturing_mgr.get_next_frame()
        self.ws_io.emit('updateMediaStreamFrame', {
            'id': self.app_id,
            'state': {
                'src': frame,
                'type': 'image/jpg',
                'encoding': 'base64',
            }
        })
        
        fps = self.measure_fps()
        self.fps_interval -= 1
        if self.fps_interval <= 0:
            sys.stdout.write('\r[SAGE2_Streamer]> Frame Rate: %sfps ' % fps)
            sys.stdout.flush()
            self.fps_interval = fps / 6.0
    
    # terminate streaming
    def terminate_streaming(self, data):
        self.capturing_mgr.terminate_all()
        self.ws_io.on_close()
    
    # the callback when opening a new socket
    def on_open(self):
        self.ws_io.set_recv_callback('initialize', self.notify_start)
        self.ws_io.set_recv_callback('requestNextFrame', self.send_next_frame)
        self.ws_io.set_recv_callback('stopMediaCapture', self.terminate_streaming)
        
        self.ws_io.emit('addClient', {
            'clientType': self.title,
            'requests': {
                'config': False,
                'version': False,
                'time': False,
                'console': False
            }
        })

