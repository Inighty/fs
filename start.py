import datetime
import json
import logging
import os
import random
import time
import urllib.parse
from logging.handlers import TimedRotatingFileHandler

import requests
from baiduspider import BaiduSpider
from bs4 import BeautifulSoup
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from twisted.internet import reactor
from twisted.internet.task import deferLater

from zzspider import settings
from zzspider.config import ConfigUtil
from zzspider.spiders.zzspider import zzspider
from zzspider.tools.browser import Browser
from zzspider.tools.dbhelper import DBHelper
from zzspider.tools.same_word import get_best_word

logger = logging.getLogger(__name__)

log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
if not os.path.exists(log_path):
    os.mkdir(log_path)
logHandler = TimedRotatingFileHandler(
    os.path.join(log_path, 'error.log'), when='MIDNIGHT', encoding='utf-8')
logHandler.setLevel(settings.LOG_LEVEL)
logHandler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
logging.getLogger().handlers = [logHandler]
dbhelper = DBHelper()
sleep_time = int(ConfigUtil.config['main']['sleep'])
start_hour = ConfigUtil.config['main']['start_hour'].split(',')
start_hour.sort()
end_hour = ConfigUtil.config['main']['end_hour'].split(',')
end_hour.sort()
cates = ConfigUtil.config['collect']['cate'].split(',')
baiduspider = BaiduSpider()


def baidu_relate(start_word, relate_arr):
    if (len(relate_arr) > 0):
        return
    result_all = baiduspider.search_web(start_word, 1,
                                        ['news', 'video', 'baike', 'tieba', 'blog', 'gitee', 'calc', 'music'])
    if len(result_all.related) == 0:
        text = urllib.parse.quote(start_word, "utf-8")
        url = f"https://www.baidu.com/s?wd={text}&pn=0&inputT={random.randint(500, 4000)}"
        res = Browser().get(url)
        soup = BeautifulSoup(res, "html.parser")
        _related = soup.findAll("table")[-1].findAll("td")
        if len(_related) != 0:
            relate_arr.extend([item.text.strip() for item in _related])
    else:
        relate_arr.extend(result_all.related)


def bing_relate(start_word, relate_arr):
    if (len(relate_arr) > 0):
        return
    url_word = urllib.parse.quote(start_word)
    bing_url = u'{}/search?q={}&search=&form=QBLH'.format('https://cn.bing.com', url_word)
    result = requests.get(bing_url)
    if result.status_code == 200:
        tags = BeautifulSoup(result.text, "html.parser")
        rs = tags.find('div', {'class': 'b_rs'})
        if rs is not None:
            relate_arr.extend([item.text for item in rs.find_all('li')])


def process_relate(start_word):
    relate_arr = []
    if random.random() < .5:
        baidu_relate(start_word, relate_arr)
        bing_relate(start_word, relate_arr)
    else:
        bing_relate(start_word, relate_arr)
        baidu_relate(start_word, relate_arr)
    return relate_arr


def get_start_urls(cate):
    sql = 'SELECT id, `word` FROM `zbp_words` WHERE `cate` = %s and `used` = 0 limit 1'
    word = dbhelper.fetch_one(sql, [cate])
    if word is None or word['word'] is None or word['word'] == '':
        return None, None, None, None, None
    dbhelper.execute(f"update zbp_words set used = 1 where id = {word['id']}")
    timestamp = time.time()
    word['word'] = word['word'].replace(" ", "")
    # word['word'] = "盖房子高低风水"
    start_word = word['word']
    title = word['word']
    down_words = []
    url_word = urllib.parse.quote(start_word)
    res = requests.get(
        f"https://www.baidu.com/sugrec?pre=1&p=3&ie=utf-8&json=1&prod=pc&from=pc_web&wd={url_word}",
        verify=False)
    try:
        if res.ok:
            logger.error("baidu drop:" + res.text)
            res_json = json.loads(res.text)
            if 'g' in res_json:
                for item in res_json['g']:
                    down_words.append(item['q'])
                best_word = get_best_word(start_word, down_words)
                if best_word is not None:
                    title = best_word
    except Exception as e:
        logger.error(e)
        pass
    finally:
        res.close()

    url = f"""https://so.toutiao.com/search?dvpf=pc&source=input&keyword={title}&filter_vendor=site&index_resource=site&filter_period=all&min_time=0&max_time={timestamp}"""

    relate_arr = process_relate(start_word)
    time_num = 0
    while len(relate_arr) == 0 and time_num < 15:
        relate_arr = process_relate(start_word)
        time_num += 1
        time.sleep(1)
    if len(relate_arr) > 0:
        if title in relate_arr:
            relate_arr.remove(title)
        sub_title = get_best_word(start_word, relate_arr, None)
        if sub_title is None:
            logger.error(start_word + ",sub_title none.")
            return None, None, None, None, word['id']
    else:
        logger.error(start_word + ",relate none than 15.")
        return [url], start_word, title, None, word['id']
    return [url], start_word, title, sub_title, word['id']


def filter_duplicate(urlss, w):
    res = dbhelper.fetch_one(
        "select count(*) as num from zbp_words where url = '" + urlss[0] + "'")
    if res['num'] == 1:
        dbhelper.execute(f"insert into zbp_words (`word`) values ('{w}')")
        return_id = dbhelper.cur.lastrowid
        return urlss, return_id
    return None, None


def sleep(self, *args, seconds):
    """Non blocking sleep callback"""
    return deferLater(reactor, seconds, lambda: None)


def _crawl(result, spider):
    cate = random.choice(cates)
    start_urls, start_word, word, word_sub, word_id = get_start_urls(cate)
    while word is None:
        if word_id is not None:
            dbhelper.execute(f"update zbp_words set used = 0 where id = {word_id}")
        cate = random.choice(cates)
        start_urls, start_word, word, word_sub, word_id = get_start_urls(cate)
    deferred = process.crawl(zzspider, start_urls=start_urls, cate=cate, start_word=start_word, word=word,
                             word_sub=word_sub,
                             word_id=word_id)
    range_seconds = sleep_time
    now = datetime.datetime.now()
    if str(now.hour) in end_hour:
        logger.error("当前时间：" + str(now.hour))
        # 计算距离下次执行时间
        nextFlag = True
        for st in start_hour:
            st = int(st)
            if st > now.hour:
                # 找到下次开启的时间
                nextFlag = False
                diff = now.hour - st
                range_seconds = diff * 3600
                logger.error("找到下次开启的时间：" + str(range_seconds) + "秒")
                break
        if nextFlag:
            # 跨天
            st = int(start_hour[0])
            diff = 24 - now.hour + st
            range_seconds = diff * 3600
            logger.error("找到下次跨天开启的时间：" + str(range_seconds) + "秒")
    deferred.addCallback(sleep, seconds=range_seconds)
    deferred.addCallback(_crawl, spider)
    return deferred


if __name__ == '__main__':
    process = CrawlerProcess(install_root_handler=False, settings=get_project_settings())
    if ConfigUtil.config['collect']['special_url']:
        cate = int(ConfigUtil.config['collect']['special_cate'])
        start_urls = [ConfigUtil.config['collect']['special_url']]
        start_word = ConfigUtil.config['collect']['special_title']
        word = ConfigUtil.config['collect']['special_title']
        word_sub = None
        if start_word is None or start_word == '':
            start_word = str(round(time.time() * 1000))
        start_urls, word_id = filter_duplicate(start_urls, start_word)
        if start_urls is None:
            exit(0)
    else:
        _crawl(None, zzspider)
    process.start()
