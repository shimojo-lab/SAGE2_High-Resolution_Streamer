# *-* encoding: utf-8 *-*
## streaming.py (ストリーム送信部)

from .utils import normal_output, status_output

## フレームをストリーミング配信するクラス
class FrameStreamer():
    # コンストラクタ
    def __init__(self, ws_io, thread_mgr, width, height, compression):
        # パラメータを設定
        self.ws_io = ws_io                       # WebSocket入出力モジュール
        self.thread_mgr = thread_mgr             # スレッド管理モジュール
        self.app_id = None                       # SAGE2アプリケーションID
        self.title = 'SAGE2_Streamer'            # SAGE UI上でのウィンドウ名
        self.color = '#cccc00'                   # SAGE UI上でのウィンドウカラー
        self.width, self.height = width, height  # フレームのサイズ
        self.compression = compression           # フレームの圧縮形式
        self.encoding = 'base64'                 # フレームのエンコード形式
    
    # デストラクタ
    def __del__(self):
        # 全スレッドを停止
        nonbreak_output('Terminating all threads...')
        self.thread_mgr.terminate_all()
        status_output(True)
        
        # ソケットを閉じて終了
        normal_output('Connection closed')
        self.ws_io.on_close()
    
    # ストリーミングの開始を通知するメソッド
    def init_stream(self, data):
        self.app_id = data['UID'] + '|0' 
        self.ws_io.emit('requestToStartMediaStream', {})
        
        # SAGE2サーバにフレームの情報をを通知
        self.ws_io.emit('startNewMediaStream', {
            'id': self.app_id,
            'title': self.title,
            'color': self.color,
            'width': self.width,
            'height': self.height,
            'src': self.thread_mgr.pop_frame(),
            'type': 'image/%s' % self.compression,
            'encoding': self.encoding
        })
        normal_output('Start frame streaming')
    
    # 次番のフレームを送信するメソッド
    def send_next_frame(self, data):
        # キャプチャ用スレッド数を調整
        self.thread_mgr.optimize()
        
        # フレームを取得してSAGE2サーバへ送信
        next_frame = self.thread_mgr.pop_frame()
        self.ws_io.emit('updateMediaStreamFrame', {
           'id': self.app_id,
           'state': {
               'src': next_frame,
               'type': 'image/%s' % self.compression,
               'encoding': self.encoding
           }
        })
    
    # ソケットの準備が完了した時のコールバック
    def on_open(self):
        # ストリーミングの開始を通知
        self.ws_io.set_recv_callback('initialize', self.init_stream)
        
        # 次番のフレームを送信
        self.ws_io.set_recv_callback('requestNextFrame', self.send_next_frame)
        
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

