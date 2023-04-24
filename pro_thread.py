"""
@Project ：Scripts 
@File    ：pro_thread.py
@Author  ：Hotakus (hotakus@foxmail.com)
@Date    ：2023/4/20 17:38 
"""

from threading import Thread
from time import sleep, ctime


class ProThread(Thread):
    def __init__(self, func, args, name=None):
        """
        :param func: 可调用的对象
        :param args: 可调用对象的参数
        """
        Thread.__init__(self, name=name)
        self.func = func
        self.args = args
        self.result = None

    def run(self):
        self.result = self.func(*self.args)

    def get_result(self):
        return self.result
