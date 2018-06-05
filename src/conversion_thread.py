# *-* encoding: utf-8 *-*
## conversion_thread.py (フレーム変換用スレッド)

from threading import Thread
import numpy as np
from .utils import error_output

# 別スレッドでフレームをnumpy配列に変換するクラス
class FrameConverter(Thread):
    # コンストラクタ
    def __init__(self, raw_frame_queue, np_frame_queue, width, height):
        # パラメータを設定
        super(FrameConverter, self).__init__()
        self.raw_frame_queue = raw_frame_queue   # 生フレームキュー
        self.np_frame_queue = np_frame_queue     # numpyフレームキュー
        self.width, self.height = width, height  # フレームサイズ
        self.active = True                       # スレッドの終了フラグ
        
    # フレームをnumpy配列に変換するメソッド
    def convert_frame_to_np(self, raw_frame):
        try:
            np_frame = np.fromstring(raw_frame, dtype=np.uint8).reshape(self.height, self.width, 3)
        except:
            error_output('Could not convert raw frame')
            exit(1)
        return np_frame
    
    # スレッドを終了するメソッド
    def terminate(self):
        self.active = False
    
    # numpy変換を繰り返すメソッド
    def run(self):
        while self.active:
            frame_num, raw_frame = self.raw_frame_queue.get()
            np_frame = self.convert_frame_to_np(raw_frame)
            self.np_frame_queue.put((frame_num, np_frame))

