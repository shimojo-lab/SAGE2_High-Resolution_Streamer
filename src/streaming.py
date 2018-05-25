# *-* encoding: utf-8 *-*
## streaming.py (ストリーム送信部)

from .utils import *
from .thread_manager import ThreadManager
from .websocket_io import *

## フレームをストリーミング配信するクラス
class FrameStreamer:
    # コンストラクタ
    def __init__(self, conf):
        # パラメータを設定
        self.streamer_conf = {
           'app_id': None,
           'title': 'SAGE2_Streamer',
           'color': '#cccc00',
           'width': conf['width'],
           'height': conf['height'],
           'compression': conf['compression'],
           'encoding': 'base64'
        }
        
        # WebSocket制御部を初期化
        self.wsio = WebSocketIO({
           'ip': conf['server_ip'],
           'port': conf['server_port'],
           'ws_tag': '#WSIO#addListener',
           'ws_id': '0000',
           'interval': 0.001
        })
        
        # スレッド制御部を初期化
        self.thread_mgr = ThreadManager({
           'display': conf['display'],
           'width': conf['width'],
           'height': conf['height'],         
           'depth': conf['depth'],
           'method': conf['capture_method'],
           'compression': conf['compression'],
           'quality': conf['quality'],
           'queue_size': conf['queue_size'],
           'min_capturer_num': conf['min_capturer_num'],
           'max_capturer_num': conf['max_capturer_num']
        })
    
    # デストラクタ
    def __del__(self):
        # 全スレッドを停止
        self.thread_mgr.terminate_all()
        
        # ソケットを閉じて終了
        output_console('Connection closed')
        self.wsio.on_close()
    
    # ストリーミングを開始するメソッド
    def start_stream(self, data):
        # ストリーミング開始を通知
        self.streamer_conf['app_id'] = data['UID'] + '|0' 
        self.wsio.emit('requestToStartMediaStream', {})
        self.wsio.emit('startNewMediaStream', {
           'id': self.streamer_conf['app_id'],
           'title': self.streamer_conf['title'],
           'color': self.streamer_conf['color'],
           'width': self.streamer_conf['width'],
           'height': self.streamer_conf['height'],
           'src': self.thread_mgr.pop_frame(),
           'type': 'image/%s' % self.streamer_conf['compression'],
           'encoding': self.streamer_conf['encoding']
        })
        output_console('Streaming started')
    
    # 次番のフレームを送信するメソッド
    def send_next_frame(self, data):
        # キャプチャ用スレッド数を調整
        self.thread_mgr.optimize()
        
        # フレームを取得してSAGE2サーバへ送信
        self.wsio.emit('updateMediaStreamFrame', {
           'id': self.streamer_conf['app_id'],
           'state': {
               'src': self.thread_mgr.pop_frame(),
               'type': 'image/%s' % self.streamer_conf['compression'],
               'encoding': self.streamer_conf['encoding']
           }
        })
    
    # ソケットを開いた時のコールバック
    def on_open(self):
        # ストリーミング開始を通知
        self.wsio.on('initialize', self.start_stream)
        
        # 次のフレームを送信
        self.wsio.on('requestNextFrame', self.send_next_frame)
        
        # 送信元の情報を通知
        self.wsio.emit('addClient', {
           'clientType': self.streamer_conf['title'],
           'requests': {
              'config': False,
              'version': False,
              'time': False,
              'console': False
           }
        })
    
    # ストリーミングを開始するメソッド
    def init(self):
        # キャプチャ用スレッドを起動
        output_console('Preparing for screenshot...')
        self.thread_mgr.init()
        
        # ソケットを準備
        output_console('Preparing for WebSocket...')
        self.wsio.open(self.on_open)

