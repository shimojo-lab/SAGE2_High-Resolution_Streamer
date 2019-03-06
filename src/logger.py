# -*- coding: utf-8 *-*

PROMPT = '[SAGE2_Streamer]>' 

class Logger:
    # print a normal message on the console
    @staticmethod
    def print_info(msg):
        print('%s %s' % (PROMPT, msg))
    
    # print an OK message on the console
    @staticmethod
    def print_ok(msg):
        print('%s \033[32m[OK]\033[0m %s' % (PROMPT, msg))
    
    # print a warning message on the console
    @staticmethod
    def print_warn(msg):
        print('%s \033[33m[Warning]\033[0m %s' % (PROMPT, msg))
    
    # print an error message on the console
    @staticmethod
    def print_err(msg):
        print('%s \033[31m[Error]\033[0m %s' % (PROMPT, msg))
    

