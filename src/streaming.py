# *-* encoding: utf-8 *-*
## streaming.py (ストリーム送信部)

from .utils import normal_output, status_output

## フレームをストリーミング配信するクラス
class FrameStreamer():
    # コンストラクタ
    def __init__(self, ws_io, thread_mgr, width, height, compression, term):
        # パラメータを設定
        self.ws_io = ws_io                       # WebSocket入出力モジュール
        self.thread_mgr = thread_mgr             # スレッド管理モジュール
        self.app_id = None                       # SAGE2アプリケーションID
        self.title = 'SAGE2_Streamer'            # SAGE UI上でのウィンドウ名
        self.color = '#cccc00'                   # SAGE UI上でのウィンドウカラー
        self.width, self.height = width, height  # フレームのサイズ
        self.compression = compression           # フレームの圧縮形式
        self.encoding = 'base64'                 # フレームのエンコード形式
        self.optimize_term = term                # スレッド数の調整周期
    
    # ストリーミングの開始を通知するメソッド
    def init_streaming(self, data):
        self.app_id = data['UID'] + '|0' 
        self.ws_io.emit('requestToStartMediaStream', {})
        
        # SAGE2サーバにフレームの情報をを通知
        frame = self.thread_mgr.pop_frame()[1]
        self.ws_io.emit('startNewMediaStream', {
            'id': self.app_id,
            'title': self.title,
            'color': self.color,
            'width': self.width,
            'height': self.height,
            'src': frame,
            'type': 'image/%s' % self.compression,
            'encoding': self.encoding
        })
        normal_output('Start frame streaming')
    
    # 次番のフレームを送信するメソッド
    def send_next_frame(self, data):
        # フレームを取得してSAGE2サーバへ送信
        frame_num, frame = self.thread_mgr.pop_frame()
        self.ws_io.emit('updateMediaStreamFrame', {
            'id': self.app_id,
            'state': {
                'src': frame,
                'type': 'image/%s' % self.compression,
                'encoding': self.encoding,
                'frame_number': frame_num
            }
        })
        
        # 一定周期でスレッド数を調整
        if frame_num % self.optimize_term == 0:
            self.thread_mgr.optimize()
            """  スレッド数とキュー内フレーム数を表示 (デバッグ用)"""
            print(self.thread_mgr.check_thread_num())
            print(self.thread_mgr.check_queue_size())
    
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

