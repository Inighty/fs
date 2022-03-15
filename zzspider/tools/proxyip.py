# ！/usr/bin/env python
# -*- coding: UTF-8 -*-
import logging
import traceback

import requests

from zzspider.config import ConfigUtil
from zzspider.tools.singleton_type import Singleton

logger = logging.getLogger(__name__)

proxy_url = ConfigUtil.config['proxy']['url']


class ProxyIp(metaclass=Singleton):
    # 构造函数
    def __init__(self):
        self.ip = None
        self.last_time = None

    def get(self):
        if not self.check():
            return self.get_new()
        return self.ip

    def get_proxy(self):
        return {
            "http": "http://" + self.get()
        }

    def get_new(self):
        res = requests.get(proxy_url)
        self.ip = res.text
        return self.ip

    def check(self):
        logger.error("start check!")
        if self.ip is None:
            return False
        proxies = {
            "http": "http://" + self.ip
        }
        r = None
        try:
            r = requests.get("http://www.baidu.com/", proxies=proxies, timeout=10)
            logger.error("status return :" + str(r.status_code))
            if r.status_code == 407:
                return False
        except Exception as e:
            logger.error("check ip error:" + traceback.format_exc())
            pass
        if r:
            return True
        else:
            return False
