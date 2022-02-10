import json
import logging
import os
import random
import time
import urllib.parse
from logging.handlers import TimedRotatingFileHandler

import requests
from baiduspider import BaiduSpider
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from zzspider import settings
from zzspider.config import ConfigUtil
from zzspider.spiders.zzspider import zzspider
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

cates = ConfigUtil.config['collect']['cate'].split(',')
baiduspider = BaiduSpider()


def get_start_urls(cate):
    sql = 'SELECT id, `word` FROM `zbp_words` WHERE `cate` = %s and `used` = 0 limit 1'
    word = dbhelper.fetch_one(sql, [cate])
    timestamp = time.time()
    word['word'] = word['word'].replace(" ", "")
    start_word = word['word']
    title = word['word']
    down_words = []
    url_word = urllib.parse.unquote(start_word)
    res = requests.get(
        f"https://www.baidu.com/sugrec?pre=1&p=3&ie=utf-8&json=1&prod=pc&from=pc_web&wd={url_word}",
        verify=False)
    try:
        if res.ok:
            res_json = json.loads(res.text)
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

    s_word = urllib.parse.quote(start_word, "utf-8")
    baidu_url = f"https://www.baidu.com/s?wd={s_word}&pn=0&inputT={random.randint(500, 4000)}"

    # # 相关搜索
    # result_all = baiduspider.search_web(start_word, 1,
    #                                     ['news', 'video', 'baike', 'tieba', 'blog', 'gitee', 'calc', 'music'])
    # print(len(result_all.related))
    # exit(0)
    # if title in result_all.related:
    #     result_all.related.remove(title)
    # sub_title = get_best_word(start_word, result_all.related)
    return [baidu_url], start_word, title, url, word['id']


def filter_duplicate(urlss, w):
    res = dbhelper.fetch_one(
        "select count(*) as num from zbp_words where url = '" + urlss[0] + "'")
    if res['num'] == 0:
        dbhelper.execute(f"insert into zbp_words (`word`) values ('{w}')")
        return_id = dbhelper.cur.lastrowid
        return urlss, return_id
    return None, None


if __name__ == '__main__':
    process = CrawlerProcess(install_root_handler=False, settings=get_project_settings())
    if ConfigUtil.config['collect']['special_url']:
        cate = int(ConfigUtil.config['collect']['special_cate'])
        start_urls = [ConfigUtil.config['collect']['special_url']]
        start_word = ConfigUtil.config['collect']['special_title']
        word = ConfigUtil.config['collect']['special_title']
        if start_word is None or start_word == '':
            start_word = str(round(time.time() * 1000))
        start_urls, word_id = filter_duplicate(start_urls, start_word)
        if start_urls is None:
            exit(0)
        url = None
    else:
        cate = random.choice(cates)
        start_urls, start_word, word, url, word_id = get_start_urls(cate)
    process.crawl(zzspider, start_urls=start_urls, cate=cate, start_word=start_word, word=word, toutiao_url=url,
                  word_id=word_id)
    process.start()
