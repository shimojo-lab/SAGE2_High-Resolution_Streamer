# *-* encoding: utf-8 *-*
## compression_thread.py (フレーム圧縮スレッド)

from threading import Thread
import numpy as np
import cv2
from base64 import b64encode

# 別スレッドでフレーム圧縮を行うクラス
class FrameCompresser(Thread):
    # コンストラクタ
    def __init__(self, raw_frame_queue, comp_frame_queue, width, height, comp, quality):
        # パラメータを設定
        super(FrameCompresser, self).__init__()
        self.raw_frame_queue = raw_frame_queue    # 生フレームキュー
        self.comp_frame_queue = comp_frame_queue  # 圧縮フレームキュー
        self.width, self.height = width, height   # フレームサイズ
        self.active = True                        # スレッドの終了フラグ
        
        # 圧縮パラメータを設定
        self.encode, self.comp_param = self.define_comp_param(comp, quality)
    
    # 圧縮パラメータを設定するメソッド
    def define_comp_param(self, comp, quality):
        if comp in ('jpeg', 'jpg', 'JPEG', 'JPG'):
            encode = '.jpg'
            comp_param = [int(cv2.IMWRITE_JPEG_QUALITY), quality]
        elif comp in ('png', 'PNG'):
            encode = '.png'
            comp_param = [int(cv2.IMWRITE_PNG_COMPRESSION), quality]
        else:
            print('Error')
            exit(1)
        return encode, comp_param
    
    # 生フレームをnumpy配列として取得するメソッド
    def get_frame_as_np(self):        
        # 生フレームを取得
        frame_num, raw_frame = self.raw_frame_queue.get()
        
        # numpy配列に変換
        np_frame = np.fromstring(raw_frame, dtype=np.uint8).reshape(self.height, self.width, 3)
        return (frame_num, np_frame)
    
    # フレームを取得するメソッド
    def compress_frame(self, np_frame_set):
        # フレームを圧縮
        frame_num = np_frame_set[0]
        result, comp_frame = cv2.imencode(self.encode, np_frame_set[1], self.comp_param)
        
        # base64に変換してキューへ
        str_frame = b64encode(comp_frame).decode('utf-8') if result else None
        return (frame_num, str_frame)
    
    # スレッドを終了するメソッド
    def terminate(self):
        self.active = False
    
    # フレーム圧縮を繰り返すメソッド
    def run(self):
        while self.active:
            np_frame_set = self.get_frame_as_np()
            comp_frame_set = self.compress_frame(np_frame_set)
            self.comp_frame_queue.put(comp_frame_set)

