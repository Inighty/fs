import json
import os
import random

import requests
from PIL import Image as pilImage
from wand.image import Image
from reportlab.graphics import renderPM
from svglib.svglib import svg2rlg


def img_to_progressive(path):
    if os.path.isdir(path):
        return path
    ext = path.split('.')[-1:][0]
    if ext == 'svg':
        pic = svg2rlg(path)
        path = path.replace('.svg', '.png')
        renderPM.drawToFile(pic, path)
        return path
    ext = path.split('.')[-1:][0]
    if ext == 'gif':
        compress_gif(path)
        return path
    if ext not in ['png', 'jpg', 'jpeg']:
        return path
    shrink_image(path)
    return path


def compress_gif(filename):
    with Image(filename=filename) as img:
        img.optimize_layers()
        destination = os.path.splitext(filename)[0] + '_destination' + os.path.splitext(filename)[1]
        img.save(filename=destination)
    os.remove(filename)
    os.rename(destination, filename)


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


def local_compress_image(path):
    destination = os.path.splitext(path)[0] + '_destination' + os.path.splitext(path)[1]
    img_size = int(os.path.getsize(path))
    if os.path.isfile(path) and os.path.splitext(path)[1] == '.png':
        cmd = 'pngquant --force --skip-if-larger --output {} --quality 50-80 --verbose {}'.format(destination, path)
        rt = os.system(cmd)
        if rt == 0:
            print(path.split('/')[-1:][0], '转换完毕')
            new_img_size = int(os.path.getsize(destination))
            if new_img_size >= img_size:
                os.remove(destination)
                print('图片变大了，不做处理：' + str(img_size) + '--->' + str(new_img_size))
            else:
                print('开始重命名文件')
                os.remove(path)
                os.rename(destination, path)
                print('图片大小：' + str(img_size) + '--->' + str(new_img_size))
                return

    if img_size < 500000:
        return
    img = pilImage.open(path)

    if img.mode == "CMYK":
        img = img.convert('RGB')
    new_width = 600
    if img.size[0] > new_width:
        new_height = int(new_width * img.size[1] * 1.0 / img.size[0])
        img = img.resize((new_width, new_height))
    print(path.split('/')[-1:][0], '开始转换图片')
    img.save(destination, "PNG", quality=60, optimize=True, progressive=True)
    print(path.split('/')[-1:][0], '转换完毕')
    new_img_size = int(os.path.getsize(destination))
    if new_img_size >= img_size:
        os.remove(destination)
        print('图片变大了，不做处理：' + str(img_size) + '--->' + str(new_img_size))
    else:
        print('开始重命名文件')
        os.remove(path)
        os.rename(destination, path)
        print('图片大小：' + str(img_size) + '--->' + str(new_img_size))
        return


def shrink_image(file_path):
    print(file_path)
    try:
        result = shrink(file_path)
        if result:
            output_path = os.path.splitext(file_path)[0] + '_destination' + os.path.splitext(file_path)[1]
            url = result['output']['url']
            response = requests.get(url)
            with open(output_path, 'wb') as file:
                file.write(response.content)
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
    except:
        local_compress_image(file_path)


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


if __name__ == '__main__':
    compress_gif("E:/桌面/202202231645593812053.gif")
