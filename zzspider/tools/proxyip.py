# ！/usr/bin/env python
# -*- coding: UTF-8 -*-
import logging
import telnetlib
import time

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
        if not self.check_time():
            return self.get_new()
        return self.ip

    def get_new(self):
        res = requests.get(proxy_url)
        self.ip = res.text
        return self.ip

    def check_time(self):
        now = time.time()
        if self.last_time is None:
            self.last_time = now
            return False
        else:
            difference = int(now - self.last_time)
            if difference >= 60:
                return False
        return True
