import json

import requests

url = f"https://didi.seowhy.com/www/quickSort/analyse?page=1&limit=100&url=https%3A%2F%2Fwww.52biqv.com&type=7"
payload = {}
headers = {
    'Connection': 'keep-alive',
    'Pragma': 'no-cache',
    'Cache-Control': 'no-cache',
    'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'DNT': '1',
    'X-Requested-With': 'XMLHttpRequest',
    'sec-ch-ua-mobile': '?0',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36',
    'sec-ch-ua-platform': '"Windows"',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Dest': 'empty',
    'Referer': 'https://didi.seowhy.com/www/quickSort/analyse',
    'Accept-Language': 'zh,zh-CN;q=0.9,en;q=0.8,zh-TW;q=0.7,en-US;q=0.6,ja;q=0.5',
    'Cookie': 'v5_quickSort_ad=1; v5_adVipStatus=1; token=6jydn10Mk1GRZNE%2BFeB0RV4KKQ4KrfUoJD6MlyRQ969n%2FyKLaH5Ir1I0%2BnvDlzbC; Hm_lvt_3e5875cdd6fd6a5ada5e50e88906a4a3=1640335766; PHPSESSID=j2556efhvur4ea259k1112ojvo; v5_quickSort_ad=1; v5_quickSearchHistory=%5B%22www.52biqv.com%22%5D; v5_66189569c6d8f25c8454b33293f7dc75=1; v5_3710099c77f3703fdd257bd8b6a784ef=1; v5_oauth_user=dhDHkg1kMK29Ow4ZFe1iUtpcs1JQib; PHPSESSID=9j37cmrdi3b59vb2qad0pqg3d8; v5_oauth_user=0mO7ki1rUXF4vPJcIB%2BjN8DEfGGTja; v5_quickSearchHistory=%5B%22www.52biqv.com%22%5D'
}

response = requests.request("GET", url, headers=headers, data=payload)
res = json.loads(response.text)
first = True
count = res['count']
page = count // 100
an = count % 100

if an > 0:
    all_page = page + 1
else:
    all_page = page

result = []
data = res['data']
result.extend(data)

for i in range(2, all_page + 1):
    url = f"https://didi.seowhy.com/www/quickSort/analyse?page={page}&limit=100&url=https%3A%2F%2Fwww.52biqv.com&type=7"
    response = requests.request("GET", url, headers=headers, data=payload)
    res = json.loads(response.text)
    data = res['data']
    result.extend(data)
