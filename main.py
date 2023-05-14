"""
@Project ：Scripts 
@File    ：main.py
@Author  ：Hotakus (hotakus@foxmail.com)
@Date    ：2023/4/21 4:32 
"""
# import sys
import os
import threading
import time
from typing import Dict, Union, List, Any

# web
import requests
from bs4 import BeautifulSoup
from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn, SpinnerColumn, TimeElapsedColumn
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select

# project
from src.get_papers import save_article, docs_folder, extract_article, pics_folder
from src.pro_random import random_user_agent, req_headers
from src.pro_thread import ProThread

# from selenium.webdriver.support.wait import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from urllib.parse import urlparse
# misc
# import random as rand
# import datetime as dt
# import docx
# from tqdm import tqdm
# import re

progress = Progress(TextColumn("[progress.description]{task.description}"),
                    SpinnerColumn(),
                    BarColumn(),
                    TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                    TimeRemainingColumn(),
                    TimeElapsedColumn()
                    )

# 网站基本信息
gov_base_url = 'http://www.nhsa.gov.cn/'
art_content_base_url: str = gov_base_url + 'col/col104/index.html?uid=2464&pageNum='  # 文章目录页基址
art_content_per_page: str = '15'  # 每页15篇文章
art_content_page_num: int = 1  # 当前目录页
art_content_max_page_num: int = 12  # 当前目录页
content_part_id = '2464'  # 标签id

get_error_list = []
content_list_path = 'content_list.txt'

the_browser_path = "./Chrome/App/chrome.exe"
the_browser_driver_path = "./Chrome/App/chromedriver.exe"


class DownloadThread(ProThread):
    def run(self):
        self.result = self.func(self.args)


def get_website(url: str = ""):
    """
    获取网址内容
    :param url: 要获取的网址
    :return: dict(is_got, req)，若网页访问失败，则调用selenium，并返回网页源码str
    """
    stats = {
        'is_got': False,  # 是否获取成功
        'req': requests.Response(),  # 响应
    }

    if url == "":
        return stats

    # 设置 headers
    # up = urlparse(url)
    # req_headers['Host'] = up.scheme + "://" + up.netloc + '/'
    # req_headers['Referer'] = url
    # req_headers['Cookie'] = ''

    req_headers['User-Agent'] = random_user_agent()
    stats['req'] = requests.get(url=url, headers=req_headers)
    stats['req'].encoding = 'utf-8'
    if stats['req'].status_code == 200:
        stats['is_got'] = True
    elif stats['req'].status_code >= 400:

        webd = get_edge_driver()
        webd.get(url)
        time.sleep(3)  # TODO: test wait
        stats = webd.page_source

        # TODO: determine status code

        # retry = 5
        # while stats['req'].status_code != 200 and retry > 0:
        #     req_headers['User-Agent'] = random_user_agent()
        #     stats['req'].status_code = requests.get(url=req_headers['Referer'], headers=req_headers)
        #     retry -= 1
        #     time.sleep(0.7)
        # stats['is_got'] = False
        # get_error_list.append(req_headers)
        return stats

    return stats


def get_art_link(soup: BeautifulSoup, append: dict = None) -> Union[None, dict, Dict[str, List[Any]]]:
    """
    提取链接与文章标题
    :param append: 添加到现有link列表
    :param soup: 要操作的soup
    :return: dict of links_list and titles_list
    """
    if append is None:
        return None
    dic = {
        'links_list': [],
        'titles_list': []
    }
    if append:
        dic = append

    full_name_list = soup.find(class_='default_pgContainer').find_all('li')
    links_list = soup.find(class_='default_pgContainer').find_all('a')
    for i, name in enumerate(full_name_list):
        dic['links_list'].append(links_list[i].attrs['href'])
        dic['titles_list'].append(name.text.strip())
        # print(link[i].attrs['href'])

    return dic


def check_and_concat_art_link(links_list: List[str], links_prefix: str):
    """
    检查链接格式是否正确，以及使用 links_prefix 与links_list拼接成有效文章链接
    :param links_list: 链接列表
    :param links_prefix: 链接前缀
    :return: 有效化的链接列表
    """
    tmp = []
    for link in links_list:
        cur_links_prefix = link[0:4]
        if cur_links_prefix == '/art':
            tmp.append(links_prefix + link)
        elif cur_links_prefix == 'http':
            tmp.append(link)
        else:
            pass
    return tmp


download_done_cnt = 0
sem_cnt = threading.Semaphore(1)
pbar_download_task = None


class CustomResponse(requests.Response):
    def __init__(self):
        requests.Response.__init__(self)
        self.extra_text = None


# TODO: 优化信息显示
def _article_download(args):
    """
    文章下载任务代码
    :param args: content list，二维列表 arg[0]为links，arg[1]为titles, [links_list, titles_list]
    :return: None
    """
    links_list = args[0]
    titles_list = args[1]
    global download_done_cnt
    global pbar_download_task
    prompt = 'Downloading'
    text = ''
    stats_is_txt = False

    self_id = progress.add_task(threading.current_thread().name, total=links_list.__len__())
    time.sleep(0.1)

    # 根据content list循环获取政策网页内容
    for i, link in enumerate(links_list):
        stats = get_website(url=link)
        if isinstance(stats, str):
            text = stats
            stats_is_txt = True
        else:
            stats_is_txt = False
            if not stats['is_got']:
                continue
            else:
                text = stats['req'].text

        # 文件分析
        save_name = titles_list[i].replace('/', '、')
        if not stats_is_txt:
            text = extract_article(req=stats['req'], save_name=save_name)
        else:
            text = extract_article(save_name=save_name, content=stats)

        # 文档保存
        save_article(art_title=save_name, content=text)
        progress.update(self_id, advance=1)

        # 信号量更新状态信息
        sem_cnt.acquire()
        download_done_cnt += 1
        progress.update(pbar_download_task, advance=1,
                        description=("[cyan]%s...[%d/%d]" % (prompt, download_done_cnt, content_len)))
        print("OK[%d]...%s" % (download_done_cnt, save_name))
        if progress.finished:
            if download_done_cnt == content_len:  # 如果成功下载的数量等于目录列表项数量，则为正常
                prompt = 'Done'
            else:
                prompt = 'Failed'
        progress.update(pbar_download_task, advance=0,
                        description=("[cyan]%s...[%d/%d]" % (prompt, download_done_cnt, content_len)))
        sem_cnt.release()

        time.sleep(0.2)

    progress.remove_task(self_id)
    time.sleep(0.5)


def _create_download_threads(func, content_list: dict, t_slice_num=1):
    """
    创建指定批次的下载线程
    :param func: 下载线程句柄
    :param content_list: 下载链接列表
    :param t_slice_num: 分批数
    :return: 分批线程列表
    """
    threads_list = []
    if t_slice_num > content_list['links_list'].__len__():
        return threads_list

    # 切分
    slice_list = []  # 分批列表
    extra_num = content_list['links_list'].__len__() % t_slice_num  # 求余，为余数项创建额外的下载线程
    slice_len = content_list['links_list'].__len__() // t_slice_num  # 每个slice的长度
    pre_pos = 0
    next_pos = slice_len
    for _ in range(t_slice_num):
        # 组合链接和文章标题
        pattern = [content_list['links_list'][pre_pos:next_pos], content_list['titles_list'][pre_pos:next_pos]]
        slice_list.append(pattern)
        pre_pos = next_pos
        next_pos += slice_len
    if extra_num:
        pattern = [content_list['links_list'][pre_pos:], content_list['titles_list'][pre_pos:]]
        slice_list.append(pattern)

    # 为线程分配任务
    for i, v in enumerate(slice_list):
        t = DownloadThread(func, v, name='Thread' + i.__str__())
        threads_list.append(t)

    return threads_list


def _start_download_threads(tl: List[DownloadThread], wait: bool = True):
    for t in tl:
        t.start()

    if wait:
        for t in tl:
            t.join()


def batch_download(content_list: dict, slice_num=1):
    """
    批量下载链接列表的文件
    :param content_list: 目录列表
    :param slice_num: 分片数
    :return:
    """
    tl = _create_download_threads(_article_download, content_list, slice_num)
    return tl


def batch_download_start(tl: list, wait: bool = True):
    global pbar_download_task
    pbar_download_task = progress.add_task("[cyan]Downloading...", total=content_len)
    time.sleep(1)
    _start_download_threads(tl, wait)


def get_edge_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-gpu")
    # options.add_argument("--no-sandbox")  # linux only
    options.add_argument('–-incognito')
    options.add_argument('--disable-infobars')
    options.add_experimental_option("excludeSwitches", ["enable-automation", 'enable-logging'])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_argument("--disable-blink-features=AutomationControlled")

    options.binary_location = the_browser_path
    wd_service = Service(executable_path=the_browser_driver_path)
    driver = webdriver.Chrome(options=options, service=wd_service)
    # driver = webdriver.Chrome(options=options)

    # driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
    #     "source": """
    #       Object.defineProperty(navigator, 'webdriver', {
    #         get: () => undefined
    #       })
    #     """
    # })

    return driver


def get_content_list(driver: str = '', page_num=art_content_max_page_num):
    """
    预下载，获取目录列表，为下载文章网页源码做准备
    :param page_num: 要获取多少页的文章
    :param driver: 设定webdriver，空则使用默认
    :return: content list
    """
    content_list = []
    timeout = 20
    prompt = "[cyan]Get content list[%d/%d]"
    page = 0

    pre_download_bar = progress.add_task(prompt % (page, page_num - 1), total=page_num)
    progress.start()

    if os.path.exists(docs_folder + content_list_path):
        with open(docs_folder + content_list_path, 'r', encoding='utf-8') as f:
            content_list = eval(f.read())
    else:
        webd = get_edge_driver()
        webd.get(art_content_base_url + art_content_page_num.__str__())
        webd.implicitly_wait(5)
        for page in range(1, page_num):
            # 下拉框选择
            sel = webd.find_element(By.CLASS_NAME, 'default_pgPerPage')
            Select(sel).select_by_value(art_content_per_page)
            # WebDriverWait(webd, timeout).until(
            #    EC.presence_of_all_elements_located((By.XPATH, '//div[@id=2464]/div/ul')))

            time.sleep(2)

            # 获取content_list
            source = webd.page_source
            soup = BeautifulSoup(source, "html.parser")
            content_part = soup.find(id=content_part_id)
            content_list = get_art_link(content_part, content_list)
            content_list['links_list'] = check_and_concat_art_link(content_list['links_list'], gov_base_url)

            next_btn = webd.find_element(By.CLASS_NAME, 'default_pgNext')
            next_btn.click()

            progress.update(pre_download_bar, advance=1, description=prompt % (page, page_num))

    time.sleep(0.5)
    progress.remove_task(pre_download_bar)

    global content_len
    content_len = content_list['links_list'].__len__()
    # 将content列表进行保存
    if not os.path.exists(docs_folder):
        os.makedirs(docs_folder)
    with open(docs_folder + content_list_path, 'w', encoding='utf-8') as f:
        f.write(content_list.__str__())

    return content_list


def print_error_links():
    for i, v in enumerate(get_error_list):
        print("Error[%d] : %s" % (i, v['Referer']))


def done_prompt():
    print('The documents were downloaded in "%s"' % docs_folder)
    print('The pictures were downloaded in "%s"' % pics_folder)
    print('Press any key to exit')


if __name__ == "__main__":
    content_len = 0

    clist = get_content_list(page_num=art_content_max_page_num)  # 获取目录列表
    tlist = batch_download(clist, art_content_max_page_num)  # 分批下载准备工作
    batch_download_start(tlist)  # 分配下载开始

    done_prompt()

    # url = 'http://www.nhc.gov.cn/yzygj/s7659/202210/2875ad7e2b2e46a2a672240ed9ee750f.shtml'
    # txt = get_website(url)
    # soup = BeautifulSoup(txt, "html.parser")
    #
    # for i in soup.find_all('p'):
    #     print(i.text)

    os.system("pause")
