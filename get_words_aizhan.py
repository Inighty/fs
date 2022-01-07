import requests
from bs4 import BeautifulSoup

result = []

payload = {}
headers = {
    'Connection': 'keep-alive',
    'Pragma': 'no-cache',
    'Cache-Control': 'no-cache',
    'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'DNT': '1',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-User': '?1',
    'Sec-Fetch-Dest': 'document',
    'Accept-Language': 'zh,zh-CN;q=0.9,en;q=0.8,zh-TW;q=0.7,en-US;q=0.6,ja;q=0.5',
    'Cookie': 'allWords=%E9%A3%8E%E6%B0%B4%7C%E4%B9%90%E5%8F%AF%7C%E4%BF%AE%E5%A3%AB%E8%AE%B0%2C0; userId=1385811; userName=WX61124c07de6cc%40aizhan.com; userGroup=1; userSecure=PlQav6CcGTzbeYqU5LRDXMw6oS6qRz11IPJtnPB7UdyPxEjsXEFMJR0fOZbbJ8ToyVvrYHyLsp8wlHd1xz0kcbyNDsMz%2Bb%2Bf; userWxNickname=%E7%8E%A9%E6%B8%B8%E6%88%8F%E5%8F%96%E6%B6%88%E9%9D%99%E9%9F%B3; Hm_lvt_b37205f3f69d03924c5447d020c09192=1640912708,1641257769,1641345282,1641430700; _csrf=e997054bdfa808216d522a704a288ed62594777fbdabff8a982c225907afdc45a%3A2%3A%7Bi%3A0%3Bs%3A5%3A%22_csrf%22%3Bi%3A1%3Bs%3A32%3A%22f3NIpMlYuvlAfjNHcWIyUPcoUqJOVt-0%22%3B%7D; allSites=d1xz.net%7Cdyxzw.net%7Cdyxz.net%7Cwww.5wl.cn%7Cwww.52biqv.com%7Chtchao.cn%7Cwww.tianqijun.com%7Cwww.ssffx.com%7Cyixuexianzhi.com%7Cyixueshengshou.com'
}


def process(page):
    process_i(page, 1)
    process_i(page, 2)


def process_i(page, i):
    global result
    url = f"https://baidurank.aizhan.com/mobile/d1xz.net/fsml/0/{page}/position/{i}/"
    response = requests.request("GET", url, headers=headers, data=payload)
    soup = BeautifulSoup(response.text, 'html.parser')
    item = soup.find_all("td", attrs={"class": "title"})
    for i in item:
        a = i.find('a')
        if a:
            title = a['title']
            result.append(title)


for k in range(0, 51):
    process(k)

with open('result_aizhan_d1xz.txt', mode='w') as f:
    lines = [f"{item}\n" for item in result]
    f.writelines(lines)
