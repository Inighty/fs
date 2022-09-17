import json
import os
import random

import requests
from pygifsicle import optimize


def img_to_progressive(path):
    if os.path.isdir(path):
        return
    ext = path.split('.')[-1:][0]
    if ext == 'gif':
        compress_gif(path)
        return
    if ext not in ['png', 'jpg', 'jpeg']:
        return
    shrink_image(path)


def compress_gif(filename):
    optimize(filename, options=['--lossy=90', '--no-extensions', '--no-comments'])


def list_images(path):
    images = None
    try:
        if path:
            os.chdir(path)
        full_path = os.getcwd()
        files = os.listdir(full_path)
        images = []
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext in ('.jpg', '.jpeg', '.png'):
                images.append(os.path.join(full_path, file))
    except:
        pass
    return images


def shrink_image(file_path):
    print(file_path)
    result = shrink(file_path)
    if result:
        output_path = os.path.splitext(file_path)[0] + '_destination' + os.path.splitext(file_path)[1]
        url = result['output']['url']
        response = requests.get(url)
        with open(output_path, 'wb') as file:
            file.write(response.content)
        print(output_path)
        os.remove(file_path)
        os.rename(output_path, file_path)
        print('%s %d=>%d(%f)' % (
            result['input']['type'],
            result['input']['size'],
            result['output']['size'],
            result['output']['ratio']
        ))
    else:
        print('压缩失败')


def shrink(file_path):
    url = 'https://tinypng.com/web/shrink'
    headers = {
        'Cache-Control': 'no-cache',
        'Content-Type': 'application/x-www-form-urlencoded',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36',
        'X-Forwarded-For': get_random_ip()
    }
    result = None
    try:
        file = open(file_path, 'rb')
        response = requests.post(url, headers=headers, data=file)
        result = json.loads(response.text)
    except:
        if file:
            file.close()
    if result and result['input'] and result['output']:
        return result
    else:
        return None


def get_random_ip():
    ip = []
    for i in range(4):
        ip.append(str(random.randint(0 if i in (2, 3) else 1, 254)))
    return '.'.join(ip)
