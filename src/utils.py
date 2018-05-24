# -*- coding: utf-8 *-*
# utils.py (その他の機能)

from subprocess import run, PIPE

# コンソールにメッセージを表示する関数
def output_console(sentence):
    msg = '[SAGE2_SS]> %s' % sentence
    print(msg)

# VNCサーバを扱うクラス
class VNCServerHandler():
    # コンストラクタ
    def __init__(self, conf):
        self.flag = conf['flag']
        self.path = conf['path']
        self.display = conf['display']
        self.width = conf['width']
        self.height = conf['height']
        self.depth = conf['depth']
    
    # VNCサーバを停止するメソッド
    def halt_server(self):
        # 起動中のVNCサーバを停止
        halt_cmd = [
           self.path,
           '-kill',
           ':%d' % self.display
        ]
        try:
            msg = run(halt_cmd, stderr=PIPE)
        except:
            output_console('Error: Could not halt running VNC server')
            print(msg['stderr'])
            output_console('exit')
            exit(1)
    
    # VNCサーバを起動するメソッド
    def launch_server(self):
        launch_cmd = [
           self.path,
           '-geometry',
           '%dx%d' % (self.width, self.height),
           '-depth',
           str(self.depth)
        ]
        try:
            msg = run(launch_cmd, stderr=PIPE)
        except:
            output_console('Error: Could not launch new VNC server')
            print(msg['stderr'])
            output_console('exit')
            exit(1)
     
    # VNCサーバを再起動するメソッド
    def reset_vnc(self):
        if self.flag == 'True':
            output_console('Resetting VNC server...')
            self.halt_server()
            self.launch_server()

