# *-* encoding: utf-8 *-*
## compression_thread.py (フレーム圧縮スレッド)

from threading import Thread
import numpy as np
from PIL import Image
from io import BytesIO
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
        self.comp = comp                          # フレームの圧縮形式
        self.quality = quality                    # フレームの圧縮品質
        self.active = True                        # スレッドの終了フラグ
    
    # 生フレームをnumpy配列として取得するメソッド
    def get_frame_as_np(self):        
        # 生フレームを取得
        frame_num, raw_frame = self.raw_frame_queue.get()
        
        # numpy配列に変換
        np_frame = np.fromstring(raw_frame, dtype=np.uint8).reshape(self.height, self.width, 3)
        return (frame_num, np_frame)
    
    # フレームを取得するメソッド
    def compress_frame(self, np_frame_set):
        # PILに画像を読み込み
        frame_num = np_frame_set[0]
        pil_frame = Image.fromarray(np_frame_set[1])
        
        # フレームを圧縮
        comp_frame_buf = BytesIO()
        pil_frame.save(comp_frame_buf, format=self.comp, quality=self.quality, optimize=True)
        comp_frame = comp_frame_buf.getvalue()
        
        # base64に変換してキューへ
        str_frame = b64encode(comp_frame).decode('utf-8')
        print(frame_num)
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

