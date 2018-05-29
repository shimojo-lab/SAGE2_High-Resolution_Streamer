# *-* encoding: utf-8 *-*
## capturing_thread.py (フレームキャプチャ用スレッド)

from threading import Thread
from subprocess import Popen, PIPE
from .utils import error_output

# 別スレッドでフレームキャプチャを行うクラス
class FrameCapturer(Thread):
    # コンストラクタ
    def __init__(self, raw_frame_queue, loglevel, display, width, height, depth, framerate):
        # パラメータを設定
        super(FrameCapturer, self).__init__()
        self.raw_frame_queue = raw_frame_queue  # 生フレームキュー
        self.frame_num = 0                      # 現在のフレーム番号
        self.active = True                      # スレッドの終了フラグ
        
        # フレーム録画を開始
        self.pipe = self.init_recording(loglevel, display, width, height, depth, framerate)
        self.frame_size = width * height * 3
    
    # フレーム録画を開始するメソッド
    def init_recording(self, loglevel, display, width, height, depth, framerate):
        # 録画用のコマンドを作成
        record_cmd = [
            'ffmpeg', '-loglevel', loglevel,
            '-f', 'x11grab', '-vcodec', 'rawvideo', '-s', '%dx%d' % (width, height), '-an',
            '-i', ':%d' % display, '-r', str(framerate),
            '-f', 'image2pipe', '-vcodec', 'rawvideo', '-pix_fmt', 'bgr%d' % depth, '-'
        ]
        
        # バックグラウンドで録画を開始
        try:
            pipe = Popen(record_cmd, stdout=PIPE)
        except:
            error_output('Could not start capturing frame')
            exit(1)
        return pipe
    
    # 生フレームを取得するメソッド
    def get_raw_frame(self):
        # フレーム1枚とフレーム番号を取得 (失敗したらNone)
        try:
            raw_frame = self.pipe.stdout.read(self.frame_size)
        except:
            return None
        
        # フレーム番号を付与して生フレームキューへ
        frame_num = self.frame_num
        self.frame_num += 1
        return (frame_num, raw_frame)
    
    # スレッドを終了するメソッド
    def terminate(self):
        self.active = False
    
    # フレームキャプチャを繰り返すメソッド
    def run(self):
        while self.active:
            raw_frame_set = self.get_raw_frame()
            if raw_frame_set != None:
                self.raw_frame_queue.put(raw_frame_set)

