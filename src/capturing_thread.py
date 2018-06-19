# *-* encoding: utf-8 *-*
## capturing_thread.py (フレームキャプチャ用スレッド)

from threading import Thread
from subprocess import Popen, PIPE
import numpy as np
from .utils import error_output

# 別スレッドでフレームキャプチャを行うクラス
class FrameCapturer(Thread):
    # コンストラクタ
    def __init__(self, raw_frame_queue, loglevel, display, width, height, depth, framerate):
        # パラメータを設定
        super(FrameCapturer, self).__init__()
        self.width, self.height = width, height  # フレームの縦横の長さ
        self.frame_size = width * height * 3     # フレームのデータサイズ
        self.raw_frame_queue = raw_frame_queue   # 生フレームキュー
        self.frame_num = 0                       # 付与するフレーム番号
        self.active = True                       # スレッドの終了フラグ
        self.prev_frame = None                   # 前回取得したフレーム
        
        # フレーム録画を開始
        self.pipe = self.init_recording(loglevel, display, depth, framerate)
    
    # 録画を開始するメソッド
    def init_recording(self, loglevel, display, depth, framerate):
        # 録画用のコマンドを作成
        record_cmd = [
            'ffmpeg', '-loglevel', loglevel, '-f', 'x11grab',
            '-vcodec', 'rawvideo', '-an', '-s', '%dx%d' % (self.width, self.height),
            '-i', ':%d+0,0' % display, '-r', str(framerate),
            '-f', 'image2pipe', '-vcodec', 'rawvideo', '-pix_fmt', 'bgr%d' % depth, '-'
        ]
        
        # バックグラウンドで録画開始
        try:
            pipe = Popen(record_cmd, stdout=PIPE)
        except:
            error_output('Could not start capturing frame')
            exit(1)
        return pipe
    
    # フレームをNumpy配列として取得するメソッド
    def get_frame(self):
        # 前回取得したフレームと差が無ければやり直し
        while True:
            frame = self.pipe.stdout.read(self.frame_size)
            if frame != self.prev_frame:
                # 前回取得したフレームを更新
                self.prev_frame = frame
                
                # Numpy配列に変換
                raw_frame = np.fromstring(frame, dtype=np.uint8).reshape(self.height, self.width, 3)
                return raw_frame
    
    # スレッドを終了するメソッド
    def terminate(self):
        self.active = False
    
    # フレームキャプチャを繰り返すメソッド
    def run(self):
        while self.active:
            # 生フレームを取得
            raw_frame = self.get_frame()
            
            # フレーム番号を付与してキューへ
            frame_num = self.frame_num
            self.frame_num += 1
            self.raw_frame_queue.put((frame_num, raw_frame))

