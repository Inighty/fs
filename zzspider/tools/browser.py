# ！/usr/bin/env python
# -*- coding: UTF-8 -*-
import logging
import os
import random
import time

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from undetected_chromedriver import ChromeOptions

from zzspider.tools.singleton_type import Singleton

logger = logging.getLogger(__name__)

basedir = os.path.dirname(os.path.realpath('__file__'))


class Browser(metaclass=Singleton):

    # 构造函数
    def __init__(self):
        self.driver = None

    def start_driver(self):
        if self.driver is not None:
            return self.driver
        options = ChromeOptions()
        options.add_argument("--window-size=1920x1080")
        options.add_argument("--lang=zh")
        options.add_argument('--ignore-certificate-errors')
        options.ignore_local_proxy_environment_variables()
        self.driver = uc.Chrome(options=options, headless=True)
        return self.driver

    # 关闭标签
    def close(self):
        if self.driver is not None:
            self.driver.close()

    # 关闭
    def quit(self):
        if self.driver is not None:
            self.driver.quit()
            self.driver = None

    # 执行数据库的sq语句,主要用来做插入操作
    def get(self, url, sleep=10):
        driver = self.start_driver()
        driver.get(url)
        time.sleep(sleep)
        return driver.page_source

    def get_util_class(self, url, classname):
        driver = self.start_driver()
        # driver.implicitly_wait(10)
        driver.get(url)
        WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.CLASS_NAME, classname)))
        return driver.page_source

    def get_util_id(self, url, id):
        driver = self.start_driver()
        # driver.implicitly_wait(10)
        driver.get(url)
        WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.ID, id)))
        return driver.page_source
