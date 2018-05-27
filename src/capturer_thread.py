# *-* encoding: utf-8 *-*
## capture_thread.py (画面キャプチャスレッド)

from threading import Thread
from subprocess import run, PIPE
from PIL import Image
from io import BytesIO
from base64 import b64encode

# 別スレッドでキャプチャを行うクラス
class FrameCapturer(Thread):
    # コンストラクタ
    def __init__(self, queue, counter, cmd, compression, quality):
        # パラメータを設定
        super(FrameCapturer, self).__init__()
        self.queue = queue              # フレームキュー
        self.counter = counter          # フレームカウンター
        self.capture_cmd = cmd          # キャプチャコマンド
        self.compression = compression  # 圧縮形式
        self.quality = quality          # 圧縮品質
        self.active = True              # スレッドの終了フラグ
    
    # フレームを取得するメソッド
    def get_frame(self):
        # フレーム番号を取得
        frame_num = self.counter.get_next_num()
        
        # キャプチャを実行 (失敗時はNoneを返す)
        try:
            raw_frame = run(self.capture_cmd, stdout=PIPE, stderr=PIPE).stdout
            raw_frame_buf = BytesIO(raw_frame)
        except:
            return None
            
        # フレームを圧縮 (失敗時はNoneを返す)
        try:
            pil_frame_buf = BytesIO()
            pil_frame = Image.open(raw_frame_buf)
            pil_frame.save(pil_frame_buf, format=self.compression, quality=self.quality, optimize=True)
            compressed_frame = pil_frame_buf.getvalue()
        except:
            return None
        
        # base64に変換してキューへ
        str_frame = b64encode(compressed_frame).decode('utf-8')
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

