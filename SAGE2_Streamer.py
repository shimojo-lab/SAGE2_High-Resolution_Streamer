# -*- coding: utf-8 -*-
## SAGE2_Streamer.py (SAGE2_Streamerの実行スクリプト)

import json
from os import path
from src.vnc_handler import VNCServerHandler
from src.streaming import FrameStreamer
from src.thread_manager import ThreadManager
from src.websocket_io import WebSocketIO

## Main
if __name__ == '__main__':
    # 設定ファイルをパース
    print('')
    conf_path = path.dirname(path.abspath(__file__)) + '/config.json'
    conf = json.load(open(conf_path, 'r'))
    
    # VNCサーバを再起動 (設定時のみ)
    vnc_handler = VNCServerHandler(flag=conf['vnc_reset'],
                                   path=conf['vnc_path'],
                                   display=conf['display'],
                                   width=conf['width'],
                                   height=conf['height'],
                                   depth=conf['depth'])
    vnc_handler.reset()
    
    # WebSocket入出力モジュールを起動
    ws_io = WebSocketIO(ip=conf['server_ip'],
                        port=conf['server_port'],
                        ws_tag='#WSIO#addListener',
                        ws_id='0000',
                        interval=0.001)
    
    # スレッド管理モジュールを起動
    thread_mgr = ThreadManager(min_threads=conf['min_capturer_num'],
                               max_threads=conf['max_capturer_num'],
                               queue_size=conf['queue_size'],
                               method=conf['capture_method'],
                               display=conf['display'],
                               width=conf['display'],
                               height=conf['height'],
                               depth=conf['depth'],
                               compression=conf['compression'],
                               quality=conf['quality'])
    
    # ストリーミングモジュールを起動
    streamer = FrameStreamer(ws_io=ws_io,
                             thread_mgr=thread_mgr,
                             width=conf['width'],
                             height=conf['height'],
                             compression=conf['compression'])
    
    # ストリーミングを開始
    streamer.init()

