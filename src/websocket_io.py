# *-* coding: utf-8 *-*
## websocket_io.py (WebSocket通信モジュール)

from tornado import websocket, ioloop
import json
from threading import Timer
import numpy as np
from .output import normal_output, ok_output, error_output, warning_output

# WebSocketの読み書きを行うクラス
class WebSocketIO():
    # コンストラクタ
    def __init__(self, ip, port, ws_tag, ws_id, interval):
        # パラメータを設定
        self.socket = None                       # 通信用のソケット
        self.open_callback = None                # ソケットを開いた時のコールバック
        self.msgs = {}                           # コールバックリスト
        self.alias_count = 1                     # エイリアスカウント
        self.ws_tag = ws_tag                     # ソケットタグ
        self.interval = interval                 # 送信失敗時の待ち時間
        self.addr = 'ws://%s:%d' % (ip, port)    # SAGE2サーバのアドレス
        self.remote_listeners = {ws_tag: ws_id}  # サーバのAPIリスト
        self.local_listeners = {ws_id: ws_tag}   # ローカルのAPIリスト
    
    # ソケットを開くメソッド
    def open(self, callback):
        # WebSocket通信用のソケットを開く
        websocket.websocket_connect(self.addr,
                                    callback=self.on_open_callback,
                                    on_message_callback=self.on_message_callback)
        
        # ソケットの準備が終わった時のコールバックを設定
        self.open_callback = callback
        
        # I/Oループを開始
        try:
            self.ioloop = ioloop.IOLoop.instance()
            self.ioloop.start()
        except KeyboardInterrupt:
            print('')
            normal_output('exit')
    
    # ソケットを閉じるメソッド
    def close(self):
        # ソケットを閉じてI/Oループを停止
        self.socket.close()
        self.ioloop.stop()
    
    # ソケットを開いた時のコールバック
    def on_open_callback(self, socket):
        # 開いたソケットを取得
        ok_output('Connected to %s' % self.addr)
        self.socket = socket.result()
        
        # コールバックを実行
        self.open_callback()
    
    # ソケットを閉じた時のコールバック
    def on_close_callback(self):
        # ソケットを閉じてI/Oループを停止
        normal_output('Connection closed')
        self.ioloop.stop()
    
    # 受信時のコールバック
    def on_message_callback(self, msg):
        # 受信メッセージをパース
        if msg == None:
            self.on_close_callback()
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
                    warning_output('No handler for massage')
            else:
                warning_output('Message format is invalid (not JSON)')
    
    # 受信時のコールバックを設定するメソッド
    def set_recv_callback(self, name, callback):
        alias = '%04x' % self.alias_count
        self.local_listeners[alias] = name
        self.msgs[name] = callback
        self.alias_count += 1
        self.emit(self.ws_tag, {'listener': name, 'alias': alias})
    
    # メッセージを送信するメソッド
    def emit(self, name, data, attempts=10):
        # メッセージ名の有無を確認
        if name==None or name=='':
            warning_output('No message name specified')
        
        # メッセージをソケットに書き込み (失敗したらやり直し)
        if name in self.remote_listeners:
            alias = self.remote_listeners[name]
            msg = json.dumps({'f': alias, 'd': data})
            self.socket.write_message(msg)
        else:
            if attempts >= 0:
                timer = Timer(self.interval, self.emit, [name, data, attempts-1])
                timer.start()
            else:
                warning_output('Not sending message, recipient has no listener (%s)' % name)

