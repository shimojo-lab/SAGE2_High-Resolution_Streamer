# *-* encoding: utf-8 *-*
## thread_manager.py (スレッド管理モジュール)

from queue import Queue, PriorityQueue
from time import sleep
from threading import active_count
from .utils import normal_output, ok_output, error_output
from .capturing_thread import FrameCapturer
from .conversion_thread import FrameConverter
from .compression_thread import FrameCompressor

## スレッドを管理するクラス
class ThreadManager:
    # コンストラクタ
    def __init__(self, comp_thread_num, raw_queue_size, np_queue_size, comp_queue_size, loglevel, display, width, height, depth, framerate, comp, quality):
        # パラメータを設定
        self.comp = comp                               # フレームの圧縮形式
        self.quality = quality                         # フレームの圧縮品質
        self.display = display                         # ディスプレイ番号
        self.framerate = framerate                     # 録画のフレームレート
        self.next_frame_num = 0                        # 次番のフレーム番号
        self.pre_frame = None                          # 前回送信したフレーム
        
        # フレームキューを用意
        self.raw_frame_queue = Queue(raw_queue_size)
        self.np_frame_queue = Queue(np_queue_size)
        self.comp_frame_queue = PriorityQueue()
        
        # フレームキャプチャ用スレッドを初期化
        self.capturer = FrameCapturer(raw_frame_queue=self.raw_frame_queue,
                                      loglevel=loglevel,
                                      display=display,
                                      width=width,
                                      height=height,
                                      depth=depth,
                                      framerate=self.framerate)
        
        # フレーム変換用スレッドを初期化
        self.converter = FrameConverter(raw_frame_queue=self.raw_frame_queue,
                                        np_frame_queue=self.np_frame_queue,
                                        width=width,
                                        height=height)
        
        # フレーム圧縮用スレッドを初期化
        self.compressors = []
        for i in range(comp_thread_num):
            compressor = FrameCompressor(np_frame_queue=self.np_frame_queue,
                                         comp_frame_queue=self.comp_frame_queue,
                                         width=width,
                                         height=height,
                                         comp=self.comp,
                                         quality=self.quality)
            self.compressors.append(compressor)
    
    # キャプチャを開始させるメソッド
    def init(self):
        # 各スレッドを起動
        self.capturer.start()
        self.converter.start()
        for compressor in self.compressors:
            compressor.start()
        
        # フレームキューが充填されるまで待機
        while self.comp_frame_queue.qsize() < len(self.compressors):
            sleep(1)
        ok_output('Captured from Display :%d' % self.display)
    
    # 全スレッドを終了させるメソッド
    def terminate_all(self):
        self.capturer.terminate()
        self.raw_frame_queue.get()
        self.capturer.join()
        
        self.converter.terminate()
        self.np_frame_queue.get()
        self.converter.join()
        
        for compresser in self.compressers:
            compresser.terminate()
            self.comp_frame_queue.get()
            compresser.join()
    
    # 次番のフレームを取り出すメソッド
    def get_next_frame(self):
        # 次番のフレームでなければキューに戻してやり直し
        while True:
            frame_num, frame = self.comp_frame_queue.get()
            if frame_num == self.next_frame_num:
                self.next_frame_num += 1
                return (frame_num, frame)
            elif frame == None:
                self.next_frame_num += 1
            else:
                self.comp_frame_queue.put((frame_num, frame))

