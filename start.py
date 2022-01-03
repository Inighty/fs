import datetime
import logging
import os
import random
import re
import sys
import time
from logging.handlers import TimedRotatingFileHandler
from mimetypes import guess_extension

import filetype
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from zzspider import settings
from zzspider.config import ConfigUtil
from zzspider.spiders.zzspider import zzspider
from zzspider.tools.dbhelper import DBHelper
from zzspider.tools.img import img_to_progressive

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
import urllib.request

cates = ConfigUtil.config['collect']['cate'].split(',')


def get_start_urls(cate):
    sql = 'SELECT id, `word` FROM `zbp_words` WHERE `cate` = %s and `used` = 0 limit 1'
    word = dbhelper.fetch_one(sql, [cate])
    timestamp = time.time()
    url = f"""https://so.toutiao.com/search?dvpf=pc&source=input&keyword={word['word']}&filter_vendor=site&index_resource=site&filter_period=all&min_time=0&max_time={timestamp}"""
    return [url], word['word'], word['id']


def process_img(img_temp, content, author):
    for src in img_temp:
        result = urllib.request.urlretrieve(src)
        if result and len(result) > 0:
            temp_path = result[0]
            suffix = guess_extension(result[1].get_content_type().partition(';')[0].strip())
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

        linux_relate_path = f"/zb_users/upload/{str(now.year)}/{str(now.month)}"
        # sftp.upload_to_dir(real_path, ConfigUtil.config['sftp']['path'] + linux_relate_path)
        kind = filetype.guess(real_path)
        head, tail = os.path.split(real_path)
        dbhelper.execute(
            f"INSERT INTO `zbp_upload`(`ul_AuthorID`, `ul_Size`, `ul_Name`, `ul_SourceName`, `ul_MimeType`, `ul_PostTime`, `ul_DownNums`, `ul_LogID`, `ul_Intro`, `ul_Meta`) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
            [author, int(os.path.getsize(real_path)), tail, tail, str(kind.mime), int(round(time.time())), 0, 0,
             '', ''])
        content = content.replace(src, linux_relate_path + f"/{filename}")
    return content

regex = r"src=\"(http.*?)\""

def repair():
    result = []
    sql = 'SELECT log_ID,log_Content,log_AuthorID FROM `zbp_post` WHERE log_Type = 0'
    posts = dbhelper.fetch_all(sql)
    for post in posts:
        id = post['log_ID']
        author = post['log_AuthorID']
        content = post['log_Content']
        if content.__contains__('toutiaoimg'):
            matches = re.finditer(regex, post['log_Content'])
            for match in matches:
                src = match.group(1)
                result.append(src)
            content = process_img(result, content, author)
            dbhelper.execute(f"update zbp_post set log_Content = '{content}' where log_ID = {id}")


if __name__ == '__main__':
    arg = sys.argv
    if len(arg) > 1:
        if arg[1] == 'repair':
            repair()
        elif arg[1] == 'compress':
            for d, _, fl in os.walk(ConfigUtil.config['main']['path'] + '/zb_users/upload'):  # 遍历目录下所有文件
                for f in fl:
                    try:
                        img_to_progressive(d + '\\' + f)
                    except Exception as e:
                        print(e)
                        pass
        exit(0)
    # for i in range(0, count):
    cate = random.choice(cates)
    process = CrawlerProcess(install_root_handler=False, settings=get_project_settings())
    start_urls, word, word_id = get_start_urls(cate)
    process.crawl(zzspider, start_urls=start_urls, cate=cate, word=word, word_id=word_id)
    process.start()
