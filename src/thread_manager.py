# *-* encoding: utf-8 *-*
## thread_manager.py (スレッド管理モジュール)

from queue import Queue, PriorityQueue
from time import sleep
from threading import active_count
from .utils import normal_output, ok_output, error_output
from .capturing_thread import FrameCapturer
from .concatenation_thread import FrameConcatenater
from .compression_thread import FrameCompresser

## キャプチャ用スレッドを管理するクラス
class ThreadManager:
    # コンストラクタ
    def __init__(self, capture_thread_num, comp_thread_num, split_queue_size, np_queue_size, comp_queue_size, loglevel, display, width, height, depth, framerate, comp, quality):
        # パラメータを設定
        self.comp = comp                               # フレームの圧縮形式
        self.quality = quality                         # フレームの圧縮品質
        self.display = display                         # ディスプレイ番号
        self.framerate = framerate                     # 録画のフレームレート
        self.next_frame_num = 0                        # 次番のフレーム番号
        self.reserved_frames = {'num': [], 'src': []}  # 保留したフレームのリスト
        self.pre_frame = None                          # 前回送信したフレーム
        
        # 各フレームキューを用意
        self.split_frame_queues = [PriorityQueue(split_queue_size) for i in range(capture_thread_num)]
        self.np_frame_queue = PriorityQueue(np_queue_size)
        self.comp_frame_queue = PriorityQueue(comp_queue_size)
        
        # フレームキャプチャ用スレッドを初期化
        self.capturers = []
        for i in range(capture_thread_num):
            capturer = FrameCapturer(split_frame_queue=self.split_frame_queues[i],
                                     loglevel=loglevel,
                                     display=display,
                                     region=i,
                                     width=width,
                                     height=int(height/capture_thread_num),
                                     depth=depth,
                                     framerate=self.framerate)
            self.capturers.append(capturer)
        
        # フレーム結合用スレッドを初期化
        self.concatenater = FrameConcatenater(split_frame_queues=self.split_frame_queues,
                                              np_frame_queue=self.np_frame_queue,
                                              width=width,
                                              height=height)
        
        # フレーム圧縮用スレッドを初期化
        self.compressers = []
        for i in range(comp_thread_num):
            compresser = FrameCompresser(np_frame_queue=self.np_frame_queue,
                                         comp_frame_queue=self.comp_frame_queue,
                                         width=width,
                                         height=height,
                                         comp=self.comp,
                                         quality=self.quality)
            self.compressers.append(compresser)
    
    # キャプチャを開始させるメソッド
    def init(self):
        # 各スレッドを起動
        for capturer in self.capturers:
            capturer.start()
        self.concatenater.start()
        for compresser in self.compressers:
            compresser.start()
        
        # フレームキューが充填されるまで待機
        while not self.comp_frame_queue.full():
            sleep(1)
        ok_output('Captured from Display :%d' % self.display)
    
    # 全スレッドを終了させるメソッド
    def terminate_all(self):
        for i, capturer in enumerate(self.capturers):
            capturer.terminate()
            capturer.split_frame_queues[i].get()
            capturer.join()
        
        self.concatenater.terminate()
        self.concatenater.join()
        
        for compresser in self.compressers:
            compresser.terminate()
            self.comp_frame_queue.get()
            compresser.join()
    
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
        print(self.split_frame_queues[0].qsize())
        return (frame_num, frame)
        
        # 前回送信したフレームと変化がないなら取得し直し
        """while True:
            if frame != self.pre_frame:
                self.pre_frame = frame
                return (frame_num, frame)
            else:
                frame_num, frame = self.get_next_frame()"""

