# *-* encoding: utf-8 *-*
## capture_thread.py (画面キャプチャスレッド)

from threading import Thread
from subprocess import run, PIPE
from base64 import b64encode

# 別スレッドでキャプチャを行うクラス
class FrameCapturer(Thread):
    # コンストラクタ
    def __init__(self, conf):
        # パラメータを設定
        super(FrameCapturer, self).__init__()
        self.queue = conf['queue']      # フレーム用キュー
        self.counter = conf['counter']  # フレーム番号管理部
        self.width = conf['width']      # フレームの横の長さ
        self.height = conf['height']    # フレームの縦の長さ
        self.display = conf['display']  # フレームのディスプレイ番号
        self.cmd = conf['command']      # キャプチャ用のコマンド
        self.active = True              # スレッド停止用のフラグ
        
    # フレームを取得するメソッド
    def get_frame(self):
        # 画面キャプチャを実行 (失敗時はやり直し)
        try:
            bin_frame = run(self.cmd, stdout=PIPE).stdout
        except:
            bin_frame = self.get_frame()
        
        # base64に変換
        str_frame = b64encode(bin_frame).decode('utf-8')
        
        # フレーム番号を取得してまとめる
        frame_num = self.counter.get_next_num()
        return (frame_num, str_frame)
    
    # スレッドを終了するメソッド
    def terminate(self):
        self.active = False
    
    # キャプチャを繰り返すメソッド
    def run(self):
        while self.active:
            frame_set = self.get_frame()
            self.queue.put(frame_set)

