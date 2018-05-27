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
        self.queue = queue         # フレーム用キュー
        self.counter = counter     # フレームカウンター
        self.capture_cmd = cmd[0]  # キャプチャ用のコマンド
        self.convert_cmd = cmd[1]  # 変換用のコマンド
        self.active = True         # スレッドの終了フラグ
    
    # フレームを取得するメソッド
    def get_frame(self):
        # キャプチャを実行 (失敗時はNoneを返す)
        try:
            raw_frame = run(self.capture_cmd, stdout=PIPE).stdout
        except:
            return None
        
        # フレーム番号を取得
        frame_num = self.counter.get_next_num()
            
        # フレームを圧縮 (失敗時はNoneを返す)
        try:
            converted_frame = run(self.convert_cmd, input=raw_frame, stdout=PIPE).stdout
        except:
            return None
        
        # base64に変換してキューへ
        str_frame = b64encode(converted_frame).decode('utf-8')
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

