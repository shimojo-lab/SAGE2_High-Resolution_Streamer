# *-* encoding: utf-8 *-*
## compression_thread.py (フレーム圧縮用スレッド)

from threading import Thread
import cv2
from base64 import b64encode
from .utils import error_output

# 別スレッドでフレーム圧縮を行うクラス
class FrameCompresser(Thread):
    # コンストラクタ
    def __init__(self, np_frame_queue, comp_frame_queue, width, height, comp, quality):
        # パラメータを設定
        super(FrameCompresser, self).__init__()
        self.np_frame_queue = np_frame_queue      # 結合フレームキュー
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
            error_output('Frame compression failed')
            exit(1)
        return encode, comp_param
    
    # 結合フレームを圧縮するメソッド
    def compress_frame(self, np_frame):
        # フレームを圧縮
        result, comp_frame = cv2.imencode(self.encode, np_frame, self.comp_param)
        
        # base64に変換してキューへ (失敗したらNone)
        str_frame = b64encode(comp_frame).decode('utf-8') if result else None
        return str_frame
    
    # スレッドを終了するメソッド
    def terminate(self):
        self.active = False
    
    # フレーム圧縮を繰り返すメソッド
    def run(self):
        while self.active:
            frame_num, np_frame = self.np_frame_queue.get()
            comp_frame = self.compress_frame(np_frame)
            self.comp_frame_queue.put((frame_num, comp_frame))

