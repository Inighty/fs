# ！/usr/bin/env python
# -*- coding: UTF-8 -*-
import logging
import traceback

import requests

from zzspider.config import ConfigUtil
from zzspider.tools.singleton_type import Singleton

logger = logging.getLogger(__name__)


class ProxyIp(metaclass=Singleton):
    # 构造函数
    def __init__(self):
        self.ip = None
        self.last_time = None

    def get(self, host="https://www.baidu.com/"):
        if not self.check(host):
            return self.get_new()
        return self.ip

    def get_proxy(self):
        return {
            "http": "socks5://" + self.get()
        }

    def get_new(self):
        res = requests.get(ConfigUtil.config['proxy']['url'])
        self.ip = res.text
        return self.ip

    def check(self, host):
        if self.ip is None:
            return False
        logger.error("ip:" + self.ip)
        proxies = {
            "http": "socks5://" + self.ip,
            "https": "socks5://" + self.ip
        }
        r = None
        try:
            r = requests.get(host, proxies=proxies, timeout=10)
            if r.status_code == 407:
                return False
        except Exception as e:
            logger.error("check ip error:" + self.ip + "," + traceback.format_exc())
            pass
        if r:
            return True
        else:
            return False
