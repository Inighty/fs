# -*- coding: utf-8 -*-
import datetime
import json
import logging
import os
import random
import re
import time
import urllib.request
from mimetypes import guess_extension

import filetype as filetype
import scrapy
from bs4 import BeautifulSoup
from scrapy import Request

from zzspider import settings
from zzspider.config import ConfigUtil
from zzspider.tools.browser import Browser
from zzspider.tools.dbhelper import DBHelper
from zzspider.tools.sftp import Sftp

browser = Browser()
dbhelper = DBHelper()
sftp = Sftp()
logger = logging.getLogger(__name__)
sentence_pattern = r',|\.|/|;|\'|`|\[|\]|<|>|\?|:|：|"|\{|\}|\~|!|@|#|\$|%|\^|&|？|\(|\)|-|=|\_|\+|，|。|、|；|‘|’|【|】|·|！| |…|（|）'


def after_insert_post(word_id, author, cate, url):
    dbhelper.execute(f"update zbp_words set used = 1, url = {url} where id = {word_id}")
    dbhelper.execute(
        f"update zbp_member set mem_Articles = mem_Articles + 1, mem_PostTime = {int(round(time.time()))} where mem_ID = {author}")
    dbhelper.execute(
        f"update zbp_category set cate_Count = cate_Count + 1 where cate_ID = {cate}")


def duplicate_title(url):
    res = dbhelper.fetch_one(
        "select count(*) as num from zbp_words where url = '" + url + "'")
    if res and res['num'] > 0:
        return True
    return False


class zzspider(scrapy.Spider):
    name = 'zzspider'
    # allowed_domains = ['toutiao.com']
    start_urls = []

    def __init__(self, start_urls, cate, word, word_id):
        self.start_urls.extend(start_urls)
        self.cate = cate
        self.word = word
        self.word_id = word_id

        mems = dbhelper.fetch_all("select mem_ID from zbp_member")
        self.author = random.choice(mems)['mem_ID']

    def parse(self, response):
        soup = BeautifulSoup(response.text, "html.parser")
        result_jsons = soup.find_all('script', attrs={'data-for': 's-result-json'})
        result = []
        for rj in result_jsons:
            data = json.loads(rj.text)
            if data.__contains__("data"):
                d = data['data']
                if d.__contains__('display_type_self') and (
                        d['display_type_self'] == 'self_article' or d['display_type_self'] == 'self_step_or_list'):
                    index = 0
                    if data.__contains__("extraData"):
                        extra = data['extraData']
                        if extra.__contains__("index"):
                            index = extra['index']
                    item = {'title': d['title'], 'source_url': d['source_url'], 'comment_count': d['comment_count'],
                            'index': index}
                    result.append(item)
        result = sorted(result, key=lambda i: i['index'])
        if len(result) == 0:
            return
        item = random.choice(result)
        article_url = item['source_url']
        title = item['title']

        title_list = re.split(sentence_pattern, title)

        for item in title_list:
            if item and len(item) > 0:
                title = item
                break

        if duplicate_title(article_url):
            return

        title = f"{self.word}({title})"
        print(article_url)
        print(title)
        # return
        # article_url = 'http://www.toutiao.com/a6406080444747825409/?channel=&source=search_tab'
        # title = '家有阳台看过来，注意这个小细节，锦上添花！'
        yield scrapy.Request(url=article_url, dont_filter=True, meta={'title': title},
                             callback=self.article)

    def article(self, response):
        title = response.meta['title']
        soup = BeautifulSoup(response.text, "html.parser")
        data = soup.find_all('article')[0]
        contents = data.find_all(['img', 'p'])
        content_str = ''
        for item in contents:
            if not item.text:
                continue
            if len(item.find_all(['img', 'a'])) > 0:
                continue
            if item.name == 'img':
                content_str += '<p>' + str(item) + '</p>'
                continue
            for i in item.find_all(attrs={'class': True}):
                del i['class']
            leap_flag = False
            for f in ConfigUtil.config['collect']['filter'].split(','):
                if str(item).__contains__(f):
                    leap_flag = True
                    break
            if not leap_flag:
                content_str += str(item)
        imgs = data.find_all('img')

        img_temp = list(set([item.attrs['src'] for item in imgs]))

        upload_count = 0
        for src in img_temp:
            result = urllib.request.urlretrieve(src)
            if result and len(result) > 0:
                temp_path = result[0]
                suffix = guess_extension(result[1].get_content_type().partition(';')[0].strip())
            else:
                logger.error("下载图片异常:" + src)
                continue
            now = datetime.datetime.now()
            filename = str(now.year) + str(now.month) + str(now.day) + str(round(time.time() * 1000)) + suffix
            relate_path = os.path.join(str(now.year), str(now.month), filename)
            real_path = os.path.join(settings.UPLOAD_PATH, relate_path)

            dirs = os.path.dirname(real_path)
            if not os.path.exists(dirs):
                os.makedirs(dirs)
            with open(temp_path, 'rb') as of:
                file = of.read()
                with open(real_path, 'wb') as new_file:
                    new_file.write(file + b'\0')
            os.remove(temp_path)

            linux_relate_path = f"/zb_users/upload/{str(now.year)}/{str(now.month)}"
            #sftp.upload_to_dir(real_path, ConfigUtil.config['sftp']['path'] + linux_relate_path)
            self.insert_upload(real_path)
            upload_count += 1
            content_str = content_str.replace(src, linux_relate_path + f"/{filename}")
        self.update_upload_count(upload_count)
        print("result:")
        print(content_str)

        self.insert_post(title, content_str, data.text, response.url)

    def insert_post(self, title, content_str, pure_text, url):
        pure_text = pure_text.replace('\'', '\\\'')
        intro = pure_text[0:150]

        now_time = int(round(time.time()))
        content_str = content_str.replace('\'', '\\\'')
        result = dbhelper.execute(
            f"INSERT INTO `zbp_post`(`log_CateID`, `log_AuthorID`, `log_Tag`, `log_Status`, `log_Type`, `log_Alias`, `log_IsTop`, `log_IsLock`, `log_Title`, `log_Intro`, `log_Content`, `log_CreateTime`, `log_PostTime`, `log_UpdateTime`, `log_CommNums`, `log_ViewNums`, `log_Template`, `log_Meta`) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
            [self.cate, self.author, '', 0, 0, '', 0, 1, title, intro, content_str, now_time,
             now_time,
             now_time, 0,
             0, '', ''])
        if result:
            after_insert_post(self.word_id, self.author, self.cate, url)

    def insert_upload(self, real_path):
        kind = filetype.guess(real_path)
        head, tail = os.path.split(real_path)
        dbhelper.execute(
            f"INSERT INTO `zbp_upload`(`ul_AuthorID`, `ul_Size`, `ul_Name`, `ul_SourceName`, `ul_MimeType`, `ul_PostTime`, `ul_DownNums`, `ul_LogID`, `ul_Intro`, `ul_Meta`) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
            [self.author, int(os.path.getsize(real_path)), tail, tail, str(kind.mime), int(round(time.time())), 0, 0,
             '', ''])

    def update_upload_count(self, upload_count):
        dbhelper.execute(
            f"update zbp_member set mem_Uploads = mem_Uploads + {upload_count}, mem_UpdateTime = {int(round(time.time()))} where mem_ID = {self.author}")
