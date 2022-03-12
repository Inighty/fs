# ！/usr/bin/env python
# -*- coding: UTF-8 -*-
import logging
import telnetlib

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
        if self.ip is None:
            return self.get_new()
        else:
            try:
                telnetlib.Telnet(self.ip.split(':')[0], self.ip.split(':')[1], timeout=2)
            except:
                return self.get_new()
        return self.ip

    def get_new(self):
        res = requests.get(proxy_url)
        self.ip = res.text
        return self.ip
