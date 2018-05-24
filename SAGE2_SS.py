# -*- coding: utf-8 -*-
## SAGE2_SS.py (SAGE2_SSの実行スクリプト)

import json
from os import path
from src.utils import *
from src.streaming import *

## Main
if __name__ == '__main__':
    # 設定ファイルをパース
    print('')
    conf_path = path.dirname(path.abspath(__file__)) + '/config.json'
    conf = json.load(open(conf_path, 'r'))
    
    # VNCサーバを再起動 (設定時のみ)
    handler = VNCServerHandler({
        'flag': conf['vnc_reset'],
        'path': conf['vnc_path'],
        'display': conf['display'],
        'width': conf['width'],
        'height': conf['height'],
        'depth': conf['depth']
    })
    handler.reset_vnc()
    
    # ストリーミングを開始
    streamer = FrameStreamer(conf)
    streamer.init()

