"""
@Project ：get gov file
@File    ：get_papers.py
@Author  ：Hotakus (hotakus@foxmail.com)
@Date    ：2023/4/19 18:36
"""
import os

# web
import requests
import re
from bs4 import BeautifulSoup

# misc
import time
import random as rand
import datetime as dt
import docx

# project
from ocr import ocr_recognize, ocr_create_threads, \
    ocr_start_threads, ocr_threads_result
from pro_random import req_headers, random_user_agent

# 政府网站文章基本信息
gov_art_begin_code = 10310  # 起始文章码
gov_art_end_code = 6431  # 尾文章码
gov_art_code_scope = range(gov_art_begin_code, gov_art_end_code, -1)  # 文章码范围
gov_art_begin_date = dt.datetime(2023, 3, 30)  # 首个文章的日期
gov_art_end_date = dt.datetime(2017, 1, 19)  # 最后一个文章的日期
date_format = "%Y/%#m/%#d"  # 日期格式
file_name_date_format = "%Y_%m_%d"  # 日期格式

# 文章链接结构
gov_base_url = 'http://www.nhsa.gov.cn/'
gov_art_passage_div_id: str = 'zoom'  # 文章正文div id

docs_folder = './documents/'
pics_folder = './pictures/'


def extract_pic_url(main_part: BeautifulSoup):
    """
    提取图片地址
    :param main_part: 文章主体
    :return: 成功获取图像则返回图像链接列表，否则返回 None
    """

    if not main_part:
        return None

    pic_div = list(main_part.find_all(name='a'))
    pic_url = []

    if not pic_div:
        return None

    for p in pic_div:
        try:
            if 'href' in p.attrs:
                url = gov_base_url + p.attrs['href']
                suffix = url[-4:]
                if suffix == '.jpg':
                    pic_url.append(url)
                else:  # TODO:
                    pass
            else:
                # TODO
                pass
        except:
            print(p)

    return pic_url


def extract_article(req: requests.Response = None, save_name: str = '', content: str = ''):
    """
    提取文章，包括文字提取和图片文字提取
    :param content:
    :param save_name: 图片名
    :param req: 请求
    :return:
    """
    text = ''

    if content != '':
        text = content
    else:
        text = req.text

    soup = BeautifulSoup(text, "html.parser")
    art_main_part = soup.find(id=gov_art_passage_div_id)  # 文章正文主体
    art_index_num = save_name[:14].replace(' ', '')
    res = ''

    pic_url = extract_pic_url(art_main_part)  # 判断是否有图片，有则提取
    if not os.path.exists(pics_folder):
        os.mkdir(pics_folder)

    # OCR提取图片
    if pic_url:
        pic_name = []
        for i, url in enumerate(pic_url):
            req_headers['User-Agent'] = random_user_agent()
            req2 = requests.get(url=url, headers=req_headers)
            name = pics_folder + art_index_num + '_' + i.__str__() + '.jpg'
            pic_name.append(name)
            with open(name, 'wb') as f:
                f.write(req2.content)

        # 创建OCR识别线程
        tl = ocr_create_threads(ocr_recognize, pic_name)
        ocr_start_threads(tl)
        res = ocr_threads_result(tl)

    # TODO: (正则)提取文本
    for i in soup.find_all('p'):
        res += i.text

    return res


def save_article(base_dir=docs_folder, art_title: str = '', content: str = '', suffix: str = '.docx'):
    """
    将内容保存到文章
    :param suffix: 文件保存后缀
    :param base_dir: 保存到哪个文件夹
    :param art_title: 文章标题
    :param content: 文章内容
    :return: Bool
    """
    if art_title == '':
        print("Article needs a title")
        return False

    if not os.path.exists(base_dir):
        os.makedirs(base_dir)

    save_dir = base_dir + art_title + suffix
    if suffix == '.docx':
        doc = docx.Document()
        paragraph = doc.add_paragraph(content)
        doc.save(save_dir)
    elif suffix == 'html':
        with open(save_dir, 'w', encoding='utf-8') as f:
            f.write(content)

    return True


def got_art(stats, art_date, art_url, id):
    """
    当轮询获取到文章时，进行文件操作
    :param stats: http请求的状态
    :param art_date: 文章日期
    :param art_url: 文章链接
    :param id: 文章序号
    :return:
    """
    content = extract_article(stats['req'])
    save_article(id.__str__() + '_' + art_date.strftime(file_name_date_format) + content[0], content[1])
    print("[" + id.__str__() + "]" + " Successfully get: " + art_url)
