# -*- coding: utf-8 -*-
## SAGE2_streamer.py
## (スクリーンショットをSAGE2サーバへ送信)

import json
from src.streaming import *

if __name__ == '__main__':
    conf = json.load(open('./config.json', 'r'))
    streamer = SAGE2Streamer(conf)
    streamer.start()

