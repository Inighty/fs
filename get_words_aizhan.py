import random
import string
from time import sleep

import requests
from bs4 import BeautifulSoup

from zzspider.tools.dbhelper import DBHelper

result = []
proxy = '127.0.0.1:10811'
proxies = {
    'http': proxy,
    'https': proxy,
}
payload = {}
headers = {
    'Host': 'baidurank.aizhan.com',
    'Connection': 'keep-alive',
    'Pragma': 'no-cache',
    'Cache-Control': 'no-cache',
    'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="99", "Google Chrome";v="99"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'DNT': '1',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-User': '?1',
    'Sec-Fetch-Dest': 'document',
    'Accept-Language': 'zh,zh-CN;q=0.9,en;q=0.8,zh-TW;q=0.7,en-US;q=0.6,ja;q=0.5',
    'Cookie': 'allWords=%E5%85%83%E5%AE%B5%E8%8A%82%7C%E6%94%BF%E5%8A%A1%E7%B3%BB%E7%BB%9F%7C%E7%94%9F%E6%B4%BB%7C%E7%94%9F%E6%B4%BB%E7%99%BE%E7%A7%91%7C%E7%94%9F%E6%B4%BB%E5%B0%8F%E7%AA%8D%E9%97%A8%7C%E7%94%9F%E6%B4%BB%E5%B0%8F%E5%B8%B8%E8%AF%86%7C%E5%81%A5%E5%BA%B7%E5%B0%8F%E7%9F%A5%E8%AF%86%7C%E7%94%9F%E6%B4%BB%E5%A6%99%E6%8B%9B%7C%E7%94%9F%E6%B4%BB%E5%B0%8F%E5%A6%99%E6%8B%9B%7C%E9%A3%8E%E6%B0%B4; Hm_lvt_b37205f3f69d03924c5447d020c09192=1646031579,1646095081,1646183590,1646354636; _csrf=0d110352f636df272e347976629545697ca2d005e3913b0041d014e0d9ef2cbca%3A2%3A%7Bi%3A0%3Bs%3A5%3A%22_csrf%22%3Bi%3A1%3Bs%3A32%3A%22Htig-DXaTpIqqigBf3ih7O7WsxR1qC6l%22%3B%7D; update=0; allSites=400zi.com%7Cwap.readfar.com%7Cwww.baikexueshe.com%7Cwww.xbgqw.com%7Cwww.52biqv.com%7Cwww.biquw.com%7Cwww.kuaishoumulu.com%7Cwww.macwk.com%7Cwww.mclose.com%7Cwww.hutu3.com'
}


def process(type, domain, path, page):
    process_i(type, domain, path, page, 1)


def process_i(type, domain, path, page, i):
    global result
    url = f"https://baidurank.aizhan.com/{type}/{domain}/{path}/0/{page}/position/{i}/"
    response = requests.request("GET", url, headers=headers, data=payload)
    soup = BeautifulSoup(response.text, 'html.parser')
    item = soup.find_all("td", attrs={"class": "title"})
    for i in item:
        a = i.find('a')
        if a:
            title = a['title']
            result.append(title)


mode = 'sql'
cate = 3
type = 'mobile'
domain = '400zi.com'
name = domain.replace('.', '_')
file_name = f'result_aizhan_{name}_{type}.txt'
file_name = 'temp.txt'
paths = ["-1", "books", "vps20210412", "vps2021-04-13", "vps2021-04-12", "vps20210413", "vps20210416", "books41",
         "books_64476", "books29", "books14", "books_92510", "books00", "books_74727", "books_45894", "books89",
         "books99", "books_72176", "books_94436", "books_10779", "books_40260", "books_71016", "books_13341",
         "books_49374", "books_98516", "books07", "tag", "books_88887", "books_69227"]
# for path in paths:
#     for k in range(1, 51):
#         process(type, domain, path, k)
#         sleep(1)
with open('D:/desktop/cate3.txt', encoding="utf-8") as f:
    result = f.readlines()
real_arr = []
real_items = []
for item in result:
    real_item = item.strip().replace('\'', '\\\'')
    real_items.append(real_item)
real_items = list(set(real_items))
if mode == 'sql':
    db = DBHelper(host="114.132.198.103", user="baikexueshe", pwd="mc0321..", db="baikexueshe")
    for item in real_items:
        count = db.fetch_one("select count(1) as num from zbp_words where word = %s", [item])
        if count['num'] == 0:
            real_arr.append(item)
    sql_arr = []
    for item in real_arr:
        sql_arr.append(
            f"INSERT INTO `zbp_words`(`word`, `cate`) VALUES ('{item}','{cate}');")
        # new_path = ''.join(random.SystemRandom().choice(string.ascii_lowercase + string.digits) for _ in range(6))
        # sql_arr.append(
        #     f"INSERT INTO `jieqi_artile_seword`(`kw`, 'path') VALUES ('{item}', '{new_path}') on duplicate key update kw = kw;")
    with open(file_name, mode='w') as f:
        f.write("\n".join(sql_arr))
else:
    with open(file_name, mode='w') as f:
        f.write("\n".join(real_items))
