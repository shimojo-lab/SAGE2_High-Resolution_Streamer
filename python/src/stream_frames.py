# *-* encoding: utf-8 *-*
## stream_frames.py (ストリーム送信部)

from threading import Lock, active_count
from queue import PriorityQueue
from time import sleep
from .utils import *
from .capture_frames import *
from .io_websocket import *

MAX_CAPTURERS = 32
MIN_CAPTURERS = 2

## フレーム番号を管理するクラス
class FrameCounter(object):
    # コンストラクタ (初期化)
    def __init__(self):
        self.count = 0
        self.lock = Lock()
    
    # フレーム番号を取得するメソッド
    def get_frame_num(self):
        with self.lock:
            frame_num = self.count
            self.count += 1
            return frame_num

## フレームをストリーミングするクラス
class FrameStreamer:
    # コンストラクタ
    def __init__(self, conf):
        # パラメータを設定
        self.conf = conf                     # 設定ファイルの内容
        self.queue_max_size = conf['queue']  # キューの容量
        self.pre_queue_size = 0              # 前時刻でのキュー内フレーム数
        self.filetype = conf['filetype']     # フレームの圧縮形式
        self.title = conf['title']           # SAGE UI上でのウィンドウ名
        self.color = conf['color']           # SAGE UI上でのウィンドウカラー
        self.width = conf['width']           # フレームの横の長さ
        self.height = conf['height']         # フレームの縦の長さ
        
        # システムを初期化
        self.queue = PriorityQueue(maxsize=self.queue_max_size)  # フレーム用キュー
        self.counter = FrameCounter()                            # フレーム番号管理部
        self.capturers = [FrameCapturer(self.queue, self.counter, conf) for i in range(MIN_CAPTURERS)]  # キャプチャ用スレッドリスト
        self.wsio = WebSocketIO(conf)  # WebSocket通信部
    
    # デストラクタ
    def __del__(self):
        output_console('Connection closed')
        self.wsio.on_close()
    
    # キャプチャ用スレッドを新たに起動するメソッド
    def increase_capturer(self):
        # 起動してスレッドリストに追加
        if len(self.capturers) < MAX_CAPTURERS:
            capturer = FrameCapturer(self.queue, self.counter, self.conf)
            capturer.start()
            self.capturers.append(capturer)
    
    # キャプチャ用スレッドを終了するメソッド
    def decrease_capturer(self):
        # スレッドリストから1つを選んで停止
        if len(self.capturers) > MIN_CAPTURERS:
            self.capturers[-1].terminate()
            self.capturers.pop()
    
    # キャプチャ用スレッド数を調整するメソッド
    def optimize_capturers(self):
        # キュー内のフレーム数の変化を確認
        current_queue_size = self.queue.qsize()
        queue_diff = current_queue_size - self.pre_queue_size
        self.pre_queue_size = current_queue_size
        
        # 1以上減ならスレッド追加、2以上増ならスレッド除去
        if queue_diff<=-1 or self.queue.empty():
            self.increase_capturer()
        elif queue_diff >= 2:
            self.decrease_capturer()
    
    # ストリーミングを開始するメソッド
    def start_stream(self, data):
        # ストリーミング開始を通知
        self.app_id = data['UID'] + '|0'
        frame = self.queue.get()[1]
        request = {
            'id': self.app_id,
            'title': self.title,
            'color': self.color,
            'width': self.width,
            'height': self.height,
            'src': frame,
            'type': 'image/' + self.filetype,
            'encoding': 'base64'
        }
        self.wsio.emit('requestToStartMediaStream', {})
        self.wsio.emit('startNewMediaStream', request)
        
        # キュー内にフレームを確保
        output_console('Preparing for queue...')
        while not self.queue.full():
            sleep(1)
        output_console('Streaming started')
    
    # 次番のフレームを送信するメソッド
    def send_next_frame(self, data):
        # キャプチャ用スレッド数を調整
        self.optimize_capturers()
        
        # フレームを取得してSAGE2サーバへ送信
        frame = self.queue.get()[1]
        request = {
            'id': self.app_id,
            'state': {
                'src': frame,
                'type': 'image/' + self.filetype,
                'encoding': 'base64'
            }
        }
        self.wsio.emit('updateMediaStreamFrame', request)
    
    # ソケット作成時のコールバックメソッド
    def on_open(self):
        # ストリーミング開始を通知
        self.wsio.on('initialize', self.start_stream)
        
        # 次のフレームを送信
        self.wsio.on('requestNextFrame', self.send_next_frame)
        
        # 送信元の情報を通知
        request = {
            'clientType': self.title,
            'requests': {
                'config': False,
                'version': False,
                'time': False,
                'console': False
            }
        }
        self.wsio.emit('addClient', request)
    
    # ストリーミングを開始するメソッド
    def init(self):
        # キャプチャ用スレッドを起動
        for capturer in self.capturers:
            capturer.start()
        
        # ソケットを準備
        output_console('Preparing for WebSocket')
        self.wsio.open(self.on_open)

