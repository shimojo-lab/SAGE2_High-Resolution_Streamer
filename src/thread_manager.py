# *-* encoding: utf-8 *-*
## thread_manager.py (スレッド管理モジュール)

from queue import PriorityQueue
from time import sleep
from .utils import normal_output, status_output, error_output
from .capturing_thread import FrameCapturer
from .compression_thread import FrameCompresser

## キャプチャ用スレッドを管理するクラス
class ThreadManager:
    # コンストラクタ
    def __init__(self, comp_thread_num, raw_queue_size, comp_queue_size, display, width, height, depth, framerate, comp, quality):
        # パラメータを設定
        self.comp = comp                              # フレームの圧縮形式
        self.quality = quality                        # フレームの圧縮品質
        self.display = display                        # ディスプレイ番号
        self.framerate = framerate                    # 録画のフレームレート
        self.next_frame_num = 0                       # 次番のフレーム番号
        self.reserved_frame = {"num": [], "src": []}  # 保留したフレームのリスト
        
        # フレームキューを用意
        self.raw_frame_queue = PriorityQueue(raw_queue_size)    # 生フレームキュー
        self.comp_frame_queue = PriorityQueue(comp_queue_size)  # 圧縮フレームキュー
        
        # フレームキャプチャ用スレッドを初期化
        self.capturer = FrameCapturer(raw_frame_queue=self.raw_frame_queue,
                                      display=display,
                                      width=width,
                                      height=height,
                                      depth=depth,
                                      framerate=self.framerate)
        
        # フレーム圧縮スレッドを初期化
        self.compressers = []
        for i in range(comp_thread_num):
            compresser = FrameCompresser(raw_frame_queue=self.raw_frame_queue,
                                         comp_frame_queue=self.comp_frame_queue,
                                         width=width,
                                         height=height,
                                         comp=self.comp,
                                         quality=self.quality)
            self.compressers.append(compresser)
    
    # キャプチャを開始させるメソッド
    def init(self):
        # スレッドを起動
        self.capturer.start()
        for compresser in self.compressers:
            compresser.start()
        
        # フレームキューが充填されるまで待機
        while not self.comp_frame_queue.full():
            sleep(1)
        status_output(True)
        normal_output('Captured from Display :%d' % self.display)
    
    # 全スレッドを終了させるメソッド
    def terminate_all(self):
        # 全スレッドの終了フラグを立てる
        self.capturer.terminate()
        for compresser in self.compressers:
            compresser.terminate()
        
        # スレッドが終了するまでキューをフラッシュ
        while active_count() >=3:
            self.raw_frame_queue.flush()
            self.comp_frame_queue.flush()
            sleep(1)
       
    # 圧縮フレームキューから次番フレームを取り出すメソッド
    def pop_next_frame(self, fps):
        while True:
            # 送信側のフレームレートに応じてフレームを読み飛ばし
            fps = self.framerate if self.framerate<=fps else fps
            skip_frame_num = int(self.framerate/fps) - 1
            for i in range(skip_frame_num):
                self.comp_frame_queue.get()
            self.next_frame_num += skip_frame_num
            frame_num, frame = self.comp_frame_queue.get()
            
            # フレームが取得できていなければやり直し
            if frame != None:
                # 取得したフレームが次番なら採用、違ったら保留
                if frame_num == self.next_frame_num:
                    self.next_frame_num += 1
                    return (frame_num, frame)
                else:
                    self.reserved_frame['num'].append(frame_num)
                    self.reserved_frame['src'].append(frame)
                    
                    # 保留したフレームの中に次番のフレームがあれば採用
                    min_frame_num = min(self.reserved_frame['num'])
                    if min_frame_num == self.next_frame_num:
                        idx = self.reserved_frame['num'].index(min_frame_num)
                        frame = self.reserved_frame['src'][idx]
                        self.reserved_frame['num'].pop(idx)
                        self.reserved_frame['src'].pop(idx)
                        self.next_frame_num += 1
                        return (frame_num, frame)
            else:
                self.next_frame_num += 1
                continue

