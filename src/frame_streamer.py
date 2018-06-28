# *-* encoding: utf-8 *-*
## frame_streamer.py (フレーム送信モジュール)

from time import time
import sys
from base64 import b64decode
from .output import normal_output

## フレームをストリーミング配信するクラス
class FrameStreamer():
    # コンストラクタ
    def __init__(self, ws_io, thread_mgr, width, height, comp):
        # パラメータを設定
        self.ws_io = ws_io                       # WebSocket入出力モジュール
        self.thread_mgr = thread_mgr             # スレッド管理モジュール
        self.app_id = None                       # SAGE2アプリケーションID
        self.title = 'SAGE2_Streamer'            # SAGE UI上でのウィンドウ名
        self.color = '#cccc00'                   # SAGE UI上でのウィンドウカラー
        self.width, self.height = width, height  # フレームのサイズ
        self.comp = comp                         # フレームの圧縮形式
        self.encoding = 'base64'                 # フレームのエンコード形式
        self.fps_interval = 1                    # フレームレートの表示間隔
        self.pre_update_time = time()            # 前回のフレーム送信時刻
    
    # 送信側での瞬間のフレームレートを計測するメソッド
    def measure_fps(self):
        post_update_time = time()
        fps = 1.0 / (post_update_time-self.pre_update_time)
        self.pre_update_time = post_update_time
        return round(fps, 2)
    
    # ストリーミングの開始を通知するメソッド
    def init_streaming(self, data):
        self.app_id = data['UID'] + '|0' 
        self.ws_io.emit('requestToStartMediaStream', {})
        
        # SAGE2サーバにフレームの情報を通知
        frame = self.thread_mgr.get_next_frame()[1]
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
        self.fps = self.measure_fps()
        normal_output('Start desktop streaming')
    
    # 次番のフレームを送信するメソッド
    def send_next_frame(self, data):
        # フレームを取得してSAGE2サーバへ送信
        frame_num, frame = self.thread_mgr.get_next_frame()
        self.ws_io.emit('updateMediaStreamFrame', {
            'id': self.app_id,
            'state': {
                'src': frame,
                'type': 'image/%s' % self.comp,
                'encoding': self.encoding,
            }
        })
        
        # 一定間隔でフレームレートを表示
        fps = self.measure_fps()
        self.fps_interval -= 1
        if self.fps_interval <= 0:
            sys.stdout.write('\r[SAGE2_Streamer]> Frame Rate: %sfps ' % fps)
            sys.stdout.flush()
            self.fps_interval = fps / 6.0
        
    # ストリーミングを停止するメソッド
    def stop_streaming(self, data):
        # 全スレッドを停止
        self.thread_mgr.terminate_all()
        
        # ソケットを閉じる
        self.ws_io.on_close_callback()
    
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

