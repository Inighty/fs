import logging
import os
import random
import sys
import time
from logging.handlers import TimedRotatingFileHandler

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
    url = f"""https://so.toutiao.com/search?dvpf=pc&source=input&keyword={word['word']}&filter_vendor=site&index_resource=site&filter_period=all&min_time=0&max_time={timestamp}"""
    return [url], word['word'], word['id']


if __name__ == '__main__':
    count = 1
    arg = sys.argv
    if len(arg) > 1:
        count = int(arg[1])

    for i in range(0, count):
        cate = random.choice(cates)
        process = CrawlerProcess(install_root_handler=False, settings=get_project_settings())
        start_urls, word, word_id = get_start_urls(cate)
        process.crawl(zzspider, start_urls=start_urls, cate=cate, word=word, word_id=word_id)
        process.start()
