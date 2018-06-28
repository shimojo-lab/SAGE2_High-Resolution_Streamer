# -*- coding: utf-8 *-*
# output.py (コンソール出力用関数)

PROMPT = '[SAGE2_Streamer]>'

# コンソールにメッセージを表示する関数
def normal_output(sentence):
    msg = '%s %s' % (PROMPT, sentence)
    print(msg)

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

