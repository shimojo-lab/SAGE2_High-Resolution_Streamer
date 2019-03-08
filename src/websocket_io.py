# *-* coding: utf-8 *-*

from tornado import websocket, ioloop
import json
from threading import Timer
from .logger import Logger

RESEND_NUM = 10

# A class for Websocket I/O
class WebSocketIO():
    def __init__(self, ip, port, ws_tag, ws_id, ws_timeout):
        self.socket = None                       # the socket
        self.open_callback = None                # the callback when opening a socket
        self.callbacks = {}                      # the list for the callback functions
        self.alias_count = 1                     # the alias count
        self.addr = 'ws://%s:%d' % (ip, port)    # the address of sage2 server
        self.ws_tag = ws_tag                     # the tag for adding a new listener
        self.remote_listeners = {ws_tag: ws_id}  # the list of listeners on the sage2 server
        self.local_listeners = {ws_id: ws_tag}   # the list of listeners on the sage2 client
        self.ws_timeout = ws_timeout             # the timeout time
    
    # open a new socket and start I/O loop
    def open(self, callback):
        websocket.websocket_connect(self.addr,
                                    callback=self.on_open,
                                    on_message_callback=self.on_message)
        self.open_callback = callback
        
        try:
            self.ioloop = ioloop.IOLoop.instance()
            self.ioloop.start()
        except KeyboardInterrupt:
            print('')
            Logger.print_info('Stopped streaming frames')
    
    # close a socket
    def close(self):
        self.socket.close()
        self.ioloop.stop()
    
    # the callback when opening a socket
    def on_open(self, socket):
        Logger.print_ok('Connected to %s' % self.addr)
        self.socket = socket.result()
        self.open_callback()
    
    # the callback when closing a socket
    def on_close(self):
        Logger.print_info('Closed websocket connection')
        self.ioloop.stop()
    
    # the callback when receiving a message
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
                        self.callbacks[f_name](json_msg['d'])
                else:
                    Logger.print_warn('No handler for massage')
            else:
                Logger.print_warn('Message format is invalid (not JSON)')
    
    # set a callback when receiving a message
    def set_recv_callback(self, name, callback):
        alias = '%04x' % self.alias_count
        self.local_listeners[alias] = name
        self.callbacks[name] = callback
        self.alias_count += 1
        self.emit(self.ws_tag, {'listener': name, 'alias': alias})
    
    # send a message
    def emit(self, name, data, attempts=RESEND_NUM):
        if name==None or name=='':
            Logger.print_warn('No message name is specified')
        
        if name in self.remote_listeners:
            alias = self.remote_listeners[name]
            msg = json.dumps({'f': alias, 'd': data})
            self.socket.write_message(msg)
        else:
            if attempts >= 0:
                timer = Timer(self.ws_timeout, self.emit, [name, data, attempts-1])
                timer.start()
            else:
                Logger.print_warn('Not sending message, recipient has no listener (%s)' % name)

