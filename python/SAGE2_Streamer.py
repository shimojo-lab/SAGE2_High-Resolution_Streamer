# -*- coding: utf-8 -*-
## SAGE2_streamer.py
## (Main)

import json
from os import path
from src.streaming import *

if __name__ == '__main__':
    conf_path = path.dirname(path.abspath(__file__)) + '/config.json'
    conf = json.load(open(conf_path, 'r'))
    streamer = SAGE2Streamer(conf)
    streamer.start()

