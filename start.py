import datetime
import json
import logging
import os
import platform
import random
import re
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
from zzspider.tools.dbhelper import DBHelper
from zzspider.tools.image_bed import upload
from zzspider.tools.proxyip import get_proxies
from zzspider.tools.same_word import get_best_word, get_real_arr
from zzspider.tools.timeout_err import timeout_error

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
start_hour = [int(numeric_string) for numeric_string in start_hour]
start_hour.sort()
end_hour = ConfigUtil.config['main']['end_hour'].split(',')
end_hour = [int(numeric_string) for numeric_string in end_hour]
end_hour.sort()
cates = ConfigUtil.config['collect']['cate'].split(',')
thread_size = int(ConfigUtil.config['main']['thread_size'])
baiduspider = BaiduSpider()


def baidu_relate(start_word, relate_arr):
    logger.error("baidu relate start")
    if (len(relate_arr) > 0):
        return
    time_num = 0

    proxy = get_proxies()
    while len(relate_arr) == 0 and time_num < 100:
        try:
            proxy_ip = {
                "http": proxy,  # HTTP代理
                "https": proxy  # HTTPS代理
            }
            logger.error("baidu relate time:" + str(time_num))
            if platform.system() == 'Windows':
                result_all = baiduspider.search_web(start_word, 1,
                                                    ['news', 'video', 'baike', 'tieba', 'blog', 'gitee', 'calc',
                                                     'music'],
                                                    proxies=proxy_ip)
            else:
                with timeout_error(seconds=10):
                    result_all = baiduspider.search_web(start_word, 1,
                                                        ['news', 'video', 'baike', 'tieba', 'blog', 'gitee', 'calc',
                                                         'music'],
                                                        proxies=proxy_ip)
            logger.error("baidu relate search done:")
            if len(result_all.related) > 0:
                if len(result_all.related) == 1 and (
                        len(result_all.related[0]) > 300 or len(result_all.related[0]) == 0):
                    break
                else:
                    relate_arr.extend(result_all.related)
            else:
                time_num += 1
        except Exception as e:
            proxy = get_proxies()
            logger.error(e)
            pass
    logger.error("baidu relate end")


def bing_relate(start_word, relate_arr):
    logger.error("bing relate start")
    if (len(relate_arr) > 0):
        return
    url_word = urllib.parse.quote(start_word)
    bing_url = u'{}/search?q={}&search=&form=QBLH'.format('https://cn.bing.com', url_word)
    result = requests.get(bing_url, verify=False, timeout=5)
    if result.status_code == 200:
        tags = BeautifulSoup(result.text, "html.parser")
        rs = tags.find('ol', {'id': 'b_results'})
        if rs is not None:
            lis = rs.find_all('li')
            for item in lis:
                if item.text.__contains__('没有与此相关的结果'):
                    return
                else:
                    if item.find('h2') is not None:
                        reals = re.search("^(.*?)[!@#$%^&*()_\-+=<>?:\"{}|,.\/;'\\[\]·~！￥…（）—《》？：“”、；‘，。]", item.find('h2').text)
                        if reals is not None and len(reals.groups()) > 1:
                            real = reals.group(1)
                            relate_arr.append(real)
    logger.error("bing relate end")


def process_relate(start_word):
    relate_arr = []
    # if random.random() < .5:
    baidu_relate(start_word, relate_arr)
    bing_relate(start_word, relate_arr)
    # else:
    #     bing_relate(start_word, relate_arr)
    #     baidu_relate(start_word, relate_arr)
    return relate_arr


def get_start_urls(cate):
    sql = 'SELECT id, `word` FROM `zbp_words` WHERE `cate` = %s and `used` = 0 order by id desc limit 1'
    word = dbhelper.fetch_one(sql, [cate])
    print(word)
    if word is None or word['word'] is None or word['word'] == '':
        return None, None, None, None, None
    dbhelper.execute(f"update zbp_words set used = 1 where id = {word['id']}")
    timestamp = time.time()
    word['word'] = word['word'].replace(" ", "")
    # word['word'] = "办理学位证书"
    start_word = word['word']
    title = word['word']
    down_words = []
    url_word = urllib.parse.quote(start_word)
    res = None
    try:
        res = requests.get(
            f"https://www.baidu.com/sugrec?pre=1&p=3&ie=utf-8&json=1&prod=pc&from=pc_web&wd={url_word}",
            verify=False)
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
        if res is not None:
            res.close()

    url = f"""https://so.toutiao.com/search?dvpf=pc&source=input&keyword={title}&filter_vendor=site&index_resource=site&filter_period=all&min_time=0&max_time={timestamp}"""

    relate_arr = process_relate(start_word)
    if len(relate_arr) > 0:
        if title in relate_arr:
            relate_arr.remove(title)
        real_relate = get_real_arr(title, relate_arr)
        sub_title = get_best_word(start_word, real_relate, None)
        if sub_title is None:
            return None, None, None, None, word['id']
    else:
        return [url], start_word, title, None, word['id']
    return [url], start_word, title, sub_title, word['id']


def filter_duplicate(urlss, w):
    res = dbhelper.fetch_one(
        "select count(*) as num from zbp_words where url = '" + urlss[0] + "'")
    if res['num'] == 0:
        dbhelper.execute(f"insert into zbp_words (`word`) values ('{w}')")
        return_id = dbhelper.cur.lastrowid
        return urlss, return_id
    return None, None


def sleep(self, *args, seconds):
    """Non blocking sleep callback"""
    print("sleep time: " + str(seconds) + "s")
    return deferLater(reactor, seconds, lambda: None)


def _crawl(result, spider, name=None):
    cate = random.choice(cates)
    print("cate" + str(cate))
    start_urls, start_word, word, word_sub, word_id = get_start_urls(cate)
    while word is None:
        if word_id is not None:
            dbhelper.execute(f"update zbp_words set used = 0 where id = {word_id}")
        cate = random.choice(cates)
        start_urls, start_word, word, word_sub, word_id = get_start_urls(cate)
    deferred = process.crawl(zzspider, start_urls=start_urls, cate=cate, start_word=start_word, word=word,
                             word_sub=word_sub,
                             word_id=word_id,
                             name=name)
    range_seconds = sleep_time
    now = datetime.datetime.now()
    if now.hour in end_hour:
        logger.error("当前时间：" + str(now.hour))
        # 计算距离下次执行时间
        nextFlag = True
        for st in start_hour:
            if st > now.hour:
                # 找到下次开启的时间
                nextFlag = False
                diff = abs(now.hour - st)
                range_seconds = diff * 3600
                logger.error("找到下次开启的时间：" + str(range_seconds) + "秒")
                break
        if nextFlag:
            # 跨天
            # st = start_hour[0]
            # diff = abs(24 - now.hour + st)
            # range_seconds = diff * 3600
            # logger.error("找到下次跨天开启的时间：" + str(range_seconds) + "秒")
            exit(0)
    deferred.addCallback(sleep, seconds=range_seconds)
    deferred.addCallback(_crawl, spider, name)
    return deferred


def g404():
    base_url = "https://www.baikexueshe.com/zb_users/upload/"
    dbhelper = DBHelper()
    images = dbhelper.fetch_all("select `ul_Name` from zbp_upload")
    all_url = []
    for item in images:
        name = item['ul_Name']
        year = name[:4]
        month = name[4:6]
        url = base_url + year + '/' + month + '/' + name
        all_url.append(url)
    lists = [all_url[i:i + 50000] for i in range(0, len(all_url), 50000)]
    index = 0
    for list in lists:
        with open(str(index) + '-404.txt', 'w', encoding='utf-8') as f:
            f.write("\n".join(list))
        index += 1


def process_upload():
    dbhelper = DBHelper()
    while True:
        posts = dbhelper.fetch_all(
            "select log_ID,log_Content from zbp_post where log_Content like '%src=\"{#ZC_BLOG_HOST#}%' limit 20")
        if posts is not None and len(posts) != 0:
            for post in posts:
                logger.error("start upload! post_id:" + str(post['log_ID']))
                content = post['log_Content']
                searches = re.findall('src=\"{#ZC_BLOG_HOST#}(.*?)\"', content)
                searches = set(searches)
                for old_url in searches:
                    real_path = ConfigUtil.config['main']['path'] + '/' + old_url
                    if not os.path.exists(real_path):
                        logger.error("image not found,real_path:" + real_path)
                        continue
                    new_url = upload(real_path)
                    if new_url is None:
                        continue
                    filename = os.path.basename(real_path)
                    dbhelper.execute(
                        f"UPDATE `zbp_upload` set `ul_TcPath` = %s,`ul_LogID` = %s where ul_SourceName = %s and ul_TcPath is null",
                        [new_url, post['log_ID'], filename])
                    content = content.replace('{#ZC_BLOG_HOST#}' + old_url, new_url)
                dbhelper.execute(
                    f"UPDATE `zbp_post` set `log_Content` = %s where log_ID = %s",
                    [content, post['log_ID']])
                logger.error("update complete! post_id:" + str(post['log_ID']))
        else:
            break


def process_upload_ys():
    dbhelper = DBHelper()
    while True:
        posts = dbhelper.fetch_all(
            "select vod_id,vod_pic from mac_vod where vod_pic like 'upload%' limit 20")
        if posts is not None and len(posts) != 0:
            for post in posts:
                real_path = '/home/wwwroot/www.ysys.tv/' + post['vod_pic']
                if not os.path.exists(real_path):
                    logger.error("image not found,real_path:" + real_path)
                    continue
                new_url = upload(real_path)
                if new_url is None:
                    continue
                new_url = new_url.replace("https://", "mac://")
                dbhelper.execute(
                    f"UPDATE `mac_vod` set `vod_pic` = %s where vod_id = %s",
                    [new_url, post['vod_id']])
                time.sleep(random.randint(1, 5))
        else:
            break


if __name__ == '__main__':
    if ConfigUtil.config['collect']['cate'] == '404':
        g404()
        exit(0)
    if ConfigUtil.config['collect']['cate'] == 'upload':
        process_upload()
        exit(0)
    if ConfigUtil.config['collect']['cate'] == 'uploadys':
        process_upload_ys()
        exit(0)
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
        process.crawl(zzspider, start_urls=start_urls, cate=cate, start_word=start_word, word=word,
                      word_sub=word_sub,
                      word_id=word_id)
    else:
        for item in range(1, thread_size):
            _crawl(None, zzspider, "spider" + str(item))
    process.start()
