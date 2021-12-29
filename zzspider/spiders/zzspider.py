# -*- coding: utf-8 -*-
import json
import os
import random
import time

import scrapy
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

basedir = os.path.dirname(os.path.realpath('__file__'))


class zzspider(scrapy.Spider):
    name = 'zzspider'
    allowed_domains = ['toutiao.com']
    start_urls = []

    def __init__(self, start_urls):
        self.start_urls.extend(start_urls)

    def parse(self, response):
        # instantiate a chrome options object so you can set the size and headless preference
        chrome_options = Options()
        chrome_options.add_argument("--window-size=1920x1080")

        # comment out the following line if you don't want to actually show Chrome instance
        # but you can still see that the crawling is working via output in console

        # chrome_options.add_argument("--headless")

        # comment out the following two lines to setup ProxyMesh service
        # make sure you add the IP of the machine running this script to you ProxyMesh account for IP authentication
        # IP:PORT or HOST:PORT you get this in your account once you pay for a plan

        # PROXY = "us-wa.proxymesh.com:31280"
        # chrome_options.add_argument('--proxy-server=%s' % PROXY)

        chrome_driver_path = os.path.join(basedir, 'chromedriver')
        driver = webdriver.Chrome(chrome_options=chrome_options, executable_path=chrome_driver_path)
        driver.get(response.url)
        time.sleep(2)
        text = driver.page_source
        soup = BeautifulSoup(text, "html.parser")
        result_jsons = soup.find_all('script', attrs={'data-for': 's-result-json'})
        result = []
        for rj in result_jsons:
            data = json.loads(rj.text)
            if data.__contains__("data"):
                d = data['data']
                if d.__contains__('title'):
                    a = d['title']
                if d.__contains__('display_type_self') and (d['display_type_self'] == 'self_article' or d['display_type_self'] == 'self_step_or_list'):
                    item = {'title': d['title'], 'source_url': d['source_url'], 'comment_count': d['comment_count']}
                    result.append(item)
        item = random.choice(result)
        driver.get(item['source_url'])
        time.sleep(2)
        text = driver.page_source
        soup = BeautifulSoup(text, "html.parser")
        contents = soup.find_all('article')[0]
        driver.quit()
