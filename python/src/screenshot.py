# *-* encoding: utf-8 *-*
## screenshot.py
## (画面キャプチャを行うクラス)

from platform import system
import pyautogui

class ScreenCapturer:
    def __init__(self):
        self.os = system()
        return
    
    def capture(self):
        if self.os == 'Windows':
            img = None
        elif self.os=='Darwin' or self.os=='Linux':
            img = pyautogui.screenshot()
        else:
            syst.stderr.write('Error: This operating system is unsupported.')
            exit()
        return img

