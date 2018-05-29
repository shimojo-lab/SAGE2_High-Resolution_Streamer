# *-* encoding: utf-8 *-*
## thread_manager.py (スレッド管理モジュール)

from queue import Queue, PriorityQueue
from time import sleep
from threading import active_count
from .utils import normal_output, ok_output, error_output
from .capturing_thread import FrameCapturer
from .compression_thread import FrameCompresser

## キャプチャ用スレッドを管理するクラス
class ThreadManager:
    # コンストラクタ
    def __init__(self, comp_thread_num, raw_queue_size, comp_queue_size, loglevel, display, width, height, depth, framerate, comp, quality):
        # パラメータを設定
        self.comp = comp                               # フレームの圧縮形式
        self.quality = quality                         # フレームの圧縮品質
        self.display = display                         # ディスプレイ番号
        self.framerate = framerate                     # 録画のフレームレート
        self.next_frame_num = 0                        # 次番のフレーム番号
        self.reserved_frames = {"num": [], "src": []}  # 保留したフレームのリスト
        self.pre_frame = None                          # 前回送信したフレーム
        
        # フレームキューを用意
        self.raw_frame_queue = Queue(raw_queue_size)            # 生フレームキュー
        self.comp_frame_queue = PriorityQueue(comp_queue_size)  # 圧縮フレームキュー
        
        # フレームキャプチャ用スレッドを初期化
        self.capturer = FrameCapturer(raw_frame_queue=self.raw_frame_queue,
                                      loglevel=loglevel,
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
        ok_output('Captured from Display :%d' % self.display)
    
    # 全スレッドを終了させるメソッド
    def terminate_all(self):
        # 全スレッドの終了フラグを立てる
        self.capturer.terminate()
        for compresser in self.compressers:
            compresser.terminate()
        
        # スレッドが終了するまで待機
        self.raw_frame_queue.get()
        self.comp_frame_queue.get()
        self.capturer.join()
        for compresser in self.compressers:
            compresser.join()
        exit(0)
    
    # 保留したフレームに次番のフレームが無いか探すメソッド
    def check_reserved_frames(self):
        result = None
        if len(self.reserved_frames['num']) != 0:
            min_frame_num = min(self.reserved_frames['num'])
            if min_frame_num == self.next_frame_num:
                idx = self.reserved_frames['num'].index(min_frame_num)
                frame = self.reserved_frames['src'][idx]
                self.reserved_frames['num'].pop(idx)
                self.reserved_frames['src'].pop(idx)
                self.next_frame_num += 1
                result = (min_frame_num, frame)
        return result
    
    # 圧縮フレームキューから次番フレームを取り出すメソッド
    def get_next_frame(self):
        # 保留したフレームをチェック
        frame_set = self.check_reserved_frames()
        
        # 保留したフレームに無いなら圧縮フレームキューから取得
        if frame_set == None:
            while True:
                frame_num, frame = self.comp_frame_queue.get()
                if frame == None:
                    self.next_frame_num += 1
                    continue
                elif frame_num == self.next_frame_num:
                    self.next_frame_num += 1
                    frame_set = (frame_num, frame)
                    break
                else:
                    self.reserved_frames['num'].append(frame_num)
                    self.reserved_frames['src'].append(frame)
        return frame_set
    
    # 送信するフレームを取得するメソッド
    def get_new_frame(self, fps):
        # 送信側のフレームレートに応じてフレームを読み飛ばし
        fps = self.framerate if self.framerate<=fps else fps
        skip_frame_num = int(self.framerate/fps)
        for i in range(skip_frame_num):
            frame_num, frame = self.get_next_frame()
        
        # 前回送信したフレームと変化がないならやり直し
        while True:
            if frame != self.pre_frame:
                self.pre_frame = frame
                return (frame_num, frame)
            else:
                frame_num, frame = self.get_next_frame()

