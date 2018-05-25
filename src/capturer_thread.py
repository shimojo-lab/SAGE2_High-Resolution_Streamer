# *-* encoding: utf-8 *-*
## capture_thread.py (画面キャプチャスレッド)

from threading import Thread
from subprocess import run, PIPE
from base64 import b64encode

# 別スレッドでキャプチャを行うクラス
class FrameCapturer(Thread):
    # コンストラクタ
    def __init__(self, queue, counter, cmd):
        # パラメータを設定
        super(FrameCapturer, self).__init__()
        self.queue = queue      # フレーム用キュー
        self.counter = counter  # フレームカウンター
        self.cmd = cmd          # キャプチャ用のコマンド
        self.active = True      # スレッドの終了フラグ
    
    # フレームを取得するメソッド
    def get_frame(self):
        # 画面キャプチャを実行 (失敗時はNoneを返す)
        try:
            raw_frame = run(self.cmd, shell=True, stdout=PIPE).stdout
        except:
            return None
        
        # base64に変換
        str_frame = b64encode(raw_frame).decode('utf-8')
        
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
            if frame_set != None:
                self.queue.put(frame_set)
        return

