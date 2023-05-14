"""
@Project ：Scripts
@File    ：ocr.py
@Author  ：Hotakus (hotakus@foxmail.com)
@Date    ：2023/4/20 15:39
"""

from cnocr import CnOcr
from threading import Thread
from time import sleep, ctime
from pro_thread import *


class OcrThread(ProThread):
    def run(self):
        self.result = self.func(self.args)


def _cnocr(pic_name: str, model: str = 'naive_det'):
    res = CnOcr(det_model_name=model).ocr(pic_name)
    if confidence_level(res) < 0.75:
        res = CnOcr().ocr(pic_name)
    return res


def confidence_level(res):
    score = 0
    for i, val in enumerate(res):
        score += float(val['score'])
    confidence = score / res.__len__()
    return confidence


def ocr_recognize(pic_name: str):
    res = _cnocr(pic_name)
    return res


def ocr_text_connect(ocr_list: list):
    txt = ''
    for line in ocr_list:
        txt += line['text']
    return txt


def ocr_create_threads(func, args: list, cnt: int = 0):
    """
    连续创建OCR识别线程
    ocr_create_threads(ocr_recognize, ['*.jpg', '*.png'])
    :param func: 执行函数
    :param args: pic_name的列表
    :param cnt: 要创建的线程数
    :return:
    """
    threads_list = []
    if args.__len__() == 0:
        return None
    if cnt == 0:
        cnt = args.__len__()

    # 创建线程
    for t in range(cnt):
        thread = OcrThread(func, args[t])
        threads_list.append(thread)
    return threads_list


def ocr_start_threads(tl: list, wait: bool = True):
    """
    从 threads list 启动 thread
    :param wait: 是否join
    :param tl: threads list
    :return:
    """
    for t in tl:
        t.start()
        if wait:
            t.join()


def ocr_threads_result(tl: list, connect: bool = True):
    """
    获取OCR list结果，若connect==True，则返回文章拼接后内容，否则返回文章分段列表
    :param tl: 线程列表
    :param connect: 是否拼接
    :return: 若connect==True，则返回文章拼接后内容，否则返回文章分段列表
    """

    result = []
    for t in tl:
        result.append(t.get_result())

    if connect:
        tmp = result
        result = ''
        for i in tmp:
            result += ocr_text_connect(i)

    return result


import docx


def ocr_test():
    """
    用于测试
    :return:
    """
    name_list = [
        'test0.jpg',
        'test1.jpg',
        'test2.jpg',
        'test3.jpg',
        'test4.jpg',
    ]

    res = _cnocr('test0.jpg')
    print(res)

    doc = docx.Document()

    # tl = ocr_create_threads(ocr_recognize, name_list)
    # ocr_start_threads(tl)

    # res = ocr_threads_result(tl)
    # doc.add_paragraph(res)
    # doc.save("test.docx")
    # print(res)
