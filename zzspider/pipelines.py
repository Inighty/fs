# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
from zzspider.tools.browser import Browser

browser = Browser()


# sftp = Sftp()


class PostPipeline:
    def process_item(self, item, spider):
        return item

    def close_spider(self, spider):
        # pass
        browser.quit()
        # browser.close()
        # sftp.close()
