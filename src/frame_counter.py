# *-* encoding: utf-8 *-*
## frame_counter.py (フレームカウンター)

from threading import Lock

## フレーム番号を管理するクラス
class FrameCounter(object):
    # コンストラクタ (初期化)
    def __init__(self):
        self.count = 0
        self.lock = Lock()
    
    # 次のフレーム番号を取得するメソッド
    def get_next_num(self):
        with self.lock:
            frame_num = self.count
            self.count += 1
        return frame_num

