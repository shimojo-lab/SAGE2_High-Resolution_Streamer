# *-* encoding: utf-8 *-*
## thread_manager.py (キャプチャ用スレッド管理部)

from threading import Lock, active_count
from queue import PriorityQueue
from time import sleep
from .utils import *
from .capturer_thread import *

## フレーム番号を管理するクラス
class FrameCounter(object):
    # コンストラクタ (初期化)
    def __init__(self):
        self.count = 0
        self.lock = Lock()
    
    # 最新のフレーム番号を取得するメソッド
    def get_current_num(self):
        with self.lock:
            frame_num = self.count
        return frame_num
    
    # 次のフレーム番号を取得するメソッド
    def get_next_num(self):
        with self.lock:
            frame_num = self.count
            self.count += 1
        return frame_num

## キャプチャ用スレッドを管理するクラス
class ThreadManager:
    # コンストラクタ
    def __init__(self, conf):
        # パラメータを設定
        self.thread_list = []
        self.min_thread_num = conf['min_capturer_num']
        self.max_thread_num = conf['max_capturer_num']
        method = conf['method']
        width = conf['width']
        height = conf['height']
        depth = conf['depth']
        display = conf['display']
        compression = conf['compression']
        quality = conf['quality']
        
        # キューとフレーム番号管理部を初期化
        self.queue = PriorityQueue(maxsize=conf['queue_size'])
        self.pre_queue_size = 0 
        self.counter = FrameCounter()
        
        # キャプチャ用のコマンドを設定
        if method == 'ffmpeg':
            cmd = [
                'ffmpeg',
                '-loglevel', 'quiet',
                '-f', 'x11grab', '-an',
                '-video_size', '%dx%d' % (width, height),
                '-i', ':%d' % display,
                '-vcodec', 'rawvideo',
                '-preset', 'ultrafast',
                '-vframes', '1',
                '-f', 'image2pipe',
                '-vcodec', 'mjpeg',
                '-qscale:v', str(quality), '-'
            ]
        elif method == 'xwd':
            cmd = [
                'xwd',
                '-display', ':%d' % display,
                '-root', '|',
                'convert', '-',
                '-depth', str(depth),
                '-quality', str(quality),
                '%s:-' % compression
            ]
        elif method == 'import':
            cmd = [
                'import',
                '-display', ':%d' % display,
                '-w', 'root',
                '-depth', str(depth),
                '-quality', str(quality),
                '%s:-' % compression
            ]
        else:
            output_console('Error: Capture method is invalid')
            exit(1)
        
        # スレッドリストを初期化
        self.thread_conf = {
            'queue': self.queue,
            'counter': self.counter,
            'width': width,
            'height': height,
            'display': display,
            'command': cmd
        }
        for i in range(self.min_thread_num):
            self.thread_list.append(FrameCapturer(self.thread_conf))
    
    # キャプチャを開始させるメソッド
    def init(self):
        # スレッドを起動
        for thread in self.thread_list:
            thread.start()
        
        # キューにフレームが充填されるまで待機
        while not self.queue.full():
            sleep(1)
        output_console('Captured from Display :%d' % self.thread_conf['display'])
    
    # スレッド数を増やすメソッド
    def increase_thread(self):
        # 起動してスレッドリストに追加
        if len(self.thread_list) < self.max_thread_num:
            thread = FrameCapturer(self.thread_conf)
            thread.start()
            self.thread_list.append(thread)
    
    # スレッド数を減らすメソッド
    def decrease_thread(self):
        if len(self.thread_list) > self.min_thread_num:
            self.thread_list[-1].terminate()
            self.thread_list.pop()
    
    # スレッド数を調整するメソッド
    def optimize(self):
        # キュー内のフレーム数の変化を確認
        current_queue_size = self.queue.qsize()
        queue_diff = current_queue_size - self.pre_queue_size
        self.pre_queue_size = current_queue_size
        
        # 1以上減ならスレッド追加、2以上増ならスレッド除去
        if queue_diff<=-1 or self.queue.empty():
            self.increase_thread()
        elif queue_diff >= 2:
            self.decrease_thread()
    
    # 全スレッドを終了させるメソッド
    def terminate_all(self):
        for thread in self.thread_list:
            thread.terminate()
    
    # キューからフレームを取り出すメソッド
    def pop_frame(self):
        frame = self.queue.get()[1]
        return frame

