# *-* encoding: utf-8 *-*
## thread_manager.py (キャプチャ用スレッド管理部)

from queue import PriorityQueue
from random import randrange
from time import sleep
from threading import active_count
from .utils import normal_output, status_output, error_output
from .capturer_thread import FrameCapturer
from .frame_counter import FrameCounter

## キャプチャ用スレッドを管理するクラス
class ThreadManager:
    # コンストラクタ
    def __init__(self, min_threads, max_threads, queue_size, queue_num, method, display, width, height, depth, compression, quality):
        # パラメータを設定
        self.thread_list = []           # スレッドリスト
        self.min_threads = min_threads  # 最小スレッド数
        self.max_threads = max_threads  # 最大スレッド数
        self.queue_list = []            # フレームキューリスト
        self.queue_size = queue_size    # フレームキューの長さ
        self.queue_num = queue_num      # フレームキューの数
        self.queue_pointer = 0          # フレームキューポインタ
        self.pre_queue_size = 0         # 前段階でのキュー内フレーム数
        self.skipped_frame = [[], []]   # 保留したフレームのリスト
        self.counter = FrameCounter()   # フレームカウンター
        self.next_frame_num = 0         # 次番のフレーム番号
        self.display = display          # フレームのディスプレイ番号
        self.compression = compression  # フレームの圧縮形式
        self.quality = quality          # フレームの圧縮品質
        
        # キャプチャ用コマンドを設定
        self.cmd = self.make_capture_command(method, width, height, depth)
        if self.cmd == None:
            error_output('Capture method is invalid')
            exit(1)
        
        # フレームキューリストを初期化
        for i in range(self.queue_num):
            queue = PriorityQueue(self.queue_size)
            self.queue_list.append(queue)
        
        # スレッドリストを初期化
        default_threads = int((self.min_threads+self.max_threads)/2)
        for i in range(default_threads):
            queue = self.queue_list[self.queue_pointer]
            self.thread_list.append(FrameCapturer(queue, self.counter, self.cmd, self.compression, self.quality))
            self.move_queue_pointer()
    
    # キャプチャ用のコマンドを生成するメソッド
    def make_capture_command(self, method, width, height, depth):
        if method == 'ffmpeg':
            capture_cmd = [
                'ffmpeg', '-loglevel', 'quiet', '-f', 'x11grab',
                '-ss', '1', '-video_size', '%dx%d' % (width, height),
                '-i', ':%d+0,0' % self.display, '-vcodec', 'rawvideo',
                '-f', 'image2pipe', '-vframes', '1', '-vcodec', 'png', 'pipe:-'
            ]
        elif method == 'xwd':
            capture_cmd = [
                'xwd', '-display', ':%d' % self.display, '-root'
            ]
        elif method == 'import':
            capture_cmd = [
                'import', '-display', ':%d' % self.display,
                '-w', 'root', '-thumbnail', '%dx%d' % (width, height),
                '-depth', str(self.depth), '-quality', str(self.quality),
                '%s:-' % self.compression
            ]
        return capture_cmd
    
    # フレームキューポインタを1つずらすメソッド
    def move_queue_pointer(self):
        self.queue_pointer += 1
        self.queue_pointer %= self.queue_num
    
    # キャプチャを開始させるメソッド
    def init(self):
        # スレッドを起動
        for thread in self.thread_list:
            thread.start()
        
        # フレームキューが充填されるまで待機
        while not self.queue_list[0].full():
            sleep(1)
        status_output(True)
        normal_output('Captured from Display :%d' % self.display)
    
    # スレッド数を増やすメソッド
    def increase_thread(self):
        # 起動してスレッドリストに追加
        if len(self.thread_list) < self.max_threads:
            thread = FrameCapturer(self.queue, self.counter, self.cmd, self.compression, self.quality)
            thread.start()
            self.thread_list.append(thread)
            self.move_queue_pointer()
    
    # スレッド数を減らすメソッド
    def decrease_thread(self):
        if len(self.thread_list) > self.min_threads:
            del_id = randrange(len(self.thread_list))
            self.thread_list[del_id].terminate()
            self.thread_list.pop(del_id)
    
    # スレッド数を調整するメソッド
    """def optimize(self):
        # キュー内のフレーム数の変化を確認
        current_queue_size = self.queue.qsize()
        queue_diff = current_queue_size - self.pre_queue_size
        self.pre_queue_size = current_queue_size
        
        # 2以上減ならスレッド追加、1以上増ならスレッド除去
        if queue_diff<=-2 or self.queue.empty():
            self.increase_thread()
        elif queue_diff>=1:
            self.decrease_thread()"""
    
    # 全スレッドを終了させるメソッド
    def terminate_all(self):
        # 全スレッドの終了フラグを立てる
        for thread in self.thread_list:
            thread.terminate()
        
        # スレッドが終了するまでキューをフラッシュ
        while active_count() >=3:
            self.queue.flush()
            sleep(1)
       
    # キューからフレームを取り出すメソッド
    def pop_frame(self):
        while True:
            # キューを1つ選んでフレームを取得 (空なら隣のキューへ)
            scan_flag = True
            while scan_flag:
                queue = self.queue_list[self.queue_pointer]
                if not queue.empty():
                    frame_num, frame = queue.get()
                    scan_flag = False
                self.move_queue_pointer()
            
            # 取得したフレームが次番なら採用、違ったら保留
            if frame_num == self.next_frame_num:
                self.next_frame_num += 1
                return (frame_num, frame)
            else:
                self.skipped_frame[0].append(frame_num)
                self.skipped_frame[1].append(frame)
                
                # 保留したフレームの中に次番のフレームがあれば採用
                frame_num = min(self.skipped_frame[0])
                if frame_num == self.next_frame_num:
                    idx = self.skipped_frame[0].index(frame_num)
                    frame = self.skipped_frame[1][idx]
                    self.skipped_frame[0].pop(idx)
                    self.skipped_frame[1].pop(idx)
                    self.next_frame_num += 1
                    return (frame_num, frame)
    
    # 起動中のスレッド数を取得するメソッド
    def check_thread_num(self):
        list_thread_num = len(self.thread_list)
        real_thread_num  = active_count()
        return (list_thread_num, real_thread_num)
    
    """# キュー内のフレーム数を取得するメソッド
    def check_queue_size(self):
        queue_size = self.queue.qsize()
        return queue_size"""

