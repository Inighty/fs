# ！/usr/bin/env python
# -*- coding: UTF-8 -*-
import datetime
import json
import logging
import urllib.parse
import urllib.request

import requests

from zzspider import settings
from zzspider.tools.send_msg import sendMsg

logger = logging.getLogger(__name__)
expire_time = None
present_key = None


def replace_key():
    global expire_time, present_key
    if expire_time is None:
        key = requests.get("https://gitee.com/inighty/public/raw/master/key").text
        result = requests.get(settings.PROXY_EXPIRE_URL.replace('{id}', key)).text
        json_object = json.loads(result)
        if json_object['success']:
            expire_time = json_object['expiretime']
            present_key = key
            return settings.PROXY_URL.replace('{id}', present_key)
        else:
            logger.error("proxy key expire")
            exit(0)
    else:
        ex_date = datetime.datetime.strptime(expire_time, "%Y-%m-%d  %H:%M:%S+0800")
        if ex_date.date() == datetime.date.today():
            # 到达过期当天  发送消息
            sendMsg("proxy expired.", "proxy expired.", "proxy")
        if expire_time < datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%d %H:%M:%S"):
            # 过期了
            key = requests.get("https://gitee.com/inighty/public/raw/master/key").text
            if key != present_key:
                present_key = key
                result = requests.get(settings.PROXY_EXPIRE_URL.replace('{id}', key)).text
                json_object = json.loads(result)
                expire_time = json_object['expiretime']
            else:
                logger.error("proxy key expire")
                exit(0)
        else:
            # 没过期
            return settings.PROXY_URL.replace('{id}', present_key)


def get_expiretime():
    res_data = urllib.request.urlopen(settings.PROXY_EXPIRE_URL)
    result = res_data.read().decode('utf-8')
    return json.loads(result)['expiretime']


def get_proxies():
    res_data = urllib.request.urlopen(replace_key())
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
