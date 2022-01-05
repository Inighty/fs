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
import requests
import scrapy
from bs4 import BeautifulSoup
from scrapy import Request

from zzspider import settings
from zzspider.config import ConfigUtil
from zzspider.tools.browser import Browser
from zzspider.tools.dbhelper import DBHelper
from zzspider.tools.img import img_to_progressive
from zzspider.tools.sftp import Sftp

browser = Browser()
dbhelper = DBHelper()
sftp = Sftp()
logger = logging.getLogger(__name__)
sentence_pattern = r',|\.|/|;|\'|`|\[|\]|<|>|\?|:|：|"|\{|\}|\~|!|@|#|\$|%|\^|&|？|\(|\)|-|=|\_|\+|，|。|、|；|‘|’|【|】|·|！| |…|（|）'
sitemap_path = ConfigUtil.config['main']['sitemap_path']


def baidu_push():
    basedir = os.path.dirname(os.path.realpath('__file__'))
    remainpath = os.path.join(basedir, 'baidu.remain')
    if os.path.exists(remainpath):
        mtime = os.path.getmtime(remainpath)
        mday = int(time.strftime("%d", time.localtime(mtime)))
        if mday == datetime.date.today().day:
            # 当天
            with open(remainpath, 'r', encoding='utf-8') as f:
                remain = int(f.read())
                if remain == 0:
                    return
        else:
            # 非当天
            remain = 3000
    else:
        remain = 3000
    if remain > 0:
        id = dbhelper.fetch_one(f"select log_ID from zbp_post order by log_ID desc limit 1")
        id = id['log_ID']
        push_url = 'http://data.zz.baidu.com/urls?site=' + ConfigUtil.config['main']['url'] + '&token=' + \
                   ConfigUtil.config['main']['baidu_push_token']
        url = ConfigUtil.config['main']['url'] + f"/s/{id}.html"
        response = requests.post(push_url, data=url)
        res_dict = json.loads(response.text)

        if response.status_code == 400:
            # 超出 不应该走到这
            print("push overflow.")
            pass
        else:
            remain = res_dict['remain']
            # 推送成功
            with open(remainpath, 'w', encoding='utf-8') as f:
                f.write(str(remain))


def after_insert_post(word_id, author, cate, url):
    dbhelper.execute(f"update zbp_words set used = 1, url = '{url}' where id = {word_id}")
    dbhelper.execute(
        f"update zbp_member set mem_Articles = mem_Articles + 1, mem_PostTime = {int(round(time.time()))} where mem_ID = {author}")
    dbhelper.execute(
        f"update zbp_category set cate_Count = cate_Count + 1 where cate_ID = {cate}")
    if os.path.exists(sitemap_path):
        os.remove(sitemap_path)
    baidu_push()


def duplicate_title(result):
    f = None
    for item in result:
        url = item['source_url']
        title = item['title']
        leap_flag = False
        for f in ConfigUtil.config['collect']['title_filter'].split(','):
            if title.__contains__(f):
                leap_flag = True
                break
        if leap_flag:
            continue
        res = dbhelper.fetch_one(
            "select count(*) as num from zbp_words where url = '" + url + "'")
        if res['num'] == 0:
            f = item
            break
    return f


class zzspider(scrapy.Spider):
    name = 'zzspider'
    # allowed_domains = ['toutiao.com']
    start_urls = []

    def __init__(self, start_urls, cate, word, word_id):
        self.start_urls.extend(start_urls)
        self.cate = cate
        self.word = word
        self.word_id = word_id
        logger.error(self.word)
        mems = dbhelper.fetch_all("select mem_ID from zbp_member")
        self.author = random.choice(mems)['mem_ID']

    def parse(self, response):
        first_title = self.word
        # 百度下拉
        # res = requests.get(
        #     "https://sp0.baidu.com/5a1Fazu8AA54nxGko9WTAnF6hhy/su?json=1&bs=s&wd=" + self.word, verify=False)
        # try:
        #     if res.ok:
        #         res_json = json.loads(res.text[17: -2])
        #         for item in res_json['s']:
        #             if item.startswith(self.word):
        #                 first_title = item
        #                 break
        # except Exception as e:
        #     logger.error(e)
        #     pass
        # finally:
        #     res.close()

        # print("获取到结果：" + response.text)
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
            logger.error(f"关键词{self.word}没有东西")
            if len(result_jsons) > 0:
                dbhelper.execute(f"update zbp_words set used = 1 where id = {self.word_id}")
            return

        item = duplicate_title(result)
        if item is None:
            # 翻页
            pages = soup.find_all('div', attrs={'class': 'cs-pagination'})
            if pages and len(pages) > 0:
                aa = pages[0].find_all('a')
                last_href = "https://so.toutiao.com" + aa[len(aa) - 1]['href']
                yield scrapy.Request(url=last_href, dont_filter=True, callback=self.parse)
            return
        article_url = item['source_url']
        title = item['title']

        title_list = re.split(sentence_pattern, title)
        for item in title_list:
            if item and len(item) > 0:
                title = item
                break

        # if duplicate_title(article_url):
        #   return

        title = f"{first_title}({title})"
        logger.error(article_url)
        logger.error(title)
        # return
        # article_url = 'http://www.toutiao.com/a6696692803763700232/?channel=&source=search_tab'
        # title = '家有阳台看过来，注意这个小细节，锦上添花！'
        yield scrapy.Request(url=article_url, dont_filter=True, meta={'title': title},
                             callback=self.article)

    def article(self, response):
        # print("获取到文章内容")
        title = response.meta['title']
        soup = BeautifulSoup(response.text, "html.parser")
        for tag in soup():
            for attribute in ["class", "style"]:
                del tag[attribute]
        data = soup.find_all('article')[0]
        imgs = data.find_all('img')
        img_temp = list(set([item.attrs['src'] for item in imgs]))
        contents = data.find_all(['img', 'p'])
        content_str = ''
        for item in contents:
            dels = item.find_all(['img', 'a'])
            if len(dels) > 0:
                for d in dels:
                    d.extract()
            if item.name == 'img':
                item['class'] = 'syl-page-img aligncenter j-lazy'
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

        upload_count = 0
        for src in img_temp:
            result = urllib.request.urlretrieve(src)
            if result and len(result) > 0:
                temp_path = result[0]
                content_type = result[1].get_content_type().partition(';')[0].strip()
                if content_type == 'image/webp':
                    suffix = '.webp'
                else:
                    suffix = guess_extension(content_type)
                logger.error(content_type)
                logger.error(suffix)

                if suffix == '.jpe':
                    suffix = '.jpg'
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

            img_to_progressive(real_path)

            linux_relate_path = f"/zb_users/upload/{str(now.year)}/{str(now.month)}"
            # sftp.upload_to_dir(real_path, ConfigUtil.config['sftp']['path'] + linux_relate_path)
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
