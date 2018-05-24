# -*- coding: utf-8 -*-
## SAGE2_SS.py (SAGE2_SSの実行スクリプト)

import json
from os import path
from src.streaming import *

## Main
if __name__ == '__main__':
    print('')
    
    # 設定ファイルをパース
    conf_path = path.dirname(path.abspath(__file__)) + '/config.json'
    conf = json.load(open(conf_path, 'r'))
    
    # ストリーミングを開始
    streamer = FrameStreamer(conf)
    streamer.init()

