import hashlib
import json
import logging
import os
import re
import time
import urllib.parse
import urllib.request
import urllib.request
from hashlib import md5
from mimetypes import guess_extension

import requests

logger = logging.getLogger(__name__)


def get_audio(id):
    url = f"https://www.ximalaya.com/revision/play/v1/audio?id={id}&ptype=1"
    payload = {}
    headers = {
        'authority': 'www.ximalaya.com',
        'dnt': '1',
        'sec-ch-ua-mobile': '?0',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36',
        'sec-ch-ua-platform': '"Windows"',
        'accept': '*/*',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'accept-language': 'zh,zh-CN;q=0.9,en;q=0.8,zh-TW;q=0.7,en-US;q=0.6,ja;q=0.5'
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    res = json.loads(response.text.encode('utf8'))
    src = res['data']['src']
    result = urllib.request.urlretrieve(src)
    if result and len(result) > 0:
        temp_path = result[0]
        content_type = result[1].get_content_type().partition(';')[0].strip()
        if content_type.__contains__("m4a"):
            suffix = ".m4a"
        else:
            suffix = guess_extension(content_type)
        result = temp_path + suffix
        os.rename(temp_path, result)
        return result
    else:
        logger.error("下载异常:" + src)
        exit(0)


def pre_upload():
    data = {
        "tasktype": "voice2text",
        "limitsize": 20480,
        "filename": "audio.mp3",
        "filecount": 1,
        "isshare": 1,
        "timestamp": int(round(time.time())),
        "softname": "pdfonlineconverter",
        "softversion": "V4.2.9.1",
        "machineid": mid,
        "productid": 146,
        "validpagescount": 20,
        "filesrotate": 0,
        "filesequence": 0,
        "fanyi_from": "zh-CHS"
    }

    data_sign = []
    for k in sorted(data):
        data_sign.append(k + "=" + str(data[k]))
    data_sign = "&".join(data_sign) + "hUuPd20171206LuOnD"
    data['datasign'] = hashlib.md5(data_sign.encode("utf-8")).hexdigest()

    req = urllib.request.Request(url="https://app.xunjiepdf.com/api/v4/uploadpar",
                                 data=urllib.parse.urlencode(data).encode('utf-8'))
    resp = urllib.request.urlopen(req)
    body_str = resp.read().decode("utf-8")
    meta = json.loads(body_str)
    return meta


def upload_chunk(tasktag, timestamp, tasktoken, chunks, chunk, size, data):
    headers = {
        "Content-Length": size,
        "Cookie": "xunjieUserTag=98F0CBB05248B0FB6ED5B487D49F4752; site_redirect_loginuri=https%3A//app.xunjiepdf.com/voice2text/; _ga=GA1.2.1632791774.1624503980; _gid=GA1.2.2015745962.1624503980; OUTFOX_SEARCH_USER_ID_NCOO=1563871560.1974661; appdownhide=1; Hm_lvt_6c985cbff8f72b9fad12191c6d53668d=1624503980,1624505334; xunjieTempFileList=0bd2b06ce2bb4b0b937e51ef1850d09c%7c87fbc4af9f7141da8a70001f675ffd0c%7cf87142a187244fb89428e56b81d1e573%7c7e96eef5ccb3448cbf2d85044b2f1e13%7c0ce8ca7c41de474ea9ac387e99c653f5; Hm_lpvt_6c985cbff8f72b9fad12191c6d53668d=1624517381; _gat_gtag_UA_117273948_9=1"
    }
    req = urllib.request.Request(
        url=f"https://app.xunjiepdf.com/api/v4/uploadfile?tasktag={tasktag}&timestamp={timestamp}&tasktoken={tasktoken}&fileindex=0&chunks={chunks}&chunk={chunk}&id=WU_FILE_0&name=audio.mp3&type=audio^%^2Fmpeg&lastModifiedDate=Thu+Jun+24+2021+11^%^3A08^%^3A48+GMT^%^2B0800+(^%^E4^%^B8^%^AD^%^E5^%^9B^%^BD^%^E6^%^A0^%^87^%^E5^%^87^%^86^%^E6^%^97^%^B6^%^E9^%^97^%^B4)&size={size}",
        headers=headers,
        data=data)
    resp = urllib.request.urlopen(req)
    body_str = resp.read().decode("utf-8")
    upload_result = json.loads(body_str)
    return upload_result


def task_down(tasktag):
    headers = {
        "Content-Type": "application/json; charset=UTF-8"
    }
    data = {"productinfo": "1245A2A101F776005F2E909C29CC8F7369FAA0BED21AE0A9F9ADBD8D49EE3783",
            "deviceid": mid, "timestamp": int(round(time.time())), "tasktag": tasktag,
            "downtype": 2,
            "brandname": "-迅捷PDF转换器"}

    data_sign = []
    for k in sorted(data):
        data_sign.append(k + "=" + str(data[k]))
    data_sign = "&".join(data_sign) + "hUuPd20171206LuOnD"
    data['datasign'] = hashlib.md5(data_sign.encode("utf-8")).hexdigest()
    url = "https://app.xunjiepdf.com/api/v4/taskdown"

    response = requests.request("POST", url, headers=headers, data=json.dumps(data))
    body_str = response.text.encode("utf-8")
    down_result = json.loads(body_str)
    return down_result


def split_data(filepath):
    fp = open(filepath, "rb")
    data = fp.read()
    fp.close()
    length = 3 * 1024 * 1024
    chunks = [data[i:i + length] for i in range(0, len(data), length)]
    return chunks


def audio2text(filepath):
    meta = pre_upload()

    if meta["code"] != 10000:
        print(meta)
        return

    chunks = split_data(filepath)
    for i in range(0, len(chunks)):
        upload_chunk(meta["tasktag"], meta["timestamp"], meta["tasktoken"], len(chunks), i,
                     len(chunks[i]), chunks[i])

    time.sleep(30)

    down_result = task_down(meta["tasktag"])
    result = urllib.request.urlretrieve(down_result['downurl'])
    path = result[0]
    with open(path, mode='r', encoding='utf-8') as f:
        result_text = f.read()
    os.remove(path)
    return result_text


if __name__ == '__main__':
    # gs
    mid = "D9C58624123B3EC73EAE5C8EAB09E6AC"
    # mid = "245E055883F34DB63C6FE3B039C130B5"
    id = 500311128
    audio = get_audio(id)
    if audio is None:
        exit(0)
    text = audio2text(audio)


    def clean_txt(data):
        data = re.sub("(哎|呢|哈|啊|啊、|呐|呀|那么|呃|嘛|诶)", "", data)
        return data


    text = clean_txt(text)
    print(text)
