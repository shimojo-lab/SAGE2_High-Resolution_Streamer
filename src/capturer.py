# *-* encoding: utf-8 *-*
## capturer.py (画面キャプチャ部)

from threading import Thread
from subprocess import Popen, PIPE
from base64 import b64encode

# 別スレッドでキャプチャを行うクラス
class FrameCapturer(Thread):
    # コンストラクタ (パラメータを設定)
    def __init__(self, queue, counter, conf):
        super(FrameCapturer, self).__init__()
        self.queue = queue              # フレーム用キュー
        self.counter = counter          # フレーム番号管理部
        self.active = True              # スレッド停止用のフラグ
        self.width = conf['width']      # フレームの横の長さ
        self.height = conf['height']    # フレームの縦の長さ
        self.display = conf['display']  # フレームのディスプレイ番号
        
        # スクリーンショット用コマンド
        self.cmd = 'ffmpeg -loglevel quiet -f x11grab '
        self.cmd += '-video_size %sx%s ' % (self.width, self.height)
        self.cmd += '-i :%s -vframes 1 -f image2pipe -' % self.display
    
    # フレームを取得するメソッド
    def get_frame(self):
        # 画面キャプチャを実行 (失敗時はやり直し)
        try:
            frame = Popen(self.cmd, shell=True, stdout=PIPE).communicate()[0]
        except:
            frame = self.get_frame()
        
        # base64に変換してキューへ
        frame = b64encode(frame).decode('utf-8')
        frame_num = self.counter.get_frame_num()
        return (frame_num, frame)
    
    # スレッドを終了するメソッド
    def terminate(self):
        self.active = False
    
    # キャプチャをし続けるメソッド
    def run(self):
        while self.active:
            frame = self.get_frame()
            self.queue.put(frame)

