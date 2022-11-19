# ！/usr/bin/env python
# -*- coding: UTF-8 -*-
import json
import logging
import urllib.parse
import urllib.request

import requests

from zzspider import settings

logger = logging.getLogger(__name__)


def get_expiretime():
    res_data = urllib.request.urlopen(settings.PROXY_EXPIRE_URL)
    result = res_data.read().decode('utf-8')
    return json.loads(result)['expiretime']


def get_proxies():
    res_data = urllib.request.urlopen(settings.PROXY_URL)
    return res_data.read().decode('utf-8')
    # while True:
    #     res_data = urllib.request.urlopen(settings.PROXY_URL)
    #     proxy = res_data.read().decode('utf-8')
    #     if check_proxy(proxy):
    #         return proxy


def get_proxies_pure():
    return get_proxies().replace('http://', '')


def check_proxy(proxy):
    proxies = {  # 分别对着一个代理ip，进行http尝试和https尝试
        'http': proxy,
        'https': proxy,
    }
    test_url = 'https://httpbin.org/get'

    try:
        response = requests.get(test_url, proxies=proxies, timeout=3)
        if response.ok:
            return True
        return False
    except Exception as ex:
        return False
