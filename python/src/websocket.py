# *-* coding: utf-8 *-*
## websocket.py
## (WebSocketでデータを送信するクラス)

from tornado import websocket, ioloop
from threading import Thread, Timer
import json
import numpy as np
from asyncio import set_event_loop, new_event_loop
from threading import Timer
import multiprocessing

WS_TAG, WS_ID = '#WSIO#addListener', '0000'
WS_CONSOLE = 'SAGE2_Streamer>'

class WebSocketIO:
    def __init__(self, conf):
        self.socket = None
        self.open_callback = None
        self.addr = 'ws://{}:{}'.format(conf['ip'], conf['port'])
        self.msgs = {}
        self.alias_count = 1
        self.remote_listeners = {WS_TAG: WS_ID}
        self.local_listeners = {WS_ID: WS_TAG}
        self.interval = conf['interval']
    
    def open(self, callback):
        websocket.websocket_connect(self.addr, callback=self.on_open, on_message_callback=self.on_message)
        self.open_callback = callback 
        try:
            self.ioloop = ioloop.IOLoop.instance()
            self.ioloop.start()
        except KeyboardInterrupt:
            print('{} exit'.format(WS_CONSOLE))

    def close(self):
        self.socket.close()
        self.ioloop.stop()
    
    def on_open(self, socket):
        print('{} Connect to {}'.format(WS_CONSOLE, self.addr))
        self.socket = socket.result()
        new_thread = Thread(target=self.open_callback)
        new_thread.start()
    
    def on_message(self, json_msg):
        if json_msg == None:
            self.on_close()
        else:
            if json_msg.startswith('{') and json_msg.endswith('}'):
                msg = json.loads(json_msg)
                if msg['f'] in self.local_listeners:
                    f_name = self.local_listeners[msg['f']]
                    if f_name == WS_TAG:
                        self.remote_listeners[msg['d']['listener']] = msg['d']['alias']
                    else:
                        self.msgs[f_name](msg['d'])
                else:
                    print('{} No handler for message.'.format(WS_CONSOLE))
            else:
                data = np.fromstring(json_msg, dtype=np.uint8, count=len(json_msg))
                func = data[:4].tostring()
                f_name = self.local_listerners[func]
                buf = data[4:]
                self.msgs[f_name](buf)
    
    def on_close(self):
        print('{} Socket closed.'.format(WS_CONSOLE))
        self.ioloop.stop()
    
    def on(self, name, callback):
        alias = '%04x' % self.alias_count
        self.local_listeners[alias] = name
        self.msgs[name] = callback
        self.alias_count += 1
        self.emit(WS_TAG, {'listener': name, 'alias': alias})
    
    def emit(self, name, data, attempts=10):
        if name==None or name=='':
            print('{} Error: No message name specified.'.format(WS_CONSOLE))
        
        if name in self.remote_listeners:
            set_event_loop(new_event_loop())
            alias = self.remote_listeners[name]
            if isinstance(data, np.ndarray):
                func_name = np.fromstring(alias, dtype=np.uint8, count=4)
                msg = np.concatenate([func_name, data])
                self.socket.write_message(msg.tostring(), binary=True)
            else:
                msg = {'f': alias, 'd': data}
                self.socket.write_message(json.dumps(msg))
        else:
            if attempts >= 0:
                timer = Timer(self.interval, self.emit, [name, data, attempts-1])
                timer.start()
            else:
                print('{} Warning: Not sending message, recipient has no listener. ({})'.format(WS_CONSOLE, name))

