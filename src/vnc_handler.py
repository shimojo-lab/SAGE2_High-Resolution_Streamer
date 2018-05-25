# -*- coding: utf-8 *-*
# vnc_handler.py (VNCサーバ管理モジュール)

from subprocess import run, PIPE
from .utils import status_output, error_output

# VNCサーバを扱うクラス
class VNCServerHandler():
    # コンストラクタ
    def __init__(self, flag, path, display, width, height, depth):
        # パラメータを設定
        self.flag = flag                         # 再起動のフラグ
        self.path = path                         # vncserverのパス
        self.display = display                   # 起動するディスプレイ
        self.width, self.height = width, height  # フレームのサイズ
        self.depth = depth                       # フレームの色深度
    
    # VNCサーバを停止するメソッド
    def halt_server(self):
        # 起動中のVNCサーバを停止
        halt_cmd = [
            self.path,
            '-kill', ':%d' % self.display
        ]
        try:
            msg = run(halt_cmd, stderr=PIPE)
        except:
            status_output(False)
            error_output('Could not halt running VNC server')
            print(msg.stderr)
            normal_output('exit')
            exit(1)
    
    # VNCサーバを起動するメソッド
    def launch_server(self):
        launch_cmd = [
            self.path,
            '-geometry', '%dx%d' % (self.width, self.height),
            '-depth', str(self.depth),
            ':%s' % self.display
        ]
        try:
            msg = run(launch_cmd, stderr=PIPE)
        except:
            status_output(False)
            error_output('Could not launch new VNC server')
            print(msg.stderr)
            normal_output('exit')
            exit(1)
        status_output(True)
     
    # VNCサーバを再起動するメソッド
    def reset(self):
        if self.flag == 'True':
            self.halt_server()
            self.launch_server()

