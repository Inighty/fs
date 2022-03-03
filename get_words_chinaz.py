import time

import requests
from bs4 import BeautifulSoup

from zzspider.tools.dbhelper import DBHelper

result = []

payload = {}
headers = {
  'Connection': 'keep-alive',
  'Cache-Control': 'max-age=0',
  'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="98", "Google Chrome";v="98"',
  'sec-ch-ua-mobile': '?0',
  'sec-ch-ua-platform': '"Windows"',
  'DNT': '1',
  'Upgrade-Insecure-Requests': '1',
  'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36',
  'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
  'Sec-Fetch-Site': 'none',
  'Sec-Fetch-Mode': 'navigate',
  'Sec-Fetch-User': '?1',
  'Sec-Fetch-Dest': 'document',
  'Accept-Language': 'zh,zh-CN;q=0.9,en;q=0.8,zh-TW;q=0.7,en-US;q=0.6,ja;q=0.5',
  'Cookie': 'UM_distinctid=17dc286633eaa2-00cf065a3ae77e-4303066-1fa400-17dc286633fc68; ucvalidate=581b9c40-4592-4ca1-ac15-1445073c3d91; user-temp=890d4c0a-7c71-88f2-8ab5-4fe00d99aa9f; bbsmax_user=890d4c0a-7c71-88f2-8ab5-4fe00d99aa9f; auth-token=061c2497-c79a-4881-b542-7eeb3252c9f1; Hm_lvt_ca96c3507ee04e182fb6d097cb2a1a4c=1645059251,1646031485,1646101444,1646188900; qHistory=aHR0cDovL3JhbmsuY2hpbmF6LmNvbV/nmb7luqZQQ+adg+mHjeafpeivonxodHRwOi8vcmFuay5jaGluYXouY29tL2JhaWR1cGNwYXkvX+e7vOWQiOadg+mHjeafpeivonxodHRwOi8vcmFuay5jaGluYXouY29tX+e7vOWQiOadg+mHjeafpeivonxodHRwOi8vc2VvLmNoaW5hei5jb21fU0VP57u85ZCI5p+l6K+i; toolbox_urls=400zi.com|www.sdxtsg.com|learntothink.cn|www.infinitystatue.com|www.baikexueshe.com|www.52biqv.com|www.bm86.com|www.oofof.com|www.fogolu.com|www.dm79.com; CNZZDATA5082706=cnzz_eid%3D867777018-1638769984-https%253A%252F%252Fseo.chinaz.com%252F%26ntime%3D1646291859'
}


def process(type, domain, path, page):
    process_i(type, domain, path, page, 1)


def process_i(type, domain, path, page, i):
    global result
    url = f"https://rank.chinaz.com{type}/{domain}-0---0-{page}"
    response = requests.request("GET", url, headers=headers, data=payload)
    soup = BeautifulSoup(response.text, 'html.parser')
    item = soup.find_all("a", attrs={"class": "ellipsis"})
    for i in item:
        title = i.text
        result.append(title)
    time.sleep(10)


mode = 'sql1'
cate = 1
type = '/baidumobile'
domain = '400zi.com'
name = domain.replace('.', '_')
file_name = f'result_chinaz_{name}_{type.strip("/")}.txt'
paths = ['-1']
for path in paths:
    for k in range(1, 51):
        process(type, domain, path, k)
# with open(file_name) as f:
#     result = f.readlines()
real_arr = []
result = list(set(result))
real_items = []
for item in result:
    real_item = item.strip().replace('\'', '\\\'')
    real_items.append(real_item)

if mode == 'sql':
    db = DBHelper(host="114.132.198.103", user="baikexueshe", pwd="mc0321..", db="baikexueshe")
    for item in real_items:
        count = db.fetch_one("select count(1) as num from zbp_words where word = %s", [item])
        if count['num'] == 0:
            real_arr.append(f"('{item}',{cate})")

    sql = "INSERT INTO `zbp_words`(`word`, `cate`) VALUES {0}".format(",".join(real_arr)) + ";"

    with open(file_name, mode='w') as f:
        f.write(sql)
else:
    with open(file_name, mode='w') as f:
        f.write("\n".join(real_items))
