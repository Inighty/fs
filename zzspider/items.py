# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class PostItem(scrapy.Item):
    log_ID = scrapy.Field()
    log_CateID = scrapy.Field()
    log_AuthorID = scrapy.Field()
    log_Tag = scrapy.Field()
    log_Status = scrapy.Field()
    log_Type = scrapy.Field()
    log_Alias = scrapy.Field()
    log_IsTop = scrapy.Field()
    log_IsLock = scrapy.Field()
    log_Title = scrapy.Field()
    log_Intro = scrapy.Field()
    log_Content = scrapy.Field()
    log_CreateTime = scrapy.Field()
    log_PostTime = scrapy.Field()
    log_UpdateTime = scrapy.Field()
    log_CommNums = scrapy.Field()
    log_ViewNums = scrapy.Field()
    log_Template = scrapy.Field()
    log_Meta = scrapy.Field()


class UploadItem(scrapy.Item):
    ul_ID = scrapy.Field()
    ul_AuthorID = scrapy.Field()
    ul_Size = scrapy.Field()
    ul_Name = scrapy.Field()
    ul_SourceName = scrapy.Field()
    ul_MimeType = scrapy.Field()
    ul_PostTime = scrapy.Field()
    ul_DownNums = scrapy.Field()
    ul_LogID = scrapy.Field()
    ul_Intro = scrapy.Field()
    ul_Meta = scrapy.Field()
