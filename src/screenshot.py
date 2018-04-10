# *-* encoding: utf-8 *-*
## screenshot.py
## (スクリーンショットを撮影)

from platform import system
import pyautogui

class ScreenCapturer:
    def __init__(self):
        self.os = system()
        return
    
    def capture(self):
        if self.os == 'Windows':
            img = 0
        elif self.os == 'Darwin':
            img = pyautogui.screenshot()
        elif self.os == 'Linux':
            img = pyautogui.screenshot()
        else:
            syst.stderr.write('Error: This operating system is unsupported.')
            exit()
        return img

