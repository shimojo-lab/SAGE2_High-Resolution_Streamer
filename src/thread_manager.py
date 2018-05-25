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
        self.display = display          # ディスプレイ番号
        
        # キャプチャ用のコマンドを設定
        self.cmd = self.make_capture_command(method, width, height, depth, quality, compression)
        if self.cmd == None:
            error_output('Capture method is invalid')
            exit(1)
        
        # スレッドリストを初期化
        for i in range(self.min_threads):
            self.thread_list.append(FrameCapturer(self.queue, self.counter, self.cmd))
    
    # キャプチャ用のコマンドを生成するメソッド
    def make_capture_command(self, method, width, height, depth, quality, compression):
        cmd = None
        if method == 'ffmpeg':
            if compression == 'jpeg' or compression == 'jpg':
                compression = 'mjpeg'
            q = 100 - quality + 1
            cmd = [
                'ffmpeg',
                '-loglevel', 'quiet',
                '-f', 'x11grab',
                '-video_size', '%dx%d' % (width, height),
                '-i', ':%d.0+0,0' % self.display,
                '-f', 'image2pipe',
                '-vcodec', compression, '-vframes', '1',
                '-qmin', '1', '-qmax', '100', '-q', str(q),
                'pipe:'
            ]
        elif method == 'xwd':
            cmd = [
                'xwd',
                '-display', ':%d' % self.display,
                '-root', '|',
                'convert', '-',
                '-depth', str(depth),
                '-quality', str(quality),
                '%s:-' % compression
            ]
        elif method == 'import':
            cmd = [
                'import',
                '-display', ':%d' % self.display,
                '-w', 'root',
                '-depth', str(depth),
                '-quality', str(quality),
                '%s:-' % compression
            ]
        return cmd
    
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

