# *-* encoding: utf-8 *-*
## capturer_manager.py (キャプチャ用スレッド管理部)

from threading import Lock, active_count
from queue import PriorityQueue
from time import sleep
from .capturer import *

## フレーム番号を管理するクラス
class FrameCounter(object):
    # コンストラクタ (初期化)
    def __init__(self):
        self.count = 0
        self.lock = Lock()
    
    # フレーム番号を取得するメソッド
    def get_frame_num(self):
        with self.lock:
            frame_num = self.count
            self.count += 1
            return frame_num

## キャプチャ用スレッドを管理するクラス
class CapturerManager:
    # コンストラクタ
    def __init__(self, conf):
        # パラメータを設定
        self.conf = conf
        self.min_capturer_num = conf['min_capturer_num']
        self.max_capturer_num = conf['max_capturer_num']
        self.counter = FrameCounter()
        self.queue = PriorityQueue(maxsize=conf['queue_size'])
        self.pre_queue_size = 0
        
        # スレッドリストを初期化
        self.capturer_list = []
        for i in range(self.min_capturer_num):
            self.capturer_list.append(FrameCapturer(self.queue, self.counter, self.conf))
    
    # キャプチャを開始させるメソッド
    def init(self):
        # スレッドを起動
        for capturer in self.capturer_list:
            capturer.start()
        
        # キューにフレームが充填されるまで待機
        while not self.queue.full():
            sleep(1)
    
    # スレッド数を増やすメソッド
    def increase_capturer(self):
        # 起動してスレッドリストに追加
        if len(self.capturer_list) < self.max_capturer_num:
            capturer = FrameCapturer(self.queue, self.counter, self.conf)
            capturer.start()
            self.capturer_list.append(capturer)
    
    # スレッド数を減らすメソッド
    def decrease_capturer(self):
        if len(self.capturer_list) > self.min_capturer_num:
            self.capturer_list[-1].terminate()
            self.capturer_list.pop()
    
    # スレッド数を調整するメソッド
    def optimize(self):
        # キュー内のフレーム数の変化を確認
        current_queue_size = self.queue.qsize()
        queue_diff = current_queue_size - self.pre_queue_size
        self.pre_queue_size = current_queue_size
        
        # 1以上減ならスレッド追加、2以上増ならスレッド除去
        if queue_diff<=-1 or self.queue.empty():
            self.increase_capturer()
        elif queue_diff >= 2:
            self.decrease_capturer()
    
    # キューからフレームを取り出すメソッド
    def pop_frame(self):
        frame = self.queue.get()[1]
        return frame

