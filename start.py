import logging
import os
import time
from logging.handlers import TimedRotatingFileHandler

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from zzspider import settings
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


def get_start_urls():
    sql = 'SELECT `word` FROM `zbp_words` WHERE `cate` = %s and `used` = 0 limit 1'
    word = dbhelper.fetch_one(sql, [1])
    timestamp = time.time()
    url = f"""https://so.toutiao.com/search?dvpf=pc&source=input&keyword={word['word']}&filter_vendor=site&index_resource=site&filter_period=all&min_time=0&max_time={timestamp}"""
    return [url]


process = CrawlerProcess(install_root_handler=False, settings=get_project_settings())
process.crawl(zzspider, start_urls=get_start_urls())
process.start()
