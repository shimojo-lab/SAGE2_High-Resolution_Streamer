# -*- coding: utf-8 -*-
## SAGE2_Streamer.py (SAGE2_Streamerの実行スクリプト)

import json
from os import path
from src.utils import nonbreak_output
from src.streaming import FrameStreamer
from src.thread_manager import ThreadManager
from src.websocket_io import WebSocketIO

## Main関数
def main():
    # 設定ファイルをパース
    conf_path = path.dirname(path.abspath(__file__)) + '/config.json'
    conf = json.load(open(conf_path, 'r'))
    
    # スレッド管理モジュールを初期化
    nonbreak_output('Preparing for screen capture')
    thread_mgr = ThreadManager(min_threads=conf['min_capturer_num'],
                               max_threads=conf['max_capturer_num'],
                               queue_size=conf['queue_size'],
                               method=conf['capture_method'],
                               display=conf['display'],
                               width=conf['width'],
                               height=conf['height'],
                               depth=conf['depth'],
                               compression=conf['compression'],
                               quality=conf['quality'])
    thread_mgr.init()
    
    # WebSocket入出力モジュールを初期化
    nonbreak_output('Preparing for server connection')
    ws_io = WebSocketIO(ip=conf['server_ip'],
                        port=conf['server_port'],
                        ws_tag='#WSIO#addListener',
                        ws_id='0000',
                        interval=0.001)
    
    # ストリーミングモジュールを初期化
    streamer = FrameStreamer(ws_io=ws_io,
                             thread_mgr=thread_mgr,
                             width=conf['width'],
                             height=conf['height'],
                             compression=conf['compression'],
                             term=conf['optimize_term'])   
    
    # ストリーミングを開始
    ws_io.open(streamer.on_open)

## Main
if __name__ == '__main__':
    main()

