import json
import logging
import os
import random
import time
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

    real_word = word['word']

    down_words = []
    res = requests.get(
        "https://sp0.baidu.com/5a1Fazu8AA54nxGko9WTAnF6hhy/su?json=1&bs=s&wd=" + real_word, verify=False)
    try:
        if res.ok:
            res_json = json.loads(res.text[17: -2])
            down_words.extend(item for item in res_json['s'])
            best_word = get_best_word(real_word, down_words)
            if best_word is not None:
                real_word = best_word
    except Exception as e:
        logger.error(e)
        pass
    finally:
        res.close()

    url = f"""https://so.toutiao.com/search?dvpf=pc&source=input&keyword={real_word}&filter_vendor=site&index_resource=site&filter_period=all&min_time=0&max_time={timestamp}"""

    # 相关搜索
    result_all = baiduspider.search_web(word['word'], 1,
                                        ['news', 'video', 'baike', 'tieba', 'blog', 'gitee', 'calc', 'music'])
    sub_title = get_best_word(word['word'], result_all.related)
    real_title = f"{real_word}({sub_title})"
    return [url], real_title, word['id']


def filter_duplicate(urlss, w):
    res = dbhelper.fetch_one(
        "select count(*) as num from zbp_words where url = '" + urlss[0] + "'")
    if res['num'] == 0:
        dbhelper.execute(f"insert into zbp_words (`word`,`url`) values ('{w}', '{urlss[0]}')")
        return_id = dbhelper.cur.lastrowid
        return urlss, return_id
    return None, None


if __name__ == '__main__':
    process = CrawlerProcess(install_root_handler=False, settings=get_project_settings())
    if ConfigUtil.config['collect']['special_url']:
        cate = int(ConfigUtil.config['collect']['special_cate'])
        start_urls = [ConfigUtil.config['collect']['special_url']]
        word = ConfigUtil.config['collect']['special_title']
        start_urls, word_id = filter_duplicate(start_urls, word)
        if start_urls is None:
            exit(0)
    else:
        cate = random.choice(cates)
        start_urls, word, word_id = get_start_urls(cate)
    process.crawl(zzspider, start_urls=start_urls, cate=cate, word=word, word_id=word_id)
    process.start()
