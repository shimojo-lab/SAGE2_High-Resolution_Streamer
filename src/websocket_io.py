# *-* coding: utf-8 *-*
## websocket_io.py (WebSocket通信部)

from tornado import websocket, ioloop
import json
from threading import Timer
from .utils import *

# WebSocketの読み書きを行うクラス
class WebSocketIO():
    # コンストラクタ
    def __init__(self, conf):
        # パラメータを設定
        self.socket = None         # 通信用のソケット
        self.open_callback = None  # ソケットを開いた時のコールバック
        self.msgs = {}             # 
        self.alias_count = 1       # 
        self.ws_tag = conf['ws_tag']                             # 
        self.interval = conf['interval']                         # 送信失敗時の待ち時間
        self.addr = 'ws://%s:%d' % (conf['ip'], conf['port'])    # SAGE2サーバのアドレス
        self.remote_listeners = {conf['ws_tag']: conf['ws_id']}  # 
        self.local_listeners = {conf['ws_id']: conf['ws_tag']}   # 
    
    # ソケットを開くメソッド
    def open(self, callback):
        websocket.websocket_connect(self.addr, callback=self.on_open, on_message_callback=self.on_message)
        self.open_callback = callback
        try:
            self.ioloop = ioloop.IOLoop.instance()
            self.ioloop.start()
        except KeyboardInterrupt:
            output_console('exit')
    
    # ソケットを閉じるメソッド
    def close(self):
        self.socket.close()
        self.ioloop.stop()
    
    # ソケットを開いた時のコールバック
    def on_open(self, socket):
        output_console('Connected to %s' % self.addr)
        self.socket = socket.result()
        self.open_callback()
    
    # ソケットを閉じた時のコールバック
    def on_close(self):
        output_console('Socket closed')
        self.ioloop.stop()
    
    # 受信時のコールバック
    def on_message(self, msg):
        if msg == None:
            self.on_close()
        else:
            if msg.startswith('{') and msg.endswith('}'):
                json_msg = json.loads(msg)
                if json_msg['f'] in self.local_listeners:
                    f_name = self.local_listeners[json_msg['f']]
                    if f_name == self.ws_tag:
                        self.remote_listeners[json_msg['d']['listener']] = json_msg['d']['alias']
                    else:
                        self.msgs[f_name](json_msg['d'])
                else:
                    output_console('No handler for massage')
            else:
                output_console('Message format is invalid (not JSON)')
    
    # 
    def on(self, name, callback):
        alias = '%04x' % self.alias_count
        self.local_listeners[alias] = name
        self.msgs[name] = callback
        self.alias_count += 1
        self.emit(self.ws_tag, {'listener': name, 'alias': alias})
    
    # データを送信するメソッド
    def emit(self, name, data, attempts=10):
        # メッセージ名の有無を確認
        if name==None or name=='':
            output_console('Error: No message name specified')
        
        # データをソケットに書き込み (失敗したらやり直し)
        if name in self.remote_listeners:
            alias = self.remote_listeners[name]
            msg = {'f': alias, 'd': data}
            self.socket.write_message(json.dumps(msg))
        else:
            if attempts >= 0:
                timer = Timer(self.interval, self.emit, [name, data, attempts-1])
                timer.start()
            else:
                output_console('Warning: Not sending message, recipient has no listener (%s)' % name)

