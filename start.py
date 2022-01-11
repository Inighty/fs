import json
import logging
import os
import random
import time
from logging.handlers import TimedRotatingFileHandler

import requests
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from zzspider import settings
from zzspider.config import ConfigUtil
from zzspider.spiders.zzspider import zzspider
from zzspider.tools.dbhelper import DBHelper

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


def get_start_urls(cate):
    sql = 'SELECT id, `word` FROM `zbp_words` WHERE `cate` = %s and `used` = 0 limit 1'
    word = dbhelper.fetch_one(sql, [cate])
    timestamp = time.time()

    real_word = word['word']
    res = requests.get(
        "https://sp0.baidu.com/5a1Fazu8AA54nxGko9WTAnF6hhy/su?json=1&bs=s&wd=" + real_word, verify=False)
    try:
        if res.ok:
            res_json = json.loads(res.text[17: -2])
            for item in res_json['s']:
                real_word = item
                break
    except Exception as e:
        logger.error(e)
        pass
    finally:
        res.close()

    url = f"""https://so.toutiao.com/search?dvpf=pc&source=input&keyword={real_word}&filter_vendor=site&index_resource=site&filter_period=all&min_time=0&max_time={timestamp}"""
    return [url], real_word, word['id']


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
