# *-* encoding: utf-8 *-*
## frame_streamer.py (フレーム送信モジュール)

from time import time
from .utils import normal_output

## フレームをストリーミング配信するクラス
class FrameStreamer():
    # コンストラクタ
    def __init__(self, ws_io, thread_mgr, width, height, comp, framerate):
        # パラメータを設定
        self.ws_io = ws_io                       # WebSocket入出力モジュール
        self.thread_mgr = thread_mgr             # スレッド管理モジュール
        self.app_id = None                       # SAGE2アプリケーションID
        self.title = 'SAGE2_Streamer'            # SAGE UI上でのウィンドウ名
        self.color = '#cccc00'                   # SAGE UI上でのウィンドウカラー
        self.width, self.height = width, height  # フレームのサイズ
        self.comp = comp                         # フレームの圧縮形式
        self.encoding = 'base64'                 # フレームのエンコード形式
        self.fps = framerate                     # フレームレート
        self.pre_update_time = time()            # 前回のフレーム送信時刻
    
    # 送信側での瞬間のフレームレートを計測するメソッド
    def measure_fps(self):
        post_update_time = time()
        fps = 1.0 / (post_update_time-self.pre_update_time)
        self.pre_update_time = post_update_time
        return fps
    
    # ストリーミングの開始を通知するメソッド
    def init_streaming(self, data):
        self.app_id = data['UID'] + '|0' 
        self.ws_io.emit('requestToStartMediaStream', {})
        
        # SAGE2サーバにフレームの情報を通知
        frame = self.thread_mgr.get_frame(self.fps)[1]
        self.ws_io.emit('startNewMediaStream', {
            'id': self.app_id,
            'title': self.title,
            'color': self.color,
            'width': self.width,
            'height': self.height,
            'src': frame,
            'type': 'image/%s' % self.comp,
            'encoding': self.encoding
        })
        
        # フレームレートを計測
        normal_output('Start frame streaming')
        self.fps = self.measure_fps()
    
    # 次番のフレームを送信するメソッド
    def send_next_frame(self, data):
        # フレームを取得してSAGE2サーバへ送信
        frame_num, frame = self.thread_mgr.get_frame(self.fps)
        self.ws_io.emit('updateMediaStreamFrame', {
            'id': self.app_id,
            'state': {
                'src': frame,
                'type': 'image/%s' % self.comp,
                'encoding': self.encoding,
                'frame_number': frame_num
            }
        })
        
        # フレームレートを計測
        self.fps = self.measure_fps()
        
    # ストリーミングを停止するメソッド
    def stop_streaming(self, data):
        # 全スレッドを停止
        self.thread_mgr.terminate_all()
        
        # ソケットを閉じる
        self.ws_io.on_close()
    
    # ソケットの準備が完了した時のコールバック
    def on_open(self):
        # ストリーミング開始時のイベントハンドラを作成
        self.ws_io.set_recv_callback('initialize', self.init_streaming)
        
        # 次番のフレームの要求時のイベントハンドラを作成
        self.ws_io.set_recv_callback('requestNextFrame', self.send_next_frame)
        
        # ストリーミング停止時のイベントハンドラを作成
        self.ws_io.set_recv_callback('stopMediaCapture', self.stop_streaming)
        
        # フレーム送信元の情報を通知
        self.ws_io.emit('addClient', {
            'clientType': self.title,
            'requests': {
                'config': False,
                'version': False,
                'time': False,
                'console': False
            }
        })

