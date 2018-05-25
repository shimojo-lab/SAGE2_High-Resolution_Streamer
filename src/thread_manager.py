# *-* encoding: utf-8 *-*
## thread_manager.py (キャプチャ用スレッド管理部)

from queue import PriorityQueue
from time import sleep
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
        self.queue = PriorityQueue(maxsize=queue_size)  # キュー
        self.pre_queue_size = 0         # 全時刻でのキュー内フレーム数
        self.counter = FrameCounter()   # フレームカウンター
        
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
            error_output('Capture method is invalid')
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
        for i in range(self.min_threads):
            self.thread_list.append(FrameCapturer(self.thread_conf))
    
    # キャプチャを開始させるメソッド
    def init(self):
        # スレッドを起動
        for thread in self.thread_list:
            thread.start()
        
        # キューにフレームが充填されるまで待機
        while not self.queue.full():
            sleep(1)
        status_output(True)
        normal_output('Captured from Display :%d' % self.thread_conf['display'])
    
    # スレッド数を増やすメソッド
    def increase_thread(self):
        # 起動してスレッドリストに追加
        if len(self.thread_list) < self.max_threads:
            thread = FrameCapturer(self.thread_conf)
            thread.start()
            self.thread_list.append(thread)
    
    # スレッド数を減らすメソッド
    def decrease_thread(self):
        if len(self.thread_list) > self.min_threads:
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

