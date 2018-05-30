# *-* encoding: utf-8 *-*
## concatenation_thread.py (フレーム結合用スレッド)

from threading import Thread
import numpy as np
from .utils import error_output

# 別スレッドでフレーム結合を行うクラス
class FrameConcatenater(Thread):
    # コンストラクタ
    def __init__(self, split_frame_queues, np_frame_queue, width, height):
        # パラメータを設定
        super(FrameConcatenater, self).__init__()
        self.split_frame_queues = split_frame_queues  # 分割フレームキュー
        self.np_frame_queue = np_frame_queue          # 結合フレームキュー
        self.width, self.height = width, height       # フレームサイズ
        self.active = True                            # スレッドの終了フラグ
        
    # 分割フレームを取得して結合するメソッド
    def concatenate_frame(self):        
        concatenated_frame = b''
        for queue in self.split_frame_queues:
            frame_num, split_frame = queue.get()
            concatenated_frame += split_frame
        return (frame_num, concatenated_frame)
    
    # 結合フレームをnumpy配列に変換するメソッド
    def convert_frame_to_np(self, concatenated_frame):
        try:
            np_frame = np.fromstring(concatenated_frame, dtype=np.uint8).reshape(self.height, self.width, 3)
        except:
            error_output('Could not concatenate split frames')
            exit(1)
        return np_frame
    
    # スレッドを終了するメソッド
    def terminate(self):
        self.active = False
    
    # フレーム結合を繰り返すメソッド
    def run(self):
        while self.active:
            frame_num, concatenated_frame = self.concatenate_frame()
            np_frame = self.convert_frame_to_np(concatenated_frame)
            self.np_frame_queue.put((frame_num, np_frame))

