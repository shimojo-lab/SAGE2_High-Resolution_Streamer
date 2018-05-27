# *-* encoding: utf-8 *-*
## thread_manager.py (キャプチャ用スレッド管理部)

from queue import PriorityQueue
from math import ceil
from random import randrange
from time import sleep
from threading import active_count
from .utils import normal_output, status_output, error_output
from .capturer_thread import FrameCapturer
from .frame_counter import FrameCounter

## キャプチャ用スレッドを管理するクラス
class ThreadManager:
    # コンストラクタ
    def __init__(self, min_threads, max_threads, queue_size, method, display, width, height, depth, compression, quality):
        # パラメータを設定
        self.thread_list = []           # スレッドリスト
        self.min_threads = min_threads  # 最小スレッド数
        self.max_threads = max_threads  # 最大スレッド数
        self.queue = PriorityQueue(queue_size)  # キュー
        self.queue_length = queue_size  # キューの長さ
        self.pre_queue_size = 0         # 全時刻でのキュー内フレーム数
        self.counter = FrameCounter()   # フレームカウンター
        self.display = display          # ディスプレイ番号
        
        # キャプチャ用のコマンドを設定
        self.cmd = self.make_capture_command(method, width, height, depth, quality, compression)
        if self.cmd == None:
            error_output('Capture method is invalid')
            exit(1)
        
        # スレッドリストを初期化
        default_threads = ceil((self.min_threads+self.max_threads)/2)
        for i in range(default_threads):
            self.thread_list.append(FrameCapturer(self.queue, self.counter, self.cmd))
    
    # キャプチャ用のコマンドを生成するメソッド
    def make_capture_command(self, method, width, height, depth, quality, compression):
        convert_cmd = [
            'convert', '-', '-thumbnail', '%dx%d' % (width, height),
            '-depth', str(depth), '-quality', str(quality), '%s:-' % compression
        ]
        if method == 'ffmpeg':
            capture_cmd = [
                'ffmpeg', '-loglevel', 'quiet', '-f', 'x11grab',
                '-video_size', '%dx%d' % (width, height),
                '-i', ':%d.0+0,0' % self.display, '-vcodec', 'rawvideo',
                '-f', 'image2pipe', '-vframes', '1', '-vcodec', 'png', 'pipe:-'
            ]
        elif method == 'xwd':
            capture_cmd = [
                'xwd', '-display', ':%d' % self.display, '-root'
            ]
        elif method == 'import':
            capture_cmd = [
                'import', '-display', ':%d.0' % self.display,
                '-w', 'root', '-thumbnail', '%dx%d' % (width, height),
                '-depth', str(depth), '-quality', str(quality),
                '%s:-' % compression
            ]
        return (capture_cmd, convert_cmd)
    
    # キャプチャを開始させるメソッド
    def init(self):
        # スレッドを起動
        for thread in self.thread_list:
            thread.start()
        
        # キューにフレームが充填されるまで待機
        while not self.queue.full():
            sleep(1)
        status_output(True)
        normal_output('Captured from Display :%d' % self.display)
    
    # スレッド数を増やすメソッド
    def increase_thread(self):
        # 起動してスレッドリストに追加
        if len(self.thread_list) < self.max_threads:
            thread = FrameCapturer(self.queue, self.counter, self.cmd)
            thread.start()
            self.thread_list.append(thread)
    
    # スレッド数を減らすメソッド
    def decrease_thread(self):
        if len(self.thread_list) > self.min_threads:
            del_id = randrange(len(self.thread_list))
            self.thread_list[del_id].terminate()
            self.thread_list.pop(del_id)
    
    # スレッド数を調整するメソッド
    def optimize(self):
        # キュー内のフレーム数の変化を確認
        current_queue_size = self.queue.qsize()
        queue_diff = current_queue_size - self.pre_queue_size
        self.pre_queue_size = current_queue_size
        
        # 1以上減ならスレッド追加、2以上増ならスレッド除去
        if queue_diff<=-1 or self.queue.empty():
            self.increase_thread()
        elif queue_diff>=2 and current_queue_size>self.queue_length/2:
            self.decrease_thread()
    
    # 全スレッドを終了させるメソッド
    def terminate_all(self):
        for thread in self.thread_list:
            thread.terminate()
       
    # キューからフレームを取り出すメソッド
    def pop_frame(self):
        frame_num, frame = self.queue.get()
        return frame_num, frame
    
    # 起動中のスレッド数を取得するメソッド
    def check_thread_num(self):
        list_thread_num = len(self.thread_list)
        real_thread_num  = active_count()
        return list_thread_num, real_thread_num
    
    # キュー内のフレーム数を取得するメソッド
    def check_queue_size(self):
        queue_size = self.queue.qsize()
        return queue_size

