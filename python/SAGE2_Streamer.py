# -*- coding: utf-8 -*-
## SAGE2_streamer.py
## (Main)

import json
from os import path
from src.stream_frames import *

## Main
if __name__ == '__main__':
    conf_path = path.dirname(path.abspath(__file__)) + '/config.json'
    conf = json.load(open(conf_path, 'r'))
    streamer = FrameStreamer(conf)
    streamer.init()

