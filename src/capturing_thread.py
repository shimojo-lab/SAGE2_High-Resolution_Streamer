# *-* encoding: utf-8 *-*
## capturing_thread.py (フレームキャプチャ用スレッド)

from threading import Thread
from subprocess import Popen, PIPE
from .utils import error_output

# 別スレッドでフレームキャプチャを行うクラス
class FrameCapturer(Thread):
    # コンストラクタ
    def __init__(self, split_frame_queue, loglevel, display, region, width, height, depth, framerate):
        # パラメータを設定
        super(FrameCapturer, self).__init__()
        self.split_frame_queue = split_frame_queue  # 担当領域用のフレームキュー
        self.frame_num = 0                          # 付与するフレーム番号
        self.active = True                          # スレッドの終了フラグ
        
        # 担当領域の録画を開始
        self.pipe = self.init_recording(loglevel, display, region, width, height, depth, framerate)
        self.frame_size = width * height * 3
    
    # 録画を開始するメソッド
    def init_recording(self, loglevel, display, region, width, height, depth, framerate):
        # 録画用のコマンドを作成
        record_cmd = [
            'ffmpeg', '-loglevel', loglevel, '-f', 'x11grab',
            '-vcodec', 'rawvideo', '-an', '-s', '%dx%d' % (width, height),
            '-i', ':%d+0,%d' % (display, region*height), '-r', str(framerate),
            '-f', 'image2pipe', '-vcodec', 'rawvideo', '-pix_fmt', 'bgr%d' % depth, '-'
        ]
        
        # バックグラウンドで録画開始
        try:
            pipe = Popen(record_cmd, stdout=PIPE)
        except:
            error_output('Could not start capturing frame')
            exit(1)
        return pipe
    
    # フレームを取得するメソッド
    def get_split_frame(self):
        # 担当領域のフレームを取得 (失敗したらNone)
        try:
            raw_frame = self.pipe.stdout.read(self.frame_size)
        except:
            return None
        
        # フレーム番号を付与
        frame_num = self.frame_num
        self.frame_num += 1
        return (frame_num, raw_frame)
    
    # スレッドを終了するメソッド
    def terminate(self):
        self.active = False
    
    # フレームキャプチャを繰り返すメソッド
    def run(self):
        while self.active:
            frame_num, split_frame = self.get_split_frame()
            if split_frame != None:
                self.split_frame_queue.put((frame_num, split_frame))

