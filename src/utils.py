# -*- coding: utf-8 *-*
# utils.py (その他の機能)

PROMPT = '[SAGE2_Streamer]>'

# コンソールにメッセージを表示する関数
def normal_output(sentence):
    msg = '%s %s' % (PROMPT, sentence)
    print(msg)

# コンソールに改行なしメッセージを表示する関数
def nonbreak_output(sentence):
    msg = '%s %s.....' % (PROMPT, sentence)
    print(msg, end='')

# コンソールにOKを表示する関数
def ok_output(sentence):
    msg = '%s \033[32m[OK]\033[0m %s' % (PROMPT, sentence)
    print(msg)

# コンソールにErrorを表示する関数
def error_output(sentence):
    msg = '%s \033[31m[Error]\033[0m %s' % (PROMPT, sentence)
    print(msg)

# コンソールにWarningを表示する関数
def warning_output(sentence):
    msg = '%s \033[33m[Warning]\033[0m %s' % (PROMPT, sentence)
    print(msg)

