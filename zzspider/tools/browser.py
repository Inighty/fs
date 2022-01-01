# ！/usr/bin/env python
# -*- coding: UTF-8 -*-
import logging
import os
import time

import pymysql
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from zzspider import settings
from zzspider.tools.singleton_type import Singleton

logger = logging.getLogger(__name__)

basedir = os.path.dirname(os.path.realpath('__file__'))


class Browser(metaclass=Singleton):
    # 构造函数
    def __init__(self):
        # instantiate a chrome options object so you can set the size and headless preference
        self.chrome_options = Options()
        self.chrome_options.add_argument("--window-size=1920x1080")
        self.driver = None
        # comment out the following line if you don't want to actually show Chrome instance
        # but you can still see that the crawling is working via output in console

        self.chrome_options.add_argument("--headless")
        self.chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])

        self.chrome_options.add_argument('--start-maximized')
        self.chrome_options.add_argument('--no-sandbox')
        self.chrome_options.add_argument("disable-blink-features=AutomationControlled")

        self.chrome_options.add_argument(f'user-agent={settings.USER_AGENT}')
        # comment out the following two lines to setup ProxyMesh service
        # make sure you add the IP of the machine running this script to you ProxyMesh account for IP authentication
        # IP:PORT or HOST:PORT you get this in your account once you pay for a plan

        # PROXY = "us-wa.proxymesh.com:31280"
        # chrome_options.add_argument('--proxy-server=%s' % PROXY)

    def start_driver(self):
        if self.driver is not None:
            return self.driver
        chrome_driver_path = os.path.join(basedir, 'chromedriver')
        self.driver = webdriver.Chrome(chrome_options=self.chrome_options)
        return self.driver

    # 关闭标签
    def close(self):
        if self.driver is not None:
            self.driver.close()

    # 关闭
    def quit(self):
        if self.driver is not None:
            self.driver.quit()

    # 执行数据库的sq语句,主要用来做插入操作
    def get(self, url, sleep=2):
        driver = self.start_driver()
        driver.get(url)
        time.sleep(sleep)
        return driver.page_source
