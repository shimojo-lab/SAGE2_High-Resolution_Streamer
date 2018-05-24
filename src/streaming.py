# *-* encoding: utf-8 *-*
## streaming.py (ストリーム送信部)

from .utils import *
from .capturer_manager import *
from .websocket_io import *

## フレームをストリーミング配信するクラス
class FrameStreamer:
    # コンストラクタ
    def __init__(self, conf):
        # パラメータを設定
        self.conf = conf['client']
        
        # システムを初期化
        self.capturer_mgr = CapturerManager(conf["client"])  # キャプチャ用スレッド管理部
        self.wsio = WebSocketIO(conf['server'])          # WebSocket通信部
    
    # デストラクタ
    def __del__(self):
        # ソケットを閉じて終了
        output_console('Connection closed')
        self.wsio.on_close()
    
    # ストリーミングを開始するメソッド
    def start_stream(self, data):
        # ストリーミング開始を通知
        self.app_id = data['UID'] + '|0'
        frame = self.capturer_mgr.pop_frame()
        request = {
            'id': self.app_id,
            'title': self.conf['title'],
            'color': self.conf['color'],
            'width': self.conf['width'],
            'height': self.conf['height'],
            'src': frame,
            'type': 'image/%s' % self.conf['compression'],
            'encoding': 'base64'
        }
        self.wsio.emit('requestToStartMediaStream', {})
        self.wsio.emit('startNewMediaStream', request)
        output_console('Streaming started')
    
    # 次番のフレームを送信するメソッド
    def send_next_frame(self, data):
        # キャプチャ用スレッド数を調整
        self.capturer_mgr.optimize()
        
        # フレームを取得してSAGE2サーバへ送信
        frame = self.capturer_mgr.pop_frame()
        request = {
            'id': self.app_id,
            'state': {
                'src': frame,
                'type': 'image/%s' % self.conf['compression'],
                'encoding': 'base64'
            }
        }
        self.wsio.emit('updateMediaStreamFrame', request)
    
    # ソケットを開いた時のコールバック
    def on_open(self):
        # ストリーミング開始を通知
        self.wsio.on('initialize', self.start_stream)
        
        # 次のフレームを送信
        self.wsio.on('requestNextFrame', self.send_next_frame)
        
        # 送信元の情報を通知
        request = {
            'clientType': self.conf['title'],
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
        output_console('Preparing for screenshot...')
        self.capturer_mgr.init()
        
        # ソケットを準備
        output_console('Preparing for WebSocket...')
        self.wsio.open(self.on_open)

