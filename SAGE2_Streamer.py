# -*- coding: utf-8 -*-

import json
from os import path
from src.logger import Logger
from src.frame_streamer import FrameStreamer
from src.capturing_manager import CapturingManager
from src.websocket_io import WebSocketIO

WS_TAG = '#WSIO#addListener'
WS_ID = '0000'
WS_TIMEOUT = 0.001

## the main function
def main():
    conf_path = path.dirname(path.abspath(__file__)) + '/config.json'
    conf = json.load(open(conf_path, 'r'))
    
    Logger.print_info('Preparing for screen capture...')
    capturing_mgr = CapturingManager(display_num=conf['vnc']['number'],
                                     width=conf['vnc']['width'],
                                     height=conf['vnc']['height'],
                                     depth=conf['vnc']['depth'],
                                     loglevel=conf['ffmpeg']['loglevel'],
                                     fps=conf['ffmpeg']['record_fps'],
                                     comp_thre_num=conf['compression']['thread_num'],
                                     raw_queue_size=conf['compression']['raw_frame_queue'],
                                     comp_queue_size=conf['compression']['comp_frame_queue'],
                                     quality=conf['compression']['quality']
                    )
    capturing_mgr.init()
    
    Logger.print_info('Preparing for server connection...')
    ws_io = WebSocketIO(ip=conf['server']['ip'],
                        port=conf['server']['port'],
                        ws_tag=WS_TAG,
                        ws_id=WS_ID,
                        ws_timeout=WS_TIMEOUT
                       )
    
    streamer = FrameStreamer(ws_io=ws_io,
                             capturing_mgr=capturing_mgr,
                             width=conf['vnc']['width'],
                             height=conf['vnc']['height']
                            )
    ws_io.open(streamer.on_open)

if __name__ == '__main__':
    main()

